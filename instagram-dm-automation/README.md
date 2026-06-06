# Instagram DM Automation

Automated outreach system for finding and DMing CPG/wellness/supplement/fitness brands on Instagram.

## Setup

```bash
cd instagram-dm-automation
pip install -r requirements.txt
playwright install chromium
```

Edit `config.py` and fill in:
- `INSTAGRAM_USERNAME` / `INSTAGRAM_PASSWORD`
- `TARGET_HASHTAGS` (already pre-filled with CPG/wellness hashtags)
- `TARGET_COMPETITOR_ACCOUNTS` (optional — scrapes their followers)
- `DM_TEMPLATES` (your outreach messages)

## Usage

```bash
# Discover accounts and score them (populates DB)
python main.py scrape

# Review the top-scored accounts before sending
python main.py review 30

# Send DMs to approved accounts (up to 100/day)
python main.py send

# Or do both in one go
python main.py run

# Check stats
python main.py stats
```

## How It Works

1. **Scraper** (`scraper.py`) — logs into Instagram via Playwright, iterates through hashtag posts and competitor follower lists, visits each candidate profile, and extracts: followers, engagement rate, posting frequency, bio, and website.

2. **Analyzer** (`analyzer.py`) — scores each account against your criteria (1k–10k followers, 2%+ engagement, 3+/week posting, Shopify site, TikTok presence, bio niche keywords). Accounts below the minimum score are marked `skipped`; others are marked `approved`.

3. **DM Sender** (`dm_sender.py`) — iterates through `approved` accounts, opens a DM thread via the Message button on their profile, types the message character-by-character (human-like), and waits 5–10 minutes between each send to stay under Instagram's radar.

4. **Database** (`dm_automation.db`) — SQLite file tracking every account: score, status, when DM was sent, which template was used, and daily send totals.

## Scoring Criteria

| Criterion | Points |
|---|---|
| Followers in 1k–10k range | 2 |
| Engagement rate ≥ 2% | 3 |
| Posts/week ≥ 3 | 2 |
| Shopify website | 3 |
| Active on TikTok (bio link) | 2 |
| Niche keyword in bio | 3 |
| Posted in last 7 days | 1 |
| Has website in bio | 1 |

Minimum passing score: **3** (configurable in `config.py`)

## ⚠️ Risk Notice

This tool uses browser automation against Instagram's ToS. Use a dedicated account, start slow (20–30 DMs/day before ramping to 100), and rotate message templates. Sending too fast or from a fresh account risks temporary action blocks.
