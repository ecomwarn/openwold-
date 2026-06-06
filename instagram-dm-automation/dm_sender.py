"""
Sends DMs to approved accounts using a logged-in Playwright session.
Generates a personalized message per account via Claude API.
Respects daily limits and uses randomized human-like delays.
"""

import asyncio
import random
import logging
from playwright.async_api import async_playwright, Page

import database
import message_generator
from scraper import login, _random_delay
from config import (
    DMS_PER_DAY,
    MIN_DELAY_BETWEEN_DMS_SECONDS,
    MAX_DELAY_BETWEEN_DMS_SECONDS,
)

log = logging.getLogger(__name__)


async def _send_dm(page: Page, username: str, message: str) -> bool:
    """Open Instagram DM compose and send a message to `username`."""
    try:
        await page.goto(f"https://www.instagram.com/{username}/", wait_until="networkidle", timeout=15_000)
        await _random_delay(page, 2, 4)

        msg_btn = page.locator('div[role="button"]:has-text("Message"), button:has-text("Message")')
        if not await msg_btn.first.is_visible(timeout=5_000):
            log.warning(f"@{username}: No Message button found (private/blocked?)")
            return False

        await msg_btn.first.click()
        await _random_delay(page, 2, 3)

        text_box = page.locator(
            'div[contenteditable="true"][role="textbox"], '
            'textarea[placeholder*="Message"]'
        ).first

        if not await text_box.is_visible(timeout=8_000):
            log.warning(f"@{username}: DM textbox not visible")
            return False

        await text_box.click()
        # Type character by character to mimic human speed
        for char in message:
            await text_box.type(char, delay=random.randint(30, 90))

        await _random_delay(page, 1, 2)
        await text_box.press("Enter")
        await _random_delay(page, 2, 3)

        log.info(f"DM sent to @{username}")
        return True

    except Exception as e:
        log.error(f"DM failed for @{username}: {e}")
        return False


async def run_dm_session():
    """Send DMs to all approved accounts up to today's daily cap."""
    database.init_db()

    already_sent = database.dms_sent_today()
    remaining = DMS_PER_DAY - already_sent

    if remaining <= 0:
        log.info(f"Daily DM cap ({DMS_PER_DAY}) already reached. Exiting.")
        return

    queue = database.get_approved_queue(limit=remaining + 20)

    if not queue:
        log.info("No approved accounts in queue. Run scraper first.")
        return

    log.info(f"Starting DM session. Cap: {DMS_PER_DAY}, sent today: {already_sent}, queue: {len(queue)}")

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

        sent_count = 0
        for row in queue:
            if sent_count >= remaining:
                log.info("Daily DM cap reached for this session.")
                break

            username = row["username"]
            account_data = dict(row)

            # Generate a personalized DM for this specific account
            log.info(f"Generating DM for @{username}...")
            message = message_generator.generate_dm(account_data)
            log.info(f"  Message: {message[:80]}...")

            success = await _send_dm(page, username, message)

            if success:
                database.mark_dm_sent(username, template_idx=0)
                sent_count += 1
                log.info(f"[{sent_count}/{remaining}] ✓ @{username}")
            else:
                database.mark_dm_failed(username, "send_failed")

            delay = random.randint(MIN_DELAY_BETWEEN_DMS_SECONDS, MAX_DELAY_BETWEEN_DMS_SECONDS)
            log.info(f"Waiting {delay}s before next DM...")
            await asyncio.sleep(delay)

        await browser.close()

    log.info(f"DM session complete. Sent {sent_count} DMs today.")
