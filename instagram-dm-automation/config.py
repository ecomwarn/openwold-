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
    "Hey {username}! Love what you're building 🙌 Your brand caught my eye — we help brands like yours scale with high-converting UGC & creator content. Would love to share a quick case study if you're open to it?",

    "Hi {username}! Your products look amazing. We specialize in helping CPG brands get more traction with content that actually converts. Mind if I send over some examples?",

    "Hey {username} 👋 Came across your brand and really liked the direction. We work with growing wellness/fitness brands on content strategy & UGC. Open to a quick chat?",

    "Hi {username}! We help brands in the wellness/supplement space create content that drives real sales. Your account seems like a great fit — would love to connect!",
]

# ── Database path ────────────────────────────────────────────────────────────
DB_PATH = "dm_automation.db"
