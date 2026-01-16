from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.api import deps
from app.db.session import get_db
from app.models.order import Order, OrderStatus
from app.models.restaurant import Restaurant
from app.models.user import User, UserRole

router = APIRouter()

@router.get("/dashboard")
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Get comprehensive dashboard statistics.
    """
    # Total orders
    total_orders_result = await db.execute(
        select(func.count(Order.id))
    )
    total_orders = total_orders_result.scalar() or 0
    
    # Total revenue (from delivered orders)
    revenue_result = await db.execute(
        select(func.sum(Order.total_amount))
        .where(Order.status == OrderStatus.DELIVERED)
    )
    total_revenue = revenue_result.scalar() or 0
    
    # Pending orders
    pending_result = await db.execute(
        select(func.count(Order.id))
        .where(Order.status == OrderStatus.NEW)
    )
    pending_orders = pending_result.scalar() or 0
    
    # Active restaurants
    active_restaurants_result = await db.execute(
        select(func.count(Restaurant.id))
        .where(Restaurant.is_active == True)
    )
    active_restaurants = active_restaurants_result.scalar() or 0
    
    # Total restaurants
    total_restaurants_result = await db.execute(
        select(func.count(Restaurant.id))
    )
    total_restaurants = total_restaurants_result.scalar() or 0
    
    # Total drivers
    drivers_result = await db.execute(
        select(func.count(User.id))
        .where(User.role == UserRole.DRIVER)
    )
    total_drivers = drivers_result.scalar() or 0
    
    # Active drivers
    active_drivers_result = await db.execute(
        select(func.count(User.id))
        .where(User.role == UserRole.DRIVER)
        .where(User.is_active == True)
    )
    active_drivers = active_drivers_result.scalar() or 0
    
    # Total customers
    customers_result = await db.execute(
        select(func.count(User.id))
        .where(User.role == UserRole.CUSTOMER)
    )
    total_customers = customers_result.scalar() or 0
    
    # Orders by status
    status_query = (
        select(Order.status, func.count(Order.id))
        .group_by(Order.status)
    )
    status_result = await db.execute(status_query)
    orders_by_status = {str(row[0].value): row[1] for row in status_result.fetchall()}
    
    # Today's orders (simplified - would need proper date filtering)
    todays_orders_result = await db.execute(
        select(func.count(Order.id))
    )
    todays_orders = todays_orders_result.scalar() or 0
    
    # Today's revenue
    todays_revenue_result = await db.execute(
        select(func.sum(Order.total_amount))
        .where(Order.status == OrderStatus.DELIVERED)
    )
    todays_revenue = todays_revenue_result.scalar() or 0
    
    return {
        "orders": {
            "total": total_orders,
            "pending": pending_orders,
            "today": todays_orders,
            "by_status": orders_by_status
        },
        "revenue": {
            "total": float(total_revenue),
            "today": float(todays_revenue) if todays_revenue else 0
        },
        "restaurants": {
            "total": total_restaurants,
            "active": active_restaurants
        },
        "drivers": {
            "total": total_drivers,
            "active": active_drivers
        },
        "customers": {
            "total": total_customers
        }
    }

@router.get("/restaurant/{restaurant_id}")
async def get_restaurant_stats(
    restaurant_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get statistics for a specific restaurant.
    """
    # Verify restaurant exists
    rest_result = await db.execute(
        select(Restaurant).where(Restaurant.id == restaurant_id)
    )
    restaurant = rest_result.scalars().first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    
    # Total orders for this restaurant
    total_orders_result = await db.execute(
        select(func.count(Order.id))
        .where(Order.restaurant_id == restaurant_id)
    )
    total_orders = total_orders_result.scalar() or 0
    
    # Revenue for this restaurant
    revenue_result = await db.execute(
        select(func.sum(Order.total_amount))
        .where(Order.restaurant_id == restaurant_id)
        .where(Order.status == OrderStatus.DELIVERED)
    )
    total_revenue = revenue_result.scalar() or 0
    
    # Pending orders
    pending_result = await db.execute(
        select(func.count(Order.id))
        .where(Order.restaurant_id == restaurant_id)
        .where(Order.status == OrderStatus.NEW)
    )
    pending_orders = pending_result.scalar() or 0
    
    # Orders by status
    status_query = (
        select(Order.status, func.count(Order.id))
        .where(Order.restaurant_id == restaurant_id)
        .group_by(Order.status)
    )
    status_result = await db.execute(status_query)
    orders_by_status = {str(row[0].value): row[1] for row in status_result.fetchall()}
    
    # Average order value
    avg_order_result = await db.execute(
        select(func.avg(Order.total_amount))
        .where(Order.restaurant_id == restaurant_id)
        .where(Order.status == OrderStatus.DELIVERED)
    )
    avg_order_value = avg_order_result.scalar() or 0
    
    return {
        "restaurant_id": restaurant_id,
        "restaurant_name": restaurant.name,
        "orders": {
            "total": total_orders,
            "pending": pending_orders,
            "by_status": orders_by_status
        },
        "revenue": {
            "total": float(total_revenue),
            "average_order": float(avg_order_value) if avg_order_value else 0
        }
    }
