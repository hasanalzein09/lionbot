"""
System Health Check API - Monitor system status
"""
from typing import Any
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime
import asyncio

from app.db.session import get_db
from app.services.redis_service import redis_service
from app.models.user import User
from app.api import deps

router = APIRouter()


@router.get("")
async def health_check() -> Any:
    """
    Basic health check endpoint.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "lion-delivery-api",
    }


@router.get("/detailed")
async def detailed_health_check(
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Detailed health check with all services.
    """
    checks = {
        "api": {"status": "healthy", "latency_ms": 0},
        "database": {"status": "unknown", "latency_ms": 0},
        "redis": {"status": "unknown", "latency_ms": 0},
    }
    
    # Check database
    try:
        start = datetime.utcnow()
        await db.execute(text("SELECT 1"))
        latency = (datetime.utcnow() - start).total_seconds() * 1000
        checks["database"] = {"status": "healthy", "latency_ms": round(latency, 2)}
    except Exception as e:
        checks["database"] = {"status": "unhealthy", "error": str(e)}
    
    # Check Redis
    try:
        start = datetime.utcnow()
        await redis_service.set("health_check", "ok", ex=10)
        value = await redis_service.get("health_check")
        latency = (datetime.utcnow() - start).total_seconds() * 1000
        if value == "ok":
            checks["redis"] = {"status": "healthy", "latency_ms": round(latency, 2)}
        else:
            checks["redis"] = {"status": "degraded", "error": "Read mismatch"}
    except Exception as e:
        checks["redis"] = {"status": "unhealthy", "error": str(e)}
    
    # Overall status
    all_healthy = all(c["status"] == "healthy" for c in checks.values())
    any_unhealthy = any(c["status"] == "unhealthy" for c in checks.values())
    
    if all_healthy:
        overall = "healthy"
    elif any_unhealthy:
        overall = "unhealthy"
    else:
        overall = "degraded"
    
    return {
        "status": overall,
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "checks": checks,
    }


@router.get("/metrics")
async def get_metrics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Get system metrics (Admin only).
    """
    from sqlalchemy import func, select
    from app.models.order import Order
    from app.models.restaurant import Restaurant
    from app.models.user import User as UserModel
    
    # Count users by role
    users_result = await db.execute(
        select(UserModel.role, func.count(UserModel.id))
        .group_by(UserModel.role)
    )
    users_by_role = {row[0]: row[1] for row in users_result.all()}
    
    # Total orders
    orders_result = await db.execute(select(func.count(Order.id)))
    total_orders = orders_result.scalar() or 0
    
    # Active restaurants
    restaurants_result = await db.execute(
        select(func.count(Restaurant.id)).where(Restaurant.is_active == True)
    )
    active_restaurants = restaurants_result.scalar() or 0
    
    # Today's orders
    from datetime import date
    today_start = datetime.combine(date.today(), datetime.min.time())
    today_orders_result = await db.execute(
        select(func.count(Order.id)).where(Order.created_at >= today_start)
    )
    today_orders = today_orders_result.scalar() or 0
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "users": {
            "by_role": users_by_role,
            "total": sum(users_by_role.values()),
        },
        "orders": {
            "total": total_orders,
            "today": today_orders,
        },
        "restaurants": {
            "active": active_restaurants,
        },
    }


@router.get("/readiness")
async def readiness_probe(
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Kubernetes readiness probe.
    """
    try:
        await db.execute(text("SELECT 1"))
        return {"ready": True}
    except Exception:
        return {"ready": False}


@router.get("/liveness")
async def liveness_probe() -> Any:
    """
    Kubernetes liveness probe.
    """
    return {"alive": True}
