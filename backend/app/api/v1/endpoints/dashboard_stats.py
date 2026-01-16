"""
Admin Dashboard Stats API - Comprehensive admin statistics
"""
from typing import Any, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timedelta

from app.db.session import get_db
from app.models.user import User, UserRole
from app.models.order import Order, OrderStatus
from app.models.restaurant import Restaurant
from app.api import deps

router = APIRouter()


@router.get("/overview")
async def get_dashboard_overview(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Get admin dashboard overview stats.
    """
    today = datetime.utcnow().date()
    today_start = datetime.combine(today, datetime.min.time())
    week_ago = datetime.utcnow() - timedelta(days=7)
    month_ago = datetime.utcnow() - timedelta(days=30)
    
    # Today's stats
    today_orders = await db.execute(
        select(func.count(Order.id)).where(Order.created_at >= today_start)
    )
    today_revenue = await db.execute(
        select(func.sum(Order.total_amount)).where(
            Order.created_at >= today_start,
            Order.status == OrderStatus.DELIVERED
        )
    )
    
    # Weekly stats
    week_orders = await db.execute(
        select(func.count(Order.id)).where(Order.created_at >= week_ago)
    )
    week_revenue = await db.execute(
        select(func.sum(Order.total_amount)).where(
            Order.created_at >= week_ago,
            Order.status == OrderStatus.DELIVERED
        )
    )
    
    # User counts
    total_customers = await db.execute(
        select(func.count(User.id)).where(User.role == UserRole.CUSTOMER)
    )
    total_drivers = await db.execute(
        select(func.count(User.id)).where(User.role == UserRole.DRIVER)
    )
    active_restaurants = await db.execute(
        select(func.count(Restaurant.id)).where(Restaurant.is_active == True)
    )
    
    # New users this week
    new_users = await db.execute(
        select(func.count(User.id)).where(User.created_at >= week_ago)
    )
    
    return {
        "today": {
            "orders": today_orders.scalar() or 0,
            "revenue": float(today_revenue.scalar() or 0),
        },
        "this_week": {
            "orders": week_orders.scalar() or 0,
            "revenue": float(week_revenue.scalar() or 0),
            "new_users": new_users.scalar() or 0,
        },
        "totals": {
            "customers": total_customers.scalar() or 0,
            "drivers": total_drivers.scalar() or 0,
            "restaurants": active_restaurants.scalar() or 0,
        },
    }


@router.get("/orders-chart")
async def get_orders_chart_data(
    days: int = Query(7, ge=1, le=30),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Get orders chart data for dashboard.
    """
    data = []
    
    for i in range(days - 1, -1, -1):
        date = datetime.utcnow().date() - timedelta(days=i)
        start = datetime.combine(date, datetime.min.time())
        end = datetime.combine(date, datetime.max.time())
        
        count = await db.execute(
            select(func.count(Order.id)).where(
                Order.created_at >= start,
                Order.created_at <= end
            )
        )
        revenue = await db.execute(
            select(func.sum(Order.total_amount)).where(
                Order.created_at >= start,
                Order.created_at <= end,
                Order.status == OrderStatus.DELIVERED
            )
        )
        
        data.append({
            "date": date.isoformat(),
            "label": date.strftime("%a"),
            "orders": count.scalar() or 0,
            "revenue": float(revenue.scalar() or 0),
        })
    
    return {
        "chart_data": data,
        "labels": [d["label"] for d in data],
        "orders_series": [d["orders"] for d in data],
        "revenue_series": [d["revenue"] for d in data],
    }


@router.get("/live")
async def get_live_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Get real-time platform stats.
    """
    # Active orders (not delivered/cancelled)
    active_orders = await db.execute(
        select(func.count(Order.id)).where(
            Order.status.notin_([OrderStatus.DELIVERED, OrderStatus.CANCELLED])
        )
    )
    
    # Orders by status
    pending = await db.execute(
        select(func.count(Order.id)).where(Order.status == OrderStatus.PENDING)
    )
    preparing = await db.execute(
        select(func.count(Order.id)).where(Order.status == OrderStatus.PREPARING)
    )
    out_for_delivery = await db.execute(
        select(func.count(Order.id)).where(Order.status == OrderStatus.OUT_FOR_DELIVERY)
    )
    
    # Online drivers (updated location in last 10 min)
    from app.services.redis_service import redis_service
    # Would scan Redis for active driver locations
    online_drivers = 5  # Placeholder
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "active_orders": active_orders.scalar() or 0,
        "by_status": {
            "pending": pending.scalar() or 0,
            "preparing": preparing.scalar() or 0,
            "out_for_delivery": out_for_delivery.scalar() or 0,
        },
        "online_drivers": online_drivers,
    }


@router.get("/top-restaurants")
async def get_top_restaurants(
    days: int = Query(7, ge=1, le=30),
    limit: int = Query(5, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Get top performing restaurants.
    """
    since = datetime.utcnow() - timedelta(days=days)
    
    result = await db.execute(
        select(
            Order.restaurant_id,
            func.count(Order.id).label("orders"),
            func.sum(Order.total_amount).label("revenue")
        )
        .where(
            Order.status == OrderStatus.DELIVERED,
            Order.created_at >= since
        )
        .group_by(Order.restaurant_id)
        .order_by(func.sum(Order.total_amount).desc())
        .limit(limit)
    )
    
    top_restaurants = []
    for row in result.all():
        rest = await db.execute(
            select(Restaurant).where(Restaurant.id == row[0])
        )
        restaurant = rest.scalars().first()
        if restaurant:
            top_restaurants.append({
                "id": restaurant.id,
                "name": restaurant.name,
                "orders": row[1],
                "revenue": float(row[2] or 0),
            })
    
    return {
        "period_days": days,
        "restaurants": top_restaurants,
    }


@router.get("/growth")
async def get_growth_metrics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Get growth metrics comparing periods.
    """
    now = datetime.utcnow()
    this_week = now - timedelta(days=7)
    last_week_start = this_week - timedelta(days=7)
    
    # This week
    this_week_orders = await db.execute(
        select(func.count(Order.id)).where(Order.created_at >= this_week)
    )
    this_week_users = await db.execute(
        select(func.count(User.id)).where(User.created_at >= this_week)
    )
    
    # Last week
    last_week_orders = await db.execute(
        select(func.count(Order.id)).where(
            Order.created_at >= last_week_start,
            Order.created_at < this_week
        )
    )
    last_week_users = await db.execute(
        select(func.count(User.id)).where(
            User.created_at >= last_week_start,
            User.created_at < this_week
        )
    )
    
    tw_orders = this_week_orders.scalar() or 0
    lw_orders = last_week_orders.scalar() or 0
    tw_users = this_week_users.scalar() or 0
    lw_users = last_week_users.scalar() or 0
    
    orders_growth = ((tw_orders - lw_orders) / lw_orders * 100) if lw_orders > 0 else 0
    users_growth = ((tw_users - lw_users) / lw_users * 100) if lw_users > 0 else 0
    
    return {
        "orders": {
            "this_week": tw_orders,
            "last_week": lw_orders,
            "growth_percent": round(orders_growth, 1),
            "trend": "up" if orders_growth > 0 else ("down" if orders_growth < 0 else "stable"),
        },
        "users": {
            "this_week": tw_users,
            "last_week": lw_users,
            "growth_percent": round(users_growth, 1),
            "trend": "up" if users_growth > 0 else ("down" if users_growth < 0 else "stable"),
        },
    }
