"""
Central configuration for the Instagram DM Automation system.
Edit the values here to control targeting, messaging, and rate limits.
"""

# ── Instagram credentials ────────────────────────────────────────────────────
INSTAGRAM_USERNAME = "oishicreatives"
INSTAGRAM_PASSWORD = "Minecraft#4"

# ── Anthropic API key (for per-account personalized DMs) ────────────────────
# Get one at https://console.anthropic.com
ANTHROPIC_API_KEY = ""  # paste your key here

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
    "require_shopify": False,
    "require_tiktok": False,
    "max_score_to_skip": 3,
}

# ── Scoring rules ────────────────────────────────────────────────────────────
SCORE_WEIGHTS = {
    "followers_in_range": 2,
    "engagement_above_threshold": 3,
    "posts_per_week_ok": 2,
    "has_shopify_site": 3,
    "active_on_tiktok": 2,
    "niche_match": 3,
    "recently_active": 1,
    "has_website_in_bio": 1,
}

# ── Discovery sources ────────────────────────────────────────────────────────
# Hashtags — posts under these tags will be scraped for brand accounts
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
    "founderlife",
    "bootstrappedfounder",
    "cpgfounder",
    "brandbuilder",
    "consumerbrand",
]

# Instagram search terms — used with the IG search bar to find accounts
TARGET_SEARCH_TERMS = [
    "wellness brand",
    "supplement brand",
    "protein snack",
    "clean snack",
    "functional food",
    "cpg brand",
    "healthy snack brand",
    "fitness supplement",
    "primal nutrition",
    "organic protein",
]

# Competitor / niche accounts — their followers + suggested accounts get scraped
TARGET_COMPETITOR_ACCOUNTS = [
    # Add usernames of brands your targets follow/look up to, e.g.:
    # "poppi",
    # "olipop",
    # "ryse_supplements",
    # "magicspoon",
]

# Explore page niche tags to browse (Instagram Explore topic pages)
TARGET_EXPLORE_TOPICS = [
    "fitness",
    "wellness",
    "nutrition",
    "health",
]

# Bio keywords that signal a good fit
BIO_POSITIVE_KEYWORDS = [
    "founder", "ceo", "co-founder", "brand", "wellness", "supplement",
    "nutrition", "snack", "fitness", "health", "protein", "organic",
    "plant-based", "keto", "vegan", "clean", "functional", "primal",
    "grass-fed", "collagen", "creatine", "colostrum", "adaptogen",
    "nootropic", "gut health", "seed oil free", "no seed oils",
]

# Bio keywords that disqualify
BIO_NEGATIVE_KEYWORDS = [
    "agency", "marketing agency", "dropship", "dropshipping", "aliexpress",
    "print on demand", "reseller", "mlm", "network marketing",
]

# Username patterns to skip (regex)
SKIP_USERNAME_PATTERNS = [
    r"official$",
    r"^the[a-z]+brand$",
]

# ── Who we are (injected into the AI prompt for personalized DMs) ────────────
OUR_AGENCY_DESCRIPTION = """
We're a small creative team (oishi creatives) that makes internet-native short-form content
for CPG, wellness, supplement, snack, and fitness brands. We specialize in UGC,
creator-style videos, and hard-hitting social ads that actually convert — not just
polished brand content. We offer a few free creatives upfront to show the vision,
no strings attached.
"""

# ── Database path ────────────────────────────────────────────────────────────
DB_PATH = "dm_automation.db"
