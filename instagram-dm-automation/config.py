"""
Central configuration for the Instagram DM Automation system.
Edit the values here to control targeting, messaging, and rate limits.
"""

# ── Instagram credentials ────────────────────────────────────────────────────
INSTAGRAM_USERNAME = ""   # your IG username
INSTAGRAM_PASSWORD = ""   # your IG password

# ── Rate limits ──────────────────────────────────────────────────────────────
DMS_PER_DAY = 100
MIN_DELAY_BETWEEN_DMS_SECONDS = 300   # 5 min minimum between each DM
MAX_DELAY_BETWEEN_DMS_SECONDS = 600   # 10 min maximum
SCRAPE_DELAY_SECONDS = (3, 8)         # random pause range while scraping

# ── Account filter thresholds ────────────────────────────────────────────────
FILTER = {
    "min_followers": 1_000,
    "max_followers": 10_000,
    "min_engagement_rate": 0.02,      # 2%
    "min_posts_per_week": 3,
    "require_shopify": False,          # set True to hard-require Shopify site
    "require_tiktok": False,           # set True to hard-require TikTok presence
    "max_score_to_skip": 3,           # accounts scoring below this are skipped
}

# ── Scoring rules (each matched criterion adds points) ───────────────────────
# Score is computed in analyzer.py. Higher = better match.
# Minimum passing score is set by FILTER["max_score_to_skip"].
SCORE_WEIGHTS = {
    "followers_in_range": 2,
    "engagement_above_threshold": 3,
    "posts_per_week_ok": 2,
    "has_shopify_site": 3,
    "active_on_tiktok": 2,
    "niche_match": 3,
    "recently_active": 1,             # posted in the last 7 days
    "has_website_in_bio": 1,
}

# ── Niche targeting ──────────────────────────────────────────────────────────
# Hashtags to scrape for candidate accounts
TARGET_HASHTAGS = [
    "cpgbrand",
    "wellnessbrand",
    "supplementbrand",
    "snackbrand",
    "fitnessbrand",
    "healthyfood",
    "functionalfood",
    "proteinsnacks",
    "cleaneating",
    "healthylifestyle",
    "newbrand",
    "dtcbrand",
    "ecommercebrand",
    "shopifystore",
]

# Competitor / niche accounts whose followers we will scrape
TARGET_COMPETITOR_ACCOUNTS = [
    # Add competitor IG usernames here, e.g.:
    # "ryse_supplements",
    # "poppi",
    # "olipop",
]

# Bio keywords that signal a good fit
BIO_POSITIVE_KEYWORDS = [
    "founder", "ceo", "co-founder", "brand", "wellness", "supplement",
    "nutrition", "snack", "fitness", "health", "protein", "organic",
    "plant-based", "keto", "vegan", "clean", "functional",
]

# Bio keywords that signal a bad fit → skip account
BIO_NEGATIVE_KEYWORDS = [
    "agency", "marketing agency", "dropship", "dropshipping", "aliexpress",
    "print on demand", "reseller",
]

# Username patterns to skip (regex)
SKIP_USERNAME_PATTERNS = [
    r"official$",          # large corporate handles often end with 'official'
    r"^the[a-z]+brand$",   # generic brand pattern
]

# ── DM message templates ─────────────────────────────────────────────────────
# Use {username} as a placeholder for the account's handle.
# Multiple templates are rotated to avoid detection.
DM_TEMPLATES = [
    # Template 1 — product is strong, content doesn't match it
    "ngl {brand_name} the product is genuinely one of the most compelling things in this space rn — but the content still feels more lifestyle / product showcase than internet-native stuff that actually hits\n\nme and my team already have a few concepts in mind and we'd love to make a couple free creatives just to show the vision. no strings attached — we genuinely think you're leaving reach on the table",

    # Template 2 — farm/founder/origin story angle
    "think the whole origin story behind {brand_name} could seriously resonate with gen z with the right short-form ugc leaning into that farm-to-bag / founder authenticity. me and my team already have a few concepts in mind and we'd love to make a couple free creatives just to show the vision. no strings attached — we genuinely think you're leaving reach on the table",

    # Template 3 — clean label / no seed oils / tiktok culture
    "ngl the whole clean label angle {brand_name} has going is genuinely one of the strongest positioning plays in the space rn — but the content still feels more product showcase than internet-native storytelling that actually converts\n\nme and my team already have a few concepts and would love to make a couple free creatives just to show the vision. no strings attached",

    # Template 4 — brand deserves better content
    "came across {brand_name} and the brand is genuinely sick — product, packaging, story. but the content doesn't do it justice yet. we were brainstorming some hard-hitting, internet-native creative ideas that lean into what makes you different and we'd love to make a couple for free just to show the vision. no strings attached — this brand deserves content as raw as the ingredients",
]

# ── Database path ────────────────────────────────────────────────────────────
DB_PATH = "dm_automation.db"
