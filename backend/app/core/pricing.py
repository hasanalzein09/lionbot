"""
Pricing Module - Handles delivery fee and commission calculations
"""
from typing import Optional
from app.core.config import settings
import math

# Subscription Tiers Configuration
SUBSCRIPTION_TIERS = {
    "basic": {
        "name": "Basic",
        "monthly_fee": 0,
        "commission_rate": 0.15,  # 15%
        "max_orders_per_month": 100,
        "features": ["basic_analytics", "whatsapp_orders"]
    },
    "pro": {
        "name": "Pro",
        "monthly_fee": 99,
        "commission_rate": 0.10,  # 10%
        "max_orders_per_month": 500,
        "features": ["basic_analytics", "whatsapp_orders", "priority_support", "custom_branding"]
    },
    "enterprise": {
        "name": "Enterprise",
        "monthly_fee": 299,
        "commission_rate": 0.05,  # 5%
        "max_orders_per_month": None,  # Unlimited
        "features": ["advanced_analytics", "whatsapp_orders", "priority_support", "custom_branding", "api_access", "dedicated_manager"]
    }
}

# Delivery Fee Configuration - Values from settings with defaults
def get_delivery_config() -> dict:
    """Get delivery configuration from settings."""
    return {
        "base_fee": getattr(settings, 'BASE_DELIVERY_FEE', 2.0),
        "per_km_fee": getattr(settings, 'PER_KM_DELIVERY_FEE', 0.5),
        "min_fee": getattr(settings, 'MIN_DELIVERY_FEE', 2.0),
        "max_fee": getattr(settings, 'MAX_DELIVERY_FEE', 15.0),
        "free_delivery_threshold": getattr(settings, 'FREE_DELIVERY_THRESHOLD', 50.0),
        "surge_multiplier": getattr(settings, 'SURGE_MULTIPLIER', 1.0),
    }


# Backward compatibility
DELIVERY_CONFIG = get_delivery_config()


def calculate_delivery_fee(
    distance_km: float,
    order_total: float,
    surge_multiplier: Optional[float] = None
) -> float:
    """
    Calculate delivery fee based on distance and order total.
    
    Args:
        distance_km: Distance from restaurant to delivery location in kilometers
        order_total: Total order amount before delivery fee
        surge_multiplier: Optional surge pricing multiplier
        
    Returns:
        Calculated delivery fee
    """
    # Free delivery for orders above threshold
    if order_total >= DELIVERY_CONFIG["free_delivery_threshold"]:
        return 0.0
    
    # Base calculation
    base_fee = DELIVERY_CONFIG["base_fee"]
    distance_fee = distance_km * DELIVERY_CONFIG["per_km_fee"]
    
    total_fee = base_fee + distance_fee
    
    # Apply surge pricing if applicable
    multiplier = surge_multiplier or DELIVERY_CONFIG["surge_multiplier"]
    total_fee *= multiplier
    
    # Apply min/max limits
    total_fee = max(total_fee, DELIVERY_CONFIG["min_fee"])
    total_fee = min(total_fee, DELIVERY_CONFIG["max_fee"])
    
    return round(total_fee, 2)


def calculate_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """
    Calculate distance between two points using Haversine formula.
    
    Args:
        lat1, lng1: Restaurant coordinates
        lat2, lng2: Delivery coordinates
        
    Returns:
        Distance in kilometers
    """
    R = 6371  # Earth's radius in kilometers
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lng = math.radians(lng2 - lng1)
    
    a = (math.sin(delta_lat / 2) ** 2 +
         math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lng / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c


def calculate_commission(
    order_total: float,
    subscription_tier: str = "basic",
    custom_rate: Optional[float] = None
) -> float:
    """
    Calculate commission for an order based on subscription tier.
    
    Args:
        order_total: Total order amount
        subscription_tier: Restaurant's subscription tier
        custom_rate: Optional custom commission rate override
        
    Returns:
        Commission amount
    """
    if custom_rate is not None:
        rate = custom_rate
    else:
        tier_config = SUBSCRIPTION_TIERS.get(subscription_tier, SUBSCRIPTION_TIERS["basic"])
        rate = tier_config["commission_rate"]
    
    return round(order_total * rate, 2)


def get_subscription_details(tier: str) -> dict:
    """
    Get details about a subscription tier.
    
    Args:
        tier: Subscription tier name
        
    Returns:
        Tier configuration dictionary
    """
    return SUBSCRIPTION_TIERS.get(tier, SUBSCRIPTION_TIERS["basic"])


def calculate_driver_payout(
    delivery_fee: float,
    tip_amount: float = 0,
    platform_cut: float = None
) -> float:
    """
    Calculate driver payout for a delivery.

    Args:
        delivery_fee: The delivery fee charged
        tip_amount: Optional tip from customer
        platform_cut: Platform's percentage of delivery fee (defaults to settings)

    Returns:
        Total payout to driver
    """
    if platform_cut is None:
        platform_cut = getattr(settings, 'DRIVER_PLATFORM_CUT', 0.20)

    driver_delivery_share = delivery_fee * (1 - platform_cut)
    total_payout = driver_delivery_share + tip_amount
    return round(total_payout, 2)


def calculate_order_totals(
    subtotal: float,
    delivery_distance_km: float,
    subscription_tier: str = "basic",
    tax_rate: float = 0.0,
    tip_amount: float = 0
) -> dict:
    """
    Calculate all order totals including fees, taxes, and commission.
    
    Args:
        subtotal: Order subtotal (sum of items)
        delivery_distance_km: Distance for delivery
        subscription_tier: Restaurant's subscription tier
        tax_rate: Tax rate to apply
        tip_amount: Optional customer tip
        
    Returns:
        Dictionary with all calculated amounts
    """
    # Calculate delivery fee
    delivery_fee = calculate_delivery_fee(delivery_distance_km, subtotal)
    
    # Calculate tax
    tax_amount = round(subtotal * tax_rate, 2)
    
    # Calculate total
    total = subtotal + delivery_fee + tax_amount + tip_amount
    
    # Calculate commission
    commission = calculate_commission(subtotal, subscription_tier)
    
    # Calculate driver payout
    driver_payout = calculate_driver_payout(delivery_fee, tip_amount)
    
    # Restaurant net (after commission)
    restaurant_net = subtotal - commission
    
    return {
        "subtotal": round(subtotal, 2),
        "delivery_fee": delivery_fee,
        "tax_amount": tax_amount,
        "tip_amount": tip_amount,
        "total": round(total, 2),
        "commission": commission,
        "restaurant_net": round(restaurant_net, 2),
        "driver_payout": driver_payout
    }
