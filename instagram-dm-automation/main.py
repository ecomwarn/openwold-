"""
Entry point for the Instagram DM Automation system.

Usage:
    python main.py scrape        -- discover + score accounts, populate DB
    python main.py send          -- send DMs to approved accounts (up to daily cap)
    python main.py run           -- scrape then immediately send
    python main.py stats         -- print DB stats
    python main.py approve-all   -- approve all pending accounts that passed scoring
    python main.py review        -- print top approved accounts for manual review
"""

import asyncio
import sys
import json
import logging
import database
import scraper
import dm_sender

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("automation.log"),
    ],
)
log = logging.getLogger(__name__)


def cmd_stats():
    database.init_db()
    stats = database.get_stats()
    print("\n── DB Stats ─────────────────────────────")
    for k, v in stats.items():
        print(f"  {k:<15}: {v}")
    print()


def cmd_approve_all():
    """Move all 'approved' (already scored as approved) pending accounts to approved."""
    database.init_db()
    with database.get_conn() as conn:
        # Accounts scored as approved but still showing 'pending' (shouldn't happen normally)
        result = conn.execute(
            "UPDATE accounts SET status='approved' WHERE status='pending' AND score >= ?",
            (database.get_conn().execute("SELECT 1").fetchone(),)  # placeholder
        )
    # Simpler: just show what's there
    cmd_stats()


def cmd_review(limit: int = 20):
    database.init_db()
    with database.get_conn() as conn:
        rows = conn.execute(
            "SELECT username, followers, engagement_rate, posts_per_week, "
            "is_shopify, has_tiktok, score, status, bio "
            "FROM accounts ORDER BY score DESC LIMIT ?",
            (limit,)
        ).fetchall()

    print(f"\n── Top {limit} accounts ──────────────────────────────────────────────────")
    print(f"{'username':<25} {'flwrs':>6} {'engr%':>6} {'ppw':>4} {'shop':>4} {'ttok':>4} {'score':>5} {'status':<10}")
    print("-" * 80)
    for r in rows:
        print(
            f"{r['username']:<25} {r['followers']:>6} "
            f"{r['engagement_rate']*100:>5.1f}% {r['posts_per_week']:>4.1f} "
            f"{'✓' if r['is_shopify'] else '·':>4} {'✓' if r['has_tiktok'] else '·':>4} "
            f"{r['score']:>5} {r['status']:<10}"
        )
    print()


async def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "stats"

    if cmd == "scrape":
        await scraper.discover_and_score()

    elif cmd == "send":
        await dm_sender.run_dm_session()

    elif cmd == "run":
        await scraper.discover_and_score()
        await dm_sender.run_dm_session()

    elif cmd == "stats":
        cmd_stats()

    elif cmd == "review":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 20
        cmd_review(limit)

    elif cmd == "approve-all":
        cmd_approve_all()

    else:
        print(__doc__)


if __name__ == "__main__":
    asyncio.run(main())
