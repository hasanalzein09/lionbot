"""
Reorder Functionality - Quick reorder from previous orders
"""
from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import json

from app.db.session import get_db
from app.models.user import User
from app.models.order import Order
from app.api import deps
from app.services.redis_service import redis_service

router = APIRouter()


@router.post("/{order_id}")
async def reorder(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Add items from a previous order to cart (reorder).
    """
    # Get the original order
    result = await db.execute(
        select(Order).where(
            Order.id == order_id,
            Order.customer_phone == current_user.phone_number
        )
    )
    order = result.scalars().first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if not order.items:
        raise HTTPException(status_code=400, detail="Order has no items")
    
    # Clear current cart
    cart_key = f"cart:{current_user.id}"
    await redis_service.delete(cart_key)
    
    # Create new cart from order items
    cart = {
        "restaurant_id": order.restaurant_id,
        "restaurant_name": order.restaurant.name if order.restaurant else "Unknown",
        "items": order.items if isinstance(order.items, list) else [],
    }
    
    # Save cart with 24h expiration
    await redis_service.set(cart_key, json.dumps(cart), ex=86400)
    
    return {
        "message": "Items added to cart",
        "cart_items": len(cart["items"]),
        "restaurant_id": order.restaurant_id,
    }


@router.get("/last")
async def get_last_orders(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
    limit: int = 5,
) -> Any:
    """
    Get last orders for quick reorder.
    """
    result = await db.execute(
        select(Order)
        .where(Order.customer_phone == current_user.phone_number)
        .order_by(Order.created_at.desc())
        .limit(limit)
    )
    orders = result.scalars().all()
    
    return [
        {
            "id": o.id,
            "restaurant_name": o.restaurant.name if o.restaurant else "Unknown",
            "restaurant_id": o.restaurant_id,
            "total_amount": float(o.total_amount) if o.total_amount else 0,
            "items_count": len(o.items) if o.items else 0,
            "created_at": o.created_at.isoformat() if o.created_at else None,
        }
        for o in orders
    ]
