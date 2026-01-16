"""
Application Constants - Centralized configuration values.
All magic numbers and hardcoded values should be defined here.
"""
from typing import Dict, Tuple
import os

# ==================== Currency & Pricing ====================
# LBP to USD exchange rate (update this when rate changes)
LBP_TO_USD_RATE: float = float(os.getenv("LBP_USD_RATE", "89500"))

# Delivery fees (in USD)
DEFAULT_DELIVERY_FEE_USD: float = float(os.getenv("DEFAULT_DELIVERY_FEE_USD", "3.0"))
DEFAULT_DELIVERY_FEE_LBP: float = DEFAULT_DELIVERY_FEE_USD * LBP_TO_USD_RATE

# Minimum order amount (in USD)
MIN_ORDER_AMOUNT_USD: float = float(os.getenv("MIN_ORDER_AMOUNT_USD", "5.0"))


# ==================== Loyalty Program ====================
# Points per USD spent
LOYALTY_POINTS_PER_USD: int = int(os.getenv("LOYALTY_POINTS_PER_USD", "10"))

# Tier thresholds (lifetime points required)
LOYALTY_TIER_THRESHOLDS: Dict[str, int] = {
    "bronze": 0,
    "silver": 1000,
    "gold": 5000,
    "platinum": 15000
}

# Tier multipliers for earning points
LOYALTY_TIER_MULTIPLIERS: Dict[str, float] = {
    "bronze": 1.0,
    "silver": 1.25,
    "gold": 1.5,
    "platinum": 2.0
}

# Tier display info (icon, name_en, name_ar)
LOYALTY_TIER_INFO: Dict[str, Tuple[str, str, str]] = {
    "bronze": ("🥉", "Bronze", "برونز"),
    "silver": ("🥈", "Silver", "فضي"),
    "gold": ("🥇", "Gold", "ذهبي"),
    "platinum": ("💎", "Platinum", "بلاتيني")
}

# Review bonus points
REVIEW_BONUS_POINTS: int = int(os.getenv("REVIEW_BONUS_POINTS", "10"))

# Points expiry (days)
POINTS_EXPIRY_DAYS: int = int(os.getenv("POINTS_EXPIRY_DAYS", "365"))


# ==================== Rate Limiting ====================
# AI requests per user per minute
AI_RATE_LIMIT_REQUESTS: int = int(os.getenv("AI_RATE_LIMIT_REQUESTS", "15"))
AI_RATE_LIMIT_WINDOW: int = int(os.getenv("AI_RATE_LIMIT_WINDOW", "60"))

# Login attempts per minute
LOGIN_RATE_LIMIT_REQUESTS: int = int(os.getenv("LOGIN_RATE_LIMIT_REQUESTS", "3"))
LOGIN_RATE_LIMIT_WINDOW: int = int(os.getenv("LOGIN_RATE_LIMIT_WINDOW", "60"))

# General API rate limit
API_RATE_LIMIT_REQUESTS: int = int(os.getenv("API_RATE_LIMIT_REQUESTS", "100"))
API_RATE_LIMIT_WINDOW: int = int(os.getenv("API_RATE_LIMIT_WINDOW", "60"))


# ==================== Session & Cache ====================
# Cart expiry (seconds) - 24 hours
CART_EXPIRY_SECONDS: int = int(os.getenv("CART_EXPIRY_SECONDS", "86400"))

# Conversation memory expiry (seconds) - 30 minutes
CONVERSATION_EXPIRY_SECONDS: int = int(os.getenv("CONVERSATION_EXPIRY_SECONDS", "1800"))

# User state expiry (seconds) - 24 hours
USER_STATE_EXPIRY_SECONDS: int = int(os.getenv("USER_STATE_EXPIRY_SECONDS", "86400"))

# Pending review expiry (seconds) - 24 hours
PENDING_REVIEW_EXPIRY_SECONDS: int = int(os.getenv("PENDING_REVIEW_EXPIRY_SECONDS", "86400"))

# Analytics data retention (seconds) - 7 days
ANALYTICS_RETENTION_SECONDS: int = int(os.getenv("ANALYTICS_RETENTION_SECONDS", "604800"))


# ==================== Database ====================
# Connection pool settings
DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "5"))
DB_MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "10"))
DB_POOL_RECYCLE: int = int(os.getenv("DB_POOL_RECYCLE", "300"))
DB_POOL_TIMEOUT: int = int(os.getenv("DB_POOL_TIMEOUT", "30"))


# ==================== AI Service ====================
# Temperature for AI responses (0.0 - 1.0)
AI_TEMPERATURE: float = float(os.getenv("AI_TEMPERATURE", "0.4"))

# Max suggestions to show
AI_MAX_SUGGESTIONS: int = int(os.getenv("AI_MAX_SUGGESTIONS", "5"))

# Max products in context
AI_MAX_PRODUCTS_CONTEXT: int = int(os.getenv("AI_MAX_PRODUCTS_CONTEXT", "80"))

# Max conversation messages to keep
AI_MAX_CONVERSATION_MESSAGES: int = int(os.getenv("AI_MAX_CONVERSATION_MESSAGES", "10"))


# ==================== WhatsApp ====================
# API version
WHATSAPP_API_VERSION: str = os.getenv("WHATSAPP_API_VERSION", "v18.0")

# Message limits
WHATSAPP_MAX_BUTTONS: int = 3
WHATSAPP_MAX_LIST_ITEMS: int = 10
WHATSAPP_MAX_LIST_SECTIONS: int = 10
WHATSAPP_MAX_TITLE_LENGTH: int = 24
WHATSAPP_MAX_DESCRIPTION_LENGTH: int = 72


# ==================== Pagination ====================
# Default page size
DEFAULT_PAGE_SIZE: int = int(os.getenv("DEFAULT_PAGE_SIZE", "10"))
MAX_PAGE_SIZE: int = int(os.getenv("MAX_PAGE_SIZE", "100"))

# Restaurant list pagination
RESTAURANTS_PER_PAGE: int = 9  # Leave room for "More" option


# ==================== Validation ====================
# Phone number regex (Lebanese format)
PHONE_REGEX: str = r"^(\+961|961|0)?[1-9]\d{6,7}$"

# Quantity limits
MIN_QUANTITY: int = 1
MAX_QUANTITY: int = 99

# Price limits
MIN_PRICE: float = 0.0
MAX_PRICE: float = 1000000.0

# Address limits
MIN_ADDRESS_LENGTH: int = 5
MAX_ADDRESS_LENGTH: int = 500

# Coordinates bounds (Lebanon approximate)
LAT_MIN: float = 33.0
LAT_MAX: float = 34.7
LNG_MIN: float = 35.0
LNG_MAX: float = 36.7


# ==================== Security ====================
# Token expiry (minutes)
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "10080"))  # 7 days

# Password requirements
PASSWORD_MIN_LENGTH: int = 8
PASSWORD_REQUIRE_UPPERCASE: bool = True
PASSWORD_REQUIRE_LOWERCASE: bool = True
PASSWORD_REQUIRE_DIGIT: bool = True


# ==================== Helper Functions ====================
def lbp_to_usd(amount_lbp) -> float:
    """Convert LBP to USD"""
    if amount_lbp is None or amount_lbp == 0:
        return 0.0
    # Convert Decimal to float if needed
    return float(amount_lbp) / LBP_TO_USD_RATE


def usd_to_lbp(amount_usd) -> float:
    """Convert USD to LBP"""
    if amount_usd is None or amount_usd == 0:
        return 0.0
    # Convert Decimal to float if needed
    return float(amount_usd) * LBP_TO_USD_RATE


def format_price_usd(amount_lbp: float) -> str:
    """Format LBP amount as USD string"""
    usd = lbp_to_usd(amount_lbp)
    return f"${usd:.2f}"


def get_tier_for_points(lifetime_points: int) -> str:
    """Get loyalty tier based on lifetime points"""
    if lifetime_points >= LOYALTY_TIER_THRESHOLDS["platinum"]:
        return "platinum"
    elif lifetime_points >= LOYALTY_TIER_THRESHOLDS["gold"]:
        return "gold"
    elif lifetime_points >= LOYALTY_TIER_THRESHOLDS["silver"]:
        return "silver"
    return "bronze"


def get_next_tier(current_tier: str) -> Tuple[str, int]:
    """Get next tier and points needed"""
    tiers = ["bronze", "silver", "gold", "platinum"]
    current_index = tiers.index(current_tier) if current_tier in tiers else 0

    if current_index >= len(tiers) - 1:
        return (None, 0)  # Already at max tier

    next_tier = tiers[current_index + 1]
    return (next_tier, LOYALTY_TIER_THRESHOLDS[next_tier])
