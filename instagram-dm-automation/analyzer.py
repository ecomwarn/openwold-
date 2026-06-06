"""
Scores and filters a candidate Instagram account against the targeting criteria.
Returns a scored dict ready for upsert_account().
"""

import re
import json
import requests
from urllib.parse import urlparse
from config import FILTER, SCORE_WEIGHTS, BIO_POSITIVE_KEYWORDS, BIO_NEGATIVE_KEYWORDS, SKIP_USERNAME_PATTERNS


def should_skip_username(username: str) -> bool:
    for pattern in SKIP_USERNAME_PATTERNS:
        if re.search(pattern, username, re.IGNORECASE):
            return True
    return False


def _check_shopify(website: str) -> bool:
    """Fetch the website and look for Shopify fingerprints."""
    if not website:
        return False
    try:
        url = website if website.startswith("http") else f"https://{website}"
        r = requests.get(url, timeout=8, allow_redirects=True,
                         headers={"User-Agent": "Mozilla/5.0"})
        body = r.text.lower()
        return "myshopify.com" in r.url or "shopify" in body or "cdn.shopify.com" in body
    except Exception:
        return False


def _check_tiktok(username: str, bio: str) -> bool:
    """Check bio/website for TikTok links."""
    combined = (bio or "").lower()
    return "tiktok.com" in combined or "@tiktok" in combined


def _niche_tags_from_bio(bio: str) -> list[str]:
    bio_lower = (bio or "").lower()
    positive_hits = [kw for kw in BIO_POSITIVE_KEYWORDS if kw in bio_lower]
    return positive_hits


def score_account(raw: dict) -> dict:
    """
    raw keys expected:
        username, full_name, followers, following, post_count,
        avg_likes, avg_comments, bio, website,
        recent_post_dates  (list of ISO date strings, most recent first)

    Returns the same dict enriched with: score, status, engagement_rate,
    posts_per_week, is_shopify, has_tiktok, niche_tags
    """
    username   = raw.get("username", "")
    followers  = raw.get("followers", 0)
    following  = raw.get("following", 0)
    post_count = raw.get("post_count", 0)
    avg_likes  = raw.get("avg_likes", 0)
    avg_comments = raw.get("avg_comments", 0)
    bio        = raw.get("bio", "") or ""
    website    = raw.get("website", "") or ""
    recent_dates = raw.get("recent_post_dates", [])

    # ── Hard disqualifiers ───────────────────────────────────────────────────
    if should_skip_username(username):
        return {**raw, "score": 0, "status": "skipped", "notes": "username pattern match"}

    bio_lower = bio.lower()
    for neg in BIO_NEGATIVE_KEYWORDS:
        if neg in bio_lower:
            return {**raw, "score": 0, "status": "skipped", "notes": f"negative bio keyword: {neg}"}

    if followers < 100:
        return {**raw, "score": 0, "status": "skipped", "notes": "under 100 followers"}

    # ── Engagement rate ──────────────────────────────────────────────────────
    engagement_rate = 0.0
    if followers > 0:
        engagement_rate = (avg_likes + avg_comments) / followers

    # ── Posts per week ───────────────────────────────────────────────────────
    posts_per_week = 0.0
    if len(recent_dates) >= 2:
        from datetime import datetime
        try:
            newest = datetime.fromisoformat(recent_dates[0])
            oldest = datetime.fromisoformat(recent_dates[-1])
            days_span = max((newest - oldest).days, 1)
            posts_per_week = (len(recent_dates) / days_span) * 7
        except Exception:
            pass

    # ── Shopify + TikTok ─────────────────────────────────────────────────────
    is_shopify = _check_shopify(website)
    has_tiktok = _check_tiktok(username, bio)

    # ── Recency ──────────────────────────────────────────────────────────────
    recently_active = False
    if recent_dates:
        from datetime import datetime, timezone
        try:
            latest = datetime.fromisoformat(recent_dates[0])
            delta = datetime.now() - latest
            recently_active = delta.days <= 7
        except Exception:
            pass

    niche_tags = _niche_tags_from_bio(bio)
    has_website = bool(website.strip())

    # ── Score ────────────────────────────────────────────────────────────────
    score = 0
    f = FILTER
    w = SCORE_WEIGHTS

    if f["min_followers"] <= followers <= f["max_followers"]:
        score += w["followers_in_range"]
    if engagement_rate >= f["min_engagement_rate"]:
        score += w["engagement_above_threshold"]
    if posts_per_week >= f["min_posts_per_week"]:
        score += w["posts_per_week_ok"]
    if is_shopify:
        score += w["has_shopify_site"]
    if has_tiktok:
        score += w["active_on_tiktok"]
    if niche_tags:
        score += w["niche_match"]
    if recently_active:
        score += w["recently_active"]
    if has_website:
        score += w["has_website_in_bio"]

    # ── Final status ─────────────────────────────────────────────────────────
    hard_fail = (
        followers < f["min_followers"] or
        followers > f["max_followers"] or
        (f["require_shopify"] and not is_shopify) or
        (f["require_tiktok"] and not has_tiktok)
    )

    if hard_fail or score < f["max_score_to_skip"]:
        status = "skipped"
    else:
        status = "approved"

    return {
        **raw,
        "engagement_rate": round(engagement_rate, 4),
        "posts_per_week": round(posts_per_week, 2),
        "is_shopify": int(is_shopify),
        "has_tiktok": int(has_tiktok),
        "niche_tags": niche_tags,
        "score": score,
        "status": status,
    }
