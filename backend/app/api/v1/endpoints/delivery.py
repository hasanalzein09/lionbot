"""
Delivery Time Estimation Service
"""
from typing import Any, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from math import radians, sin, cos, sqrt, atan2

from app.db.session import get_db
from app.models.restaurant import Restaurant

router = APIRouter()


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two points using Haversine formula.
    Returns distance in kilometers.
    """
    R = 6371  # Earth's radius in kilometers
    
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    return R * c


def estimate_delivery_time(distance_km: float, is_peak_hour: bool = False) -> dict:
    """
    Estimate delivery time based on distance.
    """
    # Base preparation time (minutes)
    prep_time = 15
    
    # Delivery time based on distance
    if distance_km <= 2:
        delivery_time = 10
    elif distance_km <= 5:
        delivery_time = 20
    elif distance_km <= 10:
        delivery_time = 35
    else:
        delivery_time = 45 + int((distance_km - 10) * 3)
    
    # Peak hour adjustment
    if is_peak_hour:
        prep_time += 10
        delivery_time += 10
    
    total_min = prep_time + delivery_time
    total_max = total_min + 15
    
    return {
        "prep_time_min": prep_time,
        "delivery_time_min": delivery_time,
        "total_min": total_min,
        "total_max": total_max,
        "display": f"{total_min}-{total_max} min",
    }


def calculate_delivery_fee(distance_km: float, order_total: float = 0) -> dict:
    """
    Calculate delivery fee based on distance.
    """
    base_fee = 2.0
    per_km_fee = 0.5
    free_threshold = 50.0
    
    if order_total >= free_threshold:
        return {
            "fee": 0.0,
            "is_free": True,
            "reason": f"Free delivery on orders over ${free_threshold}",
        }
    
    if distance_km <= 3:
        fee = base_fee
    else:
        fee = base_fee + (distance_km - 3) * per_km_fee
    
    fee = round(min(fee, 10.0), 2)  # Max fee cap
    
    return {
        "fee": fee,
        "is_free": False,
        "free_threshold": free_threshold,
    }


@router.get("/estimate")
async def get_delivery_estimate(
    restaurant_id: int,
    customer_lat: float = Query(..., description="Customer latitude"),
    customer_lon: float = Query(..., description="Customer longitude"),
    order_total: float = Query(0, description="Order total for free delivery check"),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get delivery time and fee estimate.
    """
    result = await db.execute(
        select(Restaurant).where(Restaurant.id == restaurant_id)
    )
    restaurant = result.scalars().first()
    
    if not restaurant:
        return {
            "error": "Restaurant not found",
            "time": {"display": "30-45 min"},
            "fee": {"fee": 2.0, "is_free": False},
            "distance_km": None,
        }
    
    # Use restaurant location or default
    rest_lat = getattr(restaurant, 'latitude', 33.8938)  # Default: Beirut
    rest_lon = getattr(restaurant, 'longitude', 35.5018)
    
    distance = calculate_distance(rest_lat, rest_lon, customer_lat, customer_lon)
    
    # Check if within delivery range (15km default)
    max_distance = 15.0
    if distance > max_distance:
        return {
            "error": "Outside delivery range",
            "max_distance_km": max_distance,
            "distance_km": round(distance, 2),
        }
    
    # Check if peak hour (12-2pm or 7-9pm)
    from datetime import datetime
    now = datetime.now()
    is_peak = now.hour in [12, 13, 19, 20]
    
    time_estimate = estimate_delivery_time(distance, is_peak)
    fee_info = calculate_delivery_fee(distance, order_total)
    
    return {
        "restaurant_id": restaurant_id,
        "restaurant_name": restaurant.name,
        "distance_km": round(distance, 2),
        "time": time_estimate,
        "fee": fee_info,
        "is_peak_hour": is_peak,
    }


@router.get("/nearby")
async def get_nearby_restaurants(
    lat: float = Query(..., description="Customer latitude"),
    lon: float = Query(..., description="Customer longitude"),
    radius_km: float = Query(5, description="Search radius in km"),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get restaurants within delivery radius.
    """
    result = await db.execute(
        select(Restaurant).where(Restaurant.is_active == True)
    )
    restaurants = result.scalars().all()
    
    nearby = []
    for r in restaurants:
        # Use restaurant location or default
        rest_lat = getattr(r, 'latitude', 33.8938)
        rest_lon = getattr(r, 'longitude', 35.5018)
        
        distance = calculate_distance(rest_lat, rest_lon, lat, lon)
        
        if distance <= radius_km:
            time_estimate = estimate_delivery_time(distance)
            nearby.append({
                "id": r.id,
                "name": r.name,
                "category": r.category,
                "distance_km": round(distance, 2),
                "delivery_time": time_estimate["display"],
                "delivery_fee": calculate_delivery_fee(distance)["fee"],
            })
    
    # Sort by distance
    nearby.sort(key=lambda x: x["distance_km"])
    
    return {
        "location": {"lat": lat, "lon": lon},
        "radius_km": radius_km,
        "count": len(nearby),
        "restaurants": nearby,
    }
