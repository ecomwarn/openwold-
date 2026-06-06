"""
Generates a personalized cold DM for each account using Claude.
Falls back to a hand-written template if the API key isn't set.
"""

import random
import logging
import anthropic
from config import ANTHROPIC_API_KEY, OUR_AGENCY_DESCRIPTION

log = logging.getLogger(__name__)

# Fallback templates if no API key is set
FALLBACK_TEMPLATES = [
    "ngl {brand_name} the product is genuinely one of the most compelling things in this space rn — but the content still feels more lifestyle / product showcase than internet-native stuff that actually hits\n\nme and my team already have a few concepts in mind and we'd love to make a couple free creatives just to show the vision. no strings attached — we genuinely think you're leaving reach on the table",

    "think the whole origin story behind {brand_name} could seriously resonate with gen z with the right short-form ugc. me and my team already have a few concepts in mind and we'd love to make a couple free creatives just to show the vision. no strings attached — we genuinely think you're leaving reach on the table",

    "came across {brand_name} and the brand is genuinely sick — product, packaging, story. but the content doesn't do it justice yet. we'd love to make a couple free creatives just to show the vision. no strings attached",

    "ngl the whole clean label angle {brand_name} has going is genuinely one of the strongest positioning plays in the space rn — but the content still feels more product showcase than internet-native storytelling that actually converts\n\nwe'd love to make a couple free creatives just to show the vision. no strings attached",
]


def generate_dm(account: dict) -> str:
    """
    account dict keys: username, full_name, bio, website, followers,
    engagement_rate, posts_per_week, is_shopify, has_tiktok, niche_tags, score
    """
    brand_name = _derive_brand_name(account.get("full_name", ""), account.get("username", ""))

    if not ANTHROPIC_API_KEY:
        log.warning("No ANTHROPIC_API_KEY set — using fallback template.")
        return random.choice(FALLBACK_TEMPLATES).replace("{brand_name}", brand_name)

    try:
        return _call_claude(account, brand_name)
    except Exception as e:
        log.error(f"Claude API error for @{account.get('username')}: {e}")
        return random.choice(FALLBACK_TEMPLATES).replace("{brand_name}", brand_name)


def _call_claude(account: dict, brand_name: str) -> str:
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    bio          = account.get("bio", "") or "not available"
    website      = account.get("website", "") or "none listed"
    followers    = account.get("followers", 0)
    engagement   = round((account.get("engagement_rate") or 0) * 100, 1)
    ppw          = account.get("posts_per_week", 0)
    is_shopify   = account.get("is_shopify", 0)
    has_tiktok   = account.get("has_tiktok", 0)
    niche_tags   = ", ".join(account.get("niche_tags") or []) or "not detected"

    prompt = f"""You are writing a cold Instagram DM on behalf of a creative agency called Oishi Creatives.

About us:
{OUR_AGENCY_DESCRIPTION.strip()}

About the brand we're DMing:
- Brand name: {brand_name}
- Instagram bio: {bio}
- Website: {website}
- Followers: {followers:,}
- Engagement rate: {engagement}%
- Posts per week: {ppw}
- On Shopify: {"yes" if is_shopify else "unknown"}
- Active on TikTok: {"yes" if has_tiktok else "unknown"}
- Niche signals: {niche_tags}

Write ONE short cold DM (3–5 sentences max) that:
- Leads with something genuine and specific about THIS brand — their product angle, positioning, or content gap. Reference something real from their bio or niche.
- Is written in a very casual, gen z tone — lowercase, no corporate speak, feels like a real person not a bot
- Points out (kindly, not harshly) that their content doesn't match how good the product/brand actually is
- Offers to make a couple free creatives just to show the vision, no strings attached
- Ends with a soft open-ended question or statement — NOT "book a call", NOT "let me know your thoughts"
- Does NOT mention follower counts, engagement rates, or any metrics
- Does NOT use emojis except maybe 1 at most
- Does NOT start with "Hey" or "Hi" — just dive in

Return ONLY the DM text. No quotes, no subject line, no explanation."""

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}],
    )

    return message.content[0].text.strip()


def _derive_brand_name(full_name: str, username: str) -> str:
    import re
    name = (full_name or "").strip()
    if name and len(name) > 3 and not name.islower():
        return name
    cleaned = re.sub(r"[_.\-]", " ", username).strip()
    return cleaned
