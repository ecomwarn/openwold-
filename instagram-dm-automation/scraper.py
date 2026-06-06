"""
Discovers candidate Instagram accounts by:
  1. Scraping recent posts under target hashtags
  2. Scraping followers of competitor accounts

Uses Playwright (headless Chromium) with a logged-in session.
All discovered accounts go through analyzer.py before being saved.
"""

import asyncio
import random
import json
import logging
from datetime import datetime
from playwright.async_api import async_playwright, Page, BrowserContext

import database
import analyzer
from config import (
    INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD,
    TARGET_HASHTAGS, TARGET_COMPETITOR_ACCOUNTS,
    SCRAPE_DELAY_SECONDS,
)

log = logging.getLogger(__name__)


async def _random_delay(page: Page, lo=None, hi=None):
    lo = lo or SCRAPE_DELAY_SECONDS[0]
    hi = hi or SCRAPE_DELAY_SECONDS[1]
    await asyncio.sleep(random.uniform(lo, hi))


async def login(page: Page):
    log.info("Logging in to Instagram...")
    await page.goto("https://www.instagram.com/accounts/login/", wait_until="networkidle")
    await _random_delay(page, 2, 4)

    await page.fill('input[name="username"]', INSTAGRAM_USERNAME)
    await page.fill('input[name="password"]', INSTAGRAM_PASSWORD)
    await page.click('button[type="submit"]')
    await page.wait_for_url("https://www.instagram.com/**", wait_until="networkidle", timeout=20_000)

    # Dismiss "Save login info" and notification prompts if they appear
    for selector in ['button:has-text("Not Now")', 'button:has-text("Not now")']:
        try:
            btn = page.locator(selector).first
            if await btn.is_visible(timeout=3_000):
                await btn.click()
                await _random_delay(page, 1, 2)
        except Exception:
            pass

    log.info("Login successful.")


async def _get_profile_data(page: Page, username: str) -> dict | None:
    """Navigate to a profile and scrape its metadata."""
    url = f"https://www.instagram.com/{username}/"
    try:
        await page.goto(url, wait_until="networkidle", timeout=15_000)
    except Exception as e:
        log.warning(f"Timeout loading profile {username}: {e}")
        return None

    await _random_delay(page)

    # Extract structured data from the page's JSON-LD or meta tags
    try:
        # Instagram embeds user data in a script tag
        data_script = await page.evaluate("""() => {
            const scripts = Array.from(document.querySelectorAll('script[type="application/json"]'));
            for (const s of scripts) {
                try {
                    const d = JSON.parse(s.textContent);
                    // Look for user object
                    const str = JSON.stringify(d);
                    if (str.includes('edge_followed_by')) return str;
                } catch(e) {}
            }
            return null;
        }""")

        if data_script:
            blob = json.loads(data_script)
            # Walk the blob to find the user node
            user = _find_user_node(blob)
            if user:
                return _extract_from_user_node(username, user)
    except Exception as e:
        log.debug(f"JSON extraction failed for {username}: {e}")

    # Fallback: scrape visible text
    return await _scrape_profile_fallback(page, username)


def _find_user_node(obj, depth=0):
    if depth > 10 or not isinstance(obj, (dict, list)):
        return None
    if isinstance(obj, dict):
        if "edge_followed_by" in obj and "username" in obj:
            return obj
        for v in obj.values():
            result = _find_user_node(v, depth + 1)
            if result:
                return result
    elif isinstance(obj, list):
        for item in obj:
            result = _find_user_node(item, depth + 1)
            if result:
                return result
    return None


def _extract_from_user_node(username: str, user: dict) -> dict:
    followers  = user.get("edge_followed_by", {}).get("count", 0)
    following  = user.get("edge_follow", {}).get("count", 0)
    post_count = user.get("edge_owner_to_timeline_media", {}).get("count", 0)
    bio        = user.get("biography", "")
    website    = user.get("external_url", "")
    full_name  = user.get("full_name", "")

    # Recent post edges for engagement/frequency analysis
    edges = user.get("edge_owner_to_timeline_media", {}).get("edges", [])
    likes_list    = [e["node"].get("edge_liked_by", {}).get("count", 0) for e in edges[:12]]
    comments_list = [e["node"].get("edge_media_to_comment", {}).get("count", 0) for e in edges[:12]]
    timestamps    = [
        datetime.utcfromtimestamp(e["node"]["taken_at_timestamp"]).isoformat()
        for e in edges[:12]
        if "taken_at_timestamp" in e["node"]
    ]

    avg_likes    = sum(likes_list) / max(len(likes_list), 1)
    avg_comments = sum(comments_list) / max(len(comments_list), 1)

    return {
        "username":          username,
        "full_name":         full_name,
        "followers":         followers,
        "following":         following,
        "post_count":        post_count,
        "avg_likes":         avg_likes,
        "avg_comments":      avg_comments,
        "bio":               bio,
        "website":           website,
        "recent_post_dates": timestamps,
    }


async def _scrape_profile_fallback(page: Page, username: str) -> dict | None:
    """Minimal scrape from visible page text when JSON extraction fails."""
    try:
        meta_desc = await page.get_attribute('meta[name="description"]', "content") or ""
        # Format: "X Followers, Y Following, Z Posts"
        import re
        nums = re.findall(r"([\d,]+)\s+(Followers|Following|Posts)", meta_desc)
        stat_map = {label: int(n.replace(",", "")) for n, label in nums}

        bio_el = page.locator('header section div:last-child span').first
        bio = (await bio_el.inner_text(timeout=2_000)) if await bio_el.count() else ""

        link_el = page.locator('header section a[rel="me nofollow noopener noreferrer"]').first
        website = (await link_el.get_attribute("href", timeout=2_000)) if await link_el.count() else ""

        return {
            "username":          username,
            "full_name":         "",
            "followers":         stat_map.get("Followers", 0),
            "following":         stat_map.get("Following", 0),
            "post_count":        stat_map.get("Posts", 0),
            "avg_likes":         0,
            "avg_comments":      0,
            "bio":               bio,
            "website":           website,
            "recent_post_dates": [],
        }
    except Exception as e:
        log.warning(f"Fallback scrape failed for {username}: {e}")
        return None


async def _scrape_hashtag(page: Page, hashtag: str, max_accounts: int = 50):
    """Collect usernames from the recent posts of a hashtag."""
    log.info(f"Scraping hashtag: #{hashtag}")
    await page.goto(f"https://www.instagram.com/explore/tags/{hashtag}/", wait_until="networkidle")
    await _random_delay(page, 3, 6)

    usernames = set()
    # Click the first post to open it, then iterate via next arrow
    try:
        first_post = page.locator('article a[href*="/p/"]').first
        await first_post.click()
        await _random_delay(page, 2, 4)
    except Exception:
        log.warning(f"Could not open first post for #{hashtag}")
        return usernames

    for _ in range(max_accounts):
        try:
            # Extract username from the open post dialog
            username_el = page.locator('article header a[href^="/"]').first
            href = await username_el.get_attribute("href", timeout=3_000)
            if href:
                uname = href.strip("/")
                if uname and uname not in ("explore",):
                    usernames.add(uname)

            # Go to next post
            next_btn = page.locator('button[aria-label="Next"]').first
            if not await next_btn.is_visible(timeout=2_000):
                break
            await next_btn.click()
            await _random_delay(page)
        except Exception as e:
            log.debug(f"Post iteration error: {e}")
            break

    # Close dialog
    try:
        await page.keyboard.press("Escape")
    except Exception:
        pass

    log.info(f"Found {len(usernames)} usernames from #{hashtag}")
    return usernames


async def _scrape_followers(page: Page, account: str, max_accounts: int = 100):
    """Scrape usernames from an account's followers list."""
    log.info(f"Scraping followers of @{account}")
    await page.goto(f"https://www.instagram.com/{account}/followers/", wait_until="networkidle")
    await _random_delay(page, 3, 5)

    usernames = set()
    try:
        dialog = page.locator('div[role="dialog"]')
        for _ in range(max_accounts // 5):
            links = dialog.locator('a[href^="/"]')
            count = await links.count()
            for i in range(count):
                href = await links.nth(i).get_attribute("href")
                if href:
                    uname = href.strip("/")
                    if uname and "." not in uname:
                        usernames.add(uname)
            await dialog.evaluate("el => el.scrollBy(0, 600)")
            await _random_delay(page, 1, 2)
            if len(usernames) >= max_accounts:
                break
    except Exception as e:
        log.warning(f"Followers scrape error for @{account}: {e}")

    log.info(f"Found {len(usernames)} usernames from @{account} followers")
    return usernames


async def discover_and_score(max_per_source: int = 60):
    """Main discovery loop: scrape → score → save to DB."""
    database.init_db()

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True, args=["--no-sandbox"])
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
        )
        page = await context.new_page()

        await login(page)

        all_usernames: set[str] = set()

        # Collect from hashtags
        for tag in TARGET_HASHTAGS:
            try:
                found = await _scrape_hashtag(page, tag, max_accounts=max_per_source)
                all_usernames.update(found)
            except Exception as e:
                log.error(f"Error scraping #{tag}: {e}")
            await _random_delay(page, 5, 10)

        # Collect from competitor followers
        for account in TARGET_COMPETITOR_ACCOUNTS:
            try:
                found = await _scrape_followers(page, account, max_accounts=max_per_source)
                all_usernames.update(found)
            except Exception as e:
                log.error(f"Error scraping followers of @{account}: {e}")
            await _random_delay(page, 5, 10)

        log.info(f"Total unique candidates: {len(all_usernames)}")

        # Profile-check each candidate
        processed = 0
        for username in all_usernames:
            if analyzer.should_skip_username(username):
                continue
            raw = await _get_profile_data(page, username)
            if raw is None:
                continue
            scored = analyzer.score_account(raw)
            database.upsert_account(scored)
            processed += 1
            log.info(
                f"[{processed}/{len(all_usernames)}] @{username} "
                f"score={scored['score']} status={scored['status']}"
            )
            await _random_delay(page, 4, 9)

        await browser.close()

    stats = database.get_stats()
    log.info(f"Discovery complete. DB stats: {stats}")
    return stats
