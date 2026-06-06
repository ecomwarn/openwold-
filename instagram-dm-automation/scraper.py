"""
Discovers candidate Instagram accounts via multiple methods:
  1. Hashtag posts
  2. Instagram search bar (keyword search for accounts)
  3. Competitor follower lists
  4. Suggested/related accounts on each competitor's profile
  5. Explore page topic browsing

Uses Playwright (headless Chromium) with a logged-in session.
All discovered accounts go through analyzer.py before being saved.
"""

import asyncio
import random
import json
import logging
from datetime import datetime
from playwright.async_api import async_playwright, Page

import database
import analyzer
from config import (
    INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD,
    TARGET_HASHTAGS, TARGET_SEARCH_TERMS,
    TARGET_COMPETITOR_ACCOUNTS, TARGET_EXPLORE_TOPICS,
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

    for selector in ['button:has-text("Not Now")', 'button:has-text("Not now")']:
        try:
            btn = page.locator(selector).first
            if await btn.is_visible(timeout=3_000):
                await btn.click()
                await _random_delay(page, 1, 2)
        except Exception:
            pass

    log.info("Login successful.")


# ── Profile data extraction ──────────────────────────────────────────────────

async def _get_profile_data(page: Page, username: str) -> dict | None:
    url = f"https://www.instagram.com/{username}/"
    try:
        await page.goto(url, wait_until="networkidle", timeout=15_000)
    except Exception as e:
        log.warning(f"Timeout loading profile {username}: {e}")
        return None

    await _random_delay(page)

    try:
        data_script = await page.evaluate("""() => {
            const scripts = Array.from(document.querySelectorAll('script[type="application/json"]'));
            for (const s of scripts) {
                try {
                    const d = JSON.parse(s.textContent);
                    const str = JSON.stringify(d);
                    if (str.includes('edge_followed_by')) return str;
                } catch(e) {}
            }
            return null;
        }""")

        if data_script:
            blob = json.loads(data_script)
            user = _find_user_node(blob)
            if user:
                return _extract_from_user_node(username, user)
    except Exception as e:
        log.debug(f"JSON extraction failed for {username}: {e}")

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

    edges         = user.get("edge_owner_to_timeline_media", {}).get("edges", [])
    likes_list    = [e["node"].get("edge_liked_by", {}).get("count", 0) for e in edges[:12]]
    comments_list = [e["node"].get("edge_media_to_comment", {}).get("count", 0) for e in edges[:12]]
    timestamps    = [
        datetime.utcfromtimestamp(e["node"]["taken_at_timestamp"]).isoformat()
        for e in edges[:12]
        if "taken_at_timestamp" in e["node"]
    ]

    return {
        "username":          username,
        "full_name":         full_name,
        "followers":         followers,
        "following":         following,
        "post_count":        post_count,
        "avg_likes":         sum(likes_list) / max(len(likes_list), 1),
        "avg_comments":      sum(comments_list) / max(len(comments_list), 1),
        "bio":               bio,
        "website":           website,
        "recent_post_dates": timestamps,
    }


async def _scrape_profile_fallback(page: Page, username: str) -> dict | None:
    try:
        meta_desc = await page.get_attribute('meta[name="description"]', "content") or ""
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


# ── Discovery method 1: Hashtags ─────────────────────────────────────────────

async def _scrape_hashtag(page: Page, hashtag: str, max_accounts: int = 50) -> set:
    log.info(f"[hashtag] #{hashtag}")
    await page.goto(f"https://www.instagram.com/explore/tags/{hashtag}/", wait_until="networkidle")
    await _random_delay(page, 3, 6)

    usernames = set()
    try:
        first_post = page.locator('article a[href*="/p/"]').first
        await first_post.click()
        await _random_delay(page, 2, 4)
    except Exception:
        log.warning(f"Could not open first post for #{hashtag}")
        return usernames

    for _ in range(max_accounts):
        try:
            username_el = page.locator('article header a[href^="/"]').first
            href = await username_el.get_attribute("href", timeout=3_000)
            if href:
                uname = href.strip("/")
                if uname and uname not in ("explore",):
                    usernames.add(uname)

            next_btn = page.locator('button[aria-label="Next"]').first
            if not await next_btn.is_visible(timeout=2_000):
                break
            await next_btn.click()
            await _random_delay(page)
        except Exception as e:
            log.debug(f"Post iteration error: {e}")
            break

    try:
        await page.keyboard.press("Escape")
    except Exception:
        pass

    log.info(f"  → {len(usernames)} usernames from #{hashtag}")
    return usernames


# ── Discovery method 2: Instagram search bar ─────────────────────────────────

async def _scrape_search(page: Page, query: str, max_accounts: int = 20) -> set:
    log.info(f"[search] '{query}'")
    await page.goto("https://www.instagram.com/", wait_until="networkidle")
    await _random_delay(page, 2, 3)

    usernames = set()
    try:
        # Click the search icon
        search_icon = page.locator('a[href="/explore/"]').first
        await search_icon.click()
        await _random_delay(page, 1, 2)

        search_input = page.locator('input[placeholder="Search"]')
        await search_input.fill(query)
        await _random_delay(page, 2, 4)

        # Grab account results from the dropdown
        results = page.locator('a[href^="/"][role="link"]')
        count = await results.count()
        for i in range(min(count, max_accounts)):
            href = await results.nth(i).get_attribute("href")
            if href:
                uname = href.strip("/")
                if uname and "explore" not in uname and "." not in uname:
                    usernames.add(uname)

        # Clear search
        await page.keyboard.press("Escape")
    except Exception as e:
        log.warning(f"Search scrape failed for '{query}': {e}")

    log.info(f"  → {len(usernames)} usernames from search '{query}'")
    return usernames


# ── Discovery method 3: Competitor followers ─────────────────────────────────

async def _scrape_followers(page: Page, account: str, max_accounts: int = 100) -> set:
    log.info(f"[followers] @{account}")
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

    log.info(f"  → {len(usernames)} usernames from @{account} followers")
    return usernames


# ── Discovery method 4: Suggested accounts ───────────────────────────────────

async def _scrape_suggested(page: Page, account: str, max_accounts: int = 30) -> set:
    """Scrape the 'suggested for you' sidebar on a competitor's profile."""
    log.info(f"[suggested] @{account}")
    await page.goto(f"https://www.instagram.com/{account}/", wait_until="networkidle")
    await _random_delay(page, 2, 4)

    usernames = set()
    try:
        # Suggested accounts appear in a sidebar section
        suggested = page.locator('div[data-testid="suggested-accounts"] a[href^="/"], '
                                  'aside a[href^="/"][role="link"]')
        count = await suggested.count()
        for i in range(min(count, max_accounts)):
            href = await suggested.nth(i).get_attribute("href")
            if href:
                uname = href.strip("/")
                if uname and "." not in uname and uname != account:
                    usernames.add(uname)
    except Exception as e:
        log.debug(f"Suggested scrape error for @{account}: {e}")

    log.info(f"  → {len(usernames)} usernames from @{account} suggested")
    return usernames


# ── Discovery method 5: Explore topic pages ──────────────────────────────────

async def _scrape_explore_topic(page: Page, topic: str, max_accounts: int = 30) -> set:
    """Browse Instagram Explore and collect brand accounts from posts."""
    log.info(f"[explore] topic={topic}")
    await page.goto(f"https://www.instagram.com/explore/", wait_until="networkidle")
    await _random_delay(page, 3, 5)

    usernames = set()
    try:
        # Click into first visible post and iterate
        posts = page.locator('article a[href*="/p/"]')
        if await posts.count() == 0:
            return usernames
        await posts.first.click()
        await _random_delay(page, 2, 3)

        for _ in range(max_accounts):
            try:
                username_el = page.locator('article header a[href^="/"]').first
                href = await username_el.get_attribute("href", timeout=3_000)
                if href:
                    uname = href.strip("/")
                    if uname:
                        usernames.add(uname)

                next_btn = page.locator('button[aria-label="Next"]').first
                if not await next_btn.is_visible(timeout=2_000):
                    break
                await next_btn.click()
                await _random_delay(page)
            except Exception:
                break

        await page.keyboard.press("Escape")
    except Exception as e:
        log.warning(f"Explore scrape error: {e}")

    log.info(f"  → {len(usernames)} usernames from Explore")
    return usernames


# ── Main discovery orchestrator ──────────────────────────────────────────────

async def discover_and_score(max_per_source: int = 50):
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

        # 1. Hashtags
        for tag in TARGET_HASHTAGS:
            try:
                found = await _scrape_hashtag(page, tag, max_accounts=max_per_source)
                all_usernames.update(found)
            except Exception as e:
                log.error(f"Error scraping #{tag}: {e}")
            await _random_delay(page, 5, 10)

        # 2. Search bar
        for query in TARGET_SEARCH_TERMS:
            try:
                found = await _scrape_search(page, query, max_accounts=20)
                all_usernames.update(found)
            except Exception as e:
                log.error(f"Error searching '{query}': {e}")
            await _random_delay(page, 4, 7)

        # 3. Competitor followers + suggested
        for account in TARGET_COMPETITOR_ACCOUNTS:
            try:
                found = await _scrape_followers(page, account, max_accounts=max_per_source)
                all_usernames.update(found)
            except Exception as e:
                log.error(f"Error scraping followers of @{account}: {e}")

            try:
                found = await _scrape_suggested(page, account, max_accounts=30)
                all_usernames.update(found)
            except Exception as e:
                log.error(f"Error scraping suggested for @{account}: {e}")

            await _random_delay(page, 5, 10)

        # 4. Explore page
        for topic in TARGET_EXPLORE_TOPICS:
            try:
                found = await _scrape_explore_topic(page, topic, max_accounts=30)
                all_usernames.update(found)
            except Exception as e:
                log.error(f"Error scraping Explore topic '{topic}': {e}")
            await _random_delay(page, 5, 8)

        log.info(f"Total unique candidates: {len(all_usernames)}")

        # Profile-check and score each candidate
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
