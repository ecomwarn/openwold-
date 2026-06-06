"""
SQLite queue and tracking for discovered accounts and DM status.
"""

import sqlite3
import json
from datetime import datetime
from config import DB_PATH


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_conn() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS accounts (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                username        TEXT UNIQUE NOT NULL,
                full_name       TEXT,
                followers       INTEGER,
                following       INTEGER,
                post_count      INTEGER,
                engagement_rate REAL,
                posts_per_week  REAL,
                bio             TEXT,
                website         TEXT,
                is_shopify      INTEGER DEFAULT 0,
                has_tiktok      INTEGER DEFAULT 0,
                niche_tags      TEXT,   -- JSON list
                score           INTEGER DEFAULT 0,
                status          TEXT DEFAULT 'pending',
                -- pending | approved | skipped | dm_sent | dm_failed
                dm_sent_at      TEXT,
                dm_template_idx INTEGER,
                notes           TEXT,
                discovered_at   TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS daily_log (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                date        TEXT NOT NULL,
                dms_sent    INTEGER DEFAULT 0,
                dms_failed  INTEGER DEFAULT 0
            );
        """)


def upsert_account(data: dict):
    """Insert or ignore a discovered account."""
    with get_conn() as conn:
        conn.execute("""
            INSERT OR IGNORE INTO accounts
                (username, full_name, followers, following, post_count,
                 engagement_rate, posts_per_week, bio, website,
                 is_shopify, has_tiktok, niche_tags, score, status)
            VALUES
                (:username, :full_name, :followers, :following, :post_count,
                 :engagement_rate, :posts_per_week, :bio, :website,
                 :is_shopify, :has_tiktok, :niche_tags, :score, :status)
        """, {
            **data,
            "niche_tags": json.dumps(data.get("niche_tags", [])),
        })


def update_status(username: str, status: str, notes: str = ""):
    with get_conn() as conn:
        conn.execute(
            "UPDATE accounts SET status=?, notes=? WHERE username=?",
            (status, notes, username),
        )


def mark_dm_sent(username: str, template_idx: int):
    with get_conn() as conn:
        conn.execute(
            "UPDATE accounts SET status='dm_sent', dm_sent_at=?, dm_template_idx=? WHERE username=?",
            (datetime.utcnow().isoformat(), template_idx, username),
        )
    _increment_daily_log("dms_sent")


def mark_dm_failed(username: str, reason: str = ""):
    with get_conn() as conn:
        conn.execute(
            "UPDATE accounts SET status='dm_failed', notes=? WHERE username=?",
            (reason, username),
        )
    _increment_daily_log("dms_failed")


def _increment_daily_log(field: str):
    today = datetime.utcnow().strftime("%Y-%m-%d")
    with get_conn() as conn:
        conn.execute(
            f"INSERT OR IGNORE INTO daily_log (date) VALUES (?)", (today,)
        )
        conn.execute(
            f"UPDATE daily_log SET {field}={field}+1 WHERE date=?", (today,)
        )


def dms_sent_today() -> int:
    today = datetime.utcnow().strftime("%Y-%m-%d")
    with get_conn() as conn:
        row = conn.execute(
            "SELECT dms_sent FROM daily_log WHERE date=?", (today,)
        ).fetchone()
    return row["dms_sent"] if row else 0


def get_approved_queue(limit: int = 200):
    """Return accounts approved for DMing that haven't been contacted yet."""
    with get_conn() as conn:
        return conn.execute(
            "SELECT * FROM accounts WHERE status='approved' ORDER BY score DESC LIMIT ?",
            (limit,),
        ).fetchall()


def get_stats():
    with get_conn() as conn:
        total    = conn.execute("SELECT COUNT(*) FROM accounts").fetchone()[0]
        pending  = conn.execute("SELECT COUNT(*) FROM accounts WHERE status='pending'").fetchone()[0]
        approved = conn.execute("SELECT COUNT(*) FROM accounts WHERE status='approved'").fetchone()[0]
        sent     = conn.execute("SELECT COUNT(*) FROM accounts WHERE status='dm_sent'").fetchone()[0]
        skipped  = conn.execute("SELECT COUNT(*) FROM accounts WHERE status='skipped'").fetchone()[0]
        failed   = conn.execute("SELECT COUNT(*) FROM accounts WHERE status='dm_failed'").fetchone()[0]
    return {
        "total": total,
        "pending": pending,
        "approved": approved,
        "dm_sent": sent,
        "skipped": skipped,
        "dm_failed": failed,
        "dms_today": dms_sent_today(),
    }
