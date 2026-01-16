"""
Live Driver Tracking API - Real-time driver location for customers
"""
from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta

from app.db.session import get_db
from app.models.user import User, UserRole
from app.models.order import Order, OrderStatus
from app.api import deps
from app.services.redis_service import redis_service
import json

router = APIRouter()


@router.get("/order/{order_id}")
async def get_driver_location_for_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get live driver location for an order (for customers).
    """
    result = await db.execute(
        select(Order).where(
            Order.id == order_id,
            Order.customer_phone == current_user.phone_number
        )
    )
    order = result.scalars().first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.status not in [OrderStatus.OUT_FOR_DELIVERY, OrderStatus.READY]:
        return {
            "tracking_available": False,
            "message": "Driver not yet on the way",
            "order_status": order.status.value if hasattr(order.status, 'value') else order.status,
        }
    
    if not order.driver_id:
        return {
            "tracking_available": False,
            "message": "No driver assigned yet",
        }
    
    # Get driver info
    driver_result = await db.execute(
        select(User).where(User.id == order.driver_id)
    )
    driver = driver_result.scalars().first()
    
    if not driver:
        return {"tracking_available": False, "message": "Driver not found"}
    
    # Get latest location from Redis (updated frequently by driver app)
    location_key = f"driver_location:{driver.id}"
    location_data = await redis_service.get(location_key)
    
    if location_data:
        location = json.loads(location_data)
    else:
        # Fallback to database
        location = {
            "latitude": driver.last_latitude,
            "longitude": driver.last_longitude,
            "updated_at": None,
        }
    
    return {
        "tracking_available": True,
        "order_id": order_id,
        "driver": {
            "id": driver.id,
            "name": driver.full_name,
            "phone": driver.phone_number,
        },
        "location": {
            "latitude": location.get("latitude"),
            "longitude": location.get("longitude"),
            "heading": location.get("heading"),  # Direction
            "speed": location.get("speed"),
            "updated_at": location.get("updated_at"),
        },
        "eta_minutes": calculate_eta(location, order),
    }


@router.post("/update")
async def update_driver_location(
    latitude: float,
    longitude: float,
    heading: float = None,
    speed: float = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Update driver's current location (called by driver app).
    """
    if current_user.role != UserRole.DRIVER:
        raise HTTPException(status_code=403, detail="Drivers only")
    
    # Store in Redis for real-time access
    location_key = f"driver_location:{current_user.id}"
    location_data = {
        "latitude": latitude,
        "longitude": longitude,
        "heading": heading,
        "speed": speed,
        "updated_at": datetime.utcnow().isoformat(),
    }
    
    await redis_service.set(location_key, json.dumps(location_data), ex=300)  # 5 min expiry
    
    # Also update database occasionally
    current_user.last_latitude = latitude
    current_user.last_longitude = longitude
    db.add(current_user)
    await db.commit()
    
    return {"message": "Location updated"}


@router.get("/nearby-drivers")
async def get_nearby_drivers(
    latitude: float,
    longitude: float,
    radius_km: float = 5,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Get nearby available drivers (Admin only).
    """
    result = await db.execute(
        select(User).where(
            User.role == UserRole.DRIVER,
            User.is_active == True
        )
    )
    drivers = result.scalars().all()
    
    from math import radians, sin, cos, sqrt, atan2
    
    def calculate_distance(lat1, lon1, lat2, lon2):
        R = 6371
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        return R * c
    
    nearby = []
    for driver in drivers:
        if driver.last_latitude and driver.last_longitude:
            distance = calculate_distance(
                latitude, longitude,
                driver.last_latitude, driver.last_longitude
            )
            if distance <= radius_km:
                nearby.append({
                    "id": driver.id,
                    "name": driver.full_name,
                    "distance_km": round(distance, 2),
                    "latitude": driver.last_latitude,
                    "longitude": driver.last_longitude,
                })
    
    nearby.sort(key=lambda x: x["distance_km"])
    
    return {
        "count": len(nearby),
        "drivers": nearby,
    }


def calculate_eta(location: dict, order: Order) -> int:
    """
    Calculate estimated time of arrival in minutes.
    """
    # Simple estimation based on average speed
    # In production, would use Google Maps Distance Matrix API
    if not location.get("latitude") or not location.get("longitude"):
        return 15  # Default
    
    speed = location.get("speed", 30)  # km/h default
    if speed < 5:
        speed = 30  # Probably stopped
    
    # Estimate remaining distance (would need actual destination coords)
    remaining_km = 2  # Placeholder
    
    eta = int((remaining_km / speed) * 60)  # Convert to minutes
    return max(5, min(eta, 60))  # Clamp between 5-60 minutes
