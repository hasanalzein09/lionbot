"""
Restaurant Analytics API - Insights for restaurant owners
"""
from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import datetime, timedelta

from app.db.session import get_db
from app.models.user import User, UserRole
from app.models.order import Order, OrderStatus
from app.models.restaurant import Restaurant
from app.api import deps

router = APIRouter()


@router.get("/{restaurant_id}/overview")
async def get_restaurant_analytics(
    restaurant_id: int,
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get analytics overview for a restaurant.
    """
    # Verify access (owner or admin)
    if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.RESTAURANT_MANAGER]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    since = datetime.utcnow() - timedelta(days=days)
    
    # Total orders
    orders_result = await db.execute(
        select(func.count(Order.id)).where(
            Order.restaurant_id == restaurant_id,
            Order.created_at >= since
        )
    )
    total_orders = orders_result.scalar() or 0
    
    # Completed orders
    completed_result = await db.execute(
        select(func.count(Order.id)).where(
            Order.restaurant_id == restaurant_id,
            Order.status == OrderStatus.DELIVERED,
            Order.created_at >= since
        )
    )
    completed_orders = completed_result.scalar() or 0
    
    # Cancelled orders
    cancelled_result = await db.execute(
        select(func.count(Order.id)).where(
            Order.restaurant_id == restaurant_id,
            Order.status == OrderStatus.CANCELLED,
            Order.created_at >= since
        )
    )
    cancelled_orders = cancelled_result.scalar() or 0
    
    # Total revenue
    revenue_result = await db.execute(
        select(func.sum(Order.total_amount)).where(
            Order.restaurant_id == restaurant_id,
            Order.status == OrderStatus.DELIVERED,
            Order.created_at >= since
        )
    )
    total_revenue = float(revenue_result.scalar() or 0)
    
    # Average order value
    avg_order = total_revenue / completed_orders if completed_orders > 0 else 0
    
    return {
        "restaurant_id": restaurant_id,
        "period_days": days,
        "total_orders": total_orders,
        "completed_orders": completed_orders,
        "cancelled_orders": cancelled_orders,
        "completion_rate": round(completed_orders / total_orders * 100, 1) if total_orders > 0 else 0,
        "total_revenue": round(total_revenue, 2),
        "average_order_value": round(avg_order, 2),
    }


@router.get("/{restaurant_id}/daily")
async def get_daily_stats(
    restaurant_id: int,
    days: int = Query(7, ge=1, le=30),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get daily stats for charts.
    """
    if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.RESTAURANT_MANAGER]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    stats = []
    
    for i in range(days - 1, -1, -1):
        date = datetime.utcnow().date() - timedelta(days=i)
        start = datetime.combine(date, datetime.min.time())
        end = datetime.combine(date, datetime.max.time())
        
        # Orders count
        count_result = await db.execute(
            select(func.count(Order.id)).where(
                Order.restaurant_id == restaurant_id,
                Order.created_at >= start,
                Order.created_at <= end
            )
        )
        orders = count_result.scalar() or 0
        
        # Revenue
        revenue_result = await db.execute(
            select(func.sum(Order.total_amount)).where(
                Order.restaurant_id == restaurant_id,
                Order.status == OrderStatus.DELIVERED,
                Order.created_at >= start,
                Order.created_at <= end
            )
        )
        revenue = float(revenue_result.scalar() or 0)
        
        stats.append({
            "date": date.isoformat(),
            "day": date.strftime("%a"),
            "orders": orders,
            "revenue": round(revenue, 2),
        })
    
    return {
        "restaurant_id": restaurant_id,
        "daily_stats": stats,
    }


@router.get("/{restaurant_id}/top-items")
async def get_top_items(
    restaurant_id: int,
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get top selling menu items.
    """
    if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.RESTAURANT_MANAGER]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Get recent orders with items
    result = await db.execute(
        select(Order).where(
            Order.restaurant_id == restaurant_id,
            Order.status == OrderStatus.DELIVERED,
            Order.created_at >= datetime.utcnow() - timedelta(days=30)
        )
    )
    orders = result.scalars().all()
    
    # Count item occurrences
    item_counts = {}
    for order in orders:
        if order.items:
            for item in order.items:
                name = item.get('name', 'Unknown')
                qty = item.get('quantity', 1)
                if name in item_counts:
                    item_counts[name]['count'] += qty
                    item_counts[name]['revenue'] += item.get('price', 0) * qty
                else:
                    item_counts[name] = {
                        'name': name,
                        'count': qty,
                        'revenue': item.get('price', 0) * qty,
                    }
    
    # Sort by count
    sorted_items = sorted(item_counts.values(), key=lambda x: x['count'], reverse=True)
    
    return {
        "restaurant_id": restaurant_id,
        "top_items": sorted_items[:limit],
    }


@router.get("/{restaurant_id}/peak-hours")
async def get_peak_hours(
    restaurant_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get busiest hours of the day.
    """
    if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.RESTAURANT_MANAGER]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Get orders from last 30 days
    result = await db.execute(
        select(Order).where(
            Order.restaurant_id == restaurant_id,
            Order.created_at >= datetime.utcnow() - timedelta(days=30)
        )
    )
    orders = result.scalars().all()
    
    # Count by hour
    hour_counts = {h: 0 for h in range(24)}
    for order in orders:
        if order.created_at:
            hour_counts[order.created_at.hour] += 1
    
    # Format response
    peak_hours = [
        {
            "hour": h,
            "display": f"{h:02d}:00",
            "orders": count,
        }
        for h, count in hour_counts.items()
    ]
    
    # Find peak
    max_orders = max(hour_counts.values()) if hour_counts else 0
    peak = [h for h, c in hour_counts.items() if c == max_orders] if max_orders > 0 else []
    
    return {
        "restaurant_id": restaurant_id,
        "hours": peak_hours,
        "peak_hour": peak[0] if peak else None,
        "peak_orders": max_orders,
    }
