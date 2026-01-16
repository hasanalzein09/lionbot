"""
Order Scheduling - Schedule orders for later delivery
"""
from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from datetime import datetime, timedelta
import json

from app.db.session import get_db
from app.models.user import User
from app.models.order import Order, OrderStatus
from app.models.restaurant import Restaurant
from app.api import deps
from app.services.redis_service import redis_service

router = APIRouter()


class ScheduleOrder(BaseModel):
    scheduled_time: datetime
    notes: Optional[str] = None


@router.post("/schedule")
async def schedule_order(
    schedule: ScheduleOrder,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Schedule cart items for later delivery.
    """
    # Get cart
    cart_key = f"cart:{current_user.id}"
    cart_data = await redis_service.get(cart_key)
    
    if not cart_data:
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    cart = json.loads(cart_data)
    
    if not cart.get('items'):
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    # Validate scheduled time
    now = datetime.utcnow()
    min_time = now + timedelta(hours=1)
    max_time = now + timedelta(days=7)
    
    if schedule.scheduled_time < min_time:
        raise HTTPException(
            status_code=400, 
            detail="Scheduled time must be at least 1 hour from now"
        )
    
    if schedule.scheduled_time > max_time:
        raise HTTPException(
            status_code=400,
            detail="Cannot schedule more than 7 days in advance"
        )
    
    # Check restaurant is open at scheduled time
    result = await db.execute(
        select(Restaurant).where(Restaurant.id == cart['restaurant_id'])
    )
    restaurant = result.scalars().first()
    
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    
    # Calculate total
    subtotal = sum(item['price'] * item['quantity'] for item in cart['items'])
    delivery_fee = 2.0
    total = subtotal + delivery_fee
    
    # Create scheduled order
    order = Order(
        restaurant_id=cart['restaurant_id'],
        customer_phone=current_user.phone_number,
        customer_name=current_user.full_name,
        delivery_address=current_user.address or "Not specified",
        total_amount=total,
        status=OrderStatus.PENDING,
        items=cart['items'],
        notes=f"SCHEDULED FOR: {schedule.scheduled_time.isoformat()}. {schedule.notes or ''}",
        scheduled_time=schedule.scheduled_time,
    )
    
    db.add(order)
    await db.commit()
    await db.refresh(order)
    
    # Clear cart
    await redis_service.delete(cart_key)
    
    return {
        "message": "Order scheduled successfully",
        "order_id": order.id,
        "scheduled_time": schedule.scheduled_time.isoformat(),
        "total": total,
    }


@router.get("/available-slots")
async def get_available_slots(
    restaurant_id: int,
    date: Optional[str] = Query(None, description="YYYY-MM-DD"),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get available delivery time slots for a restaurant.
    """
    if date:
        try:
            target_date = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    else:
        target_date = datetime.utcnow()
    
    # Generate time slots (every 30 minutes from 10am to 10pm)
    slots = []
    start_hour = 10
    end_hour = 22
    
    for hour in range(start_hour, end_hour):
        for minute in [0, 30]:
            slot_time = target_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            # Skip past times
            if slot_time <= datetime.utcnow() + timedelta(hours=1):
                continue
            
            slots.append({
                "time": slot_time.strftime("%H:%M"),
                "display": slot_time.strftime("%I:%M %p"),
                "datetime": slot_time.isoformat(),
                "available": True,  # Would check capacity in production
            })
    
    return {
        "date": target_date.strftime("%Y-%m-%d"),
        "restaurant_id": restaurant_id,
        "slots": slots,
    }
