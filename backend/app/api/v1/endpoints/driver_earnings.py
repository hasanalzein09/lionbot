"""
Driver Earnings API - Track driver earnings and performance
"""
from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timedelta

from app.db.session import get_db
from app.models.user import User, UserRole
from app.models.order import Order, OrderStatus
from app.api import deps

router = APIRouter()


@router.get("/summary")
async def get_earnings_summary(
    days: int = Query(7, ge=1, le=90),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get driver earnings summary.
    """
    if current_user.role != UserRole.DRIVER:
        raise HTTPException(status_code=403, detail="Drivers only")
    
    since = datetime.utcnow() - timedelta(days=days)
    
    # Get delivered orders
    result = await db.execute(
        select(Order).where(
            Order.driver_id == current_user.id,
            Order.status == OrderStatus.DELIVERED,
            Order.created_at >= since
        )
    )
    orders = result.scalars().all()
    
    total_deliveries = len(orders)
    total_earnings = total_deliveries * 3.0  # $3 per delivery
    
    # Get tips
    from app.api.v1.endpoints.tips import Tip
    tips_result = await db.execute(
        select(func.sum(Tip.amount)).where(
            Tip.driver_id == current_user.id,
            Tip.created_at >= since
        )
    )
    total_tips = float(tips_result.scalar() or 0)
    
    return {
        "period_days": days,
        "total_deliveries": total_deliveries,
        "delivery_earnings": round(total_earnings, 2),
        "tips_earned": round(total_tips, 2),
        "total_earnings": round(total_earnings + total_tips, 2),
        "average_per_delivery": round((total_earnings + total_tips) / total_deliveries, 2) if total_deliveries > 0 else 0,
    }


@router.get("/daily")
async def get_daily_earnings(
    days: int = Query(7, ge=1, le=30),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get daily earnings breakdown.
    """
    if current_user.role != UserRole.DRIVER:
        raise HTTPException(status_code=403, detail="Drivers only")
    
    daily_stats = []
    
    for i in range(days - 1, -1, -1):
        date = datetime.utcnow().date() - timedelta(days=i)
        start = datetime.combine(date, datetime.min.time())
        end = datetime.combine(date, datetime.max.time())
        
        # Count deliveries
        result = await db.execute(
            select(func.count(Order.id)).where(
                Order.driver_id == current_user.id,
                Order.status == OrderStatus.DELIVERED,
                Order.created_at >= start,
                Order.created_at <= end
            )
        )
        deliveries = result.scalar() or 0
        earnings = deliveries * 3.0
        
        daily_stats.append({
            "date": date.isoformat(),
            "day": date.strftime("%a"),
            "deliveries": deliveries,
            "earnings": round(earnings, 2),
        })
    
    return {
        "daily_stats": daily_stats,
        "chart_data": {
            "labels": [d["day"] for d in daily_stats],
            "values": [d["earnings"] for d in daily_stats],
        },
    }


@router.get("/performance")
async def get_driver_performance(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get driver performance metrics.
    """
    if current_user.role != UserRole.DRIVER:
        raise HTTPException(status_code=403, detail="Drivers only")
    
    since = datetime.utcnow() - timedelta(days=30)
    
    # Total orders
    total_result = await db.execute(
        select(func.count(Order.id)).where(
            Order.driver_id == current_user.id,
            Order.created_at >= since
        )
    )
    total_orders = total_result.scalar() or 0
    
    # Completed orders
    completed_result = await db.execute(
        select(func.count(Order.id)).where(
            Order.driver_id == current_user.id,
            Order.status == OrderStatus.DELIVERED,
            Order.created_at >= since
        )
    )
    completed_orders = completed_result.scalar() or 0
    
    # Average rating (from reviews)
    from app.api.v1.endpoints.reviews import Review
    rating_result = await db.execute(
        select(func.avg(Review.rating)).where(
            Review.customer_id == current_user.id
        )
    )
    avg_rating = rating_result.scalar()
    
    completion_rate = (completed_orders / total_orders * 100) if total_orders > 0 else 0
    
    return {
        "period_days": 30,
        "total_orders": total_orders,
        "completed_orders": completed_orders,
        "completion_rate": round(completion_rate, 1),
        "average_rating": round(float(avg_rating or 0), 1),
        "status": "excellent" if completion_rate >= 95 else ("good" if completion_rate >= 80 else "needs_improvement"),
    }


@router.get("/leaderboard")
async def get_driver_leaderboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Get driver leaderboard (Admin).
    """
    since = datetime.utcnow() - timedelta(days=7)
    
    # Get all drivers with their delivery counts
    result = await db.execute(
        select(
            Order.driver_id,
            func.count(Order.id).label("deliveries")
        )
        .where(
            Order.status == OrderStatus.DELIVERED,
            Order.created_at >= since,
            Order.driver_id != None
        )
        .group_by(Order.driver_id)
        .order_by(func.count(Order.id).desc())
        .limit(10)
    )
    
    leaderboard = []
    for row in result.all():
        driver_result = await db.execute(
            select(User).where(User.id == row[0])
        )
        driver = driver_result.scalars().first()
        if driver:
            leaderboard.append({
                "rank": len(leaderboard) + 1,
                "driver_id": driver.id,
                "driver_name": driver.full_name,
                "deliveries": row[1],
                "earnings": round(row[1] * 3.0, 2),
            })
    
    return {
        "period": "Last 7 days",
        "leaderboard": leaderboard,
    }
