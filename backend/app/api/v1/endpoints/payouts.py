"""
Restaurant Payouts API - Track restaurant earnings and payouts
"""
from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel
from datetime import datetime, timedelta
from decimal import Decimal

from app.db.session import get_db
from app.models.user import User, UserRole
from app.models.order import Order, OrderStatus
from app.models.restaurant import Restaurant
from app.api import deps

# Model
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, String, Boolean
from app.db.base_class import Base


router = APIRouter()


class Payout(Base):
    __tablename__ = "payouts"
    
    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurant.id"), nullable=False)
    amount = Column(Float, nullable=False)
    commission = Column(Float, default=0)  # Platform commission
    net_amount = Column(Float, nullable=False)
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    status = Column(String(20), default="pending")  # pending, processing, completed
    payment_method = Column(String(50), nullable=True)
    reference_number = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    paid_at = Column(DateTime, nullable=True)


COMMISSION_RATE = 0.15  # 15% platform commission


# ==================== Endpoints ====================

@router.get("/restaurant/{restaurant_id}/summary")
async def get_payout_summary(
    restaurant_id: int,
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get payout summary for a restaurant.
    """
    # Check access
    if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.RESTAURANT_MANAGER]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    since = datetime.utcnow() - timedelta(days=days)
    
    # Get delivered orders
    result = await db.execute(
        select(Order).where(
            Order.restaurant_id == restaurant_id,
            Order.status == OrderStatus.DELIVERED,
            Order.created_at >= since
        )
    )
    orders = result.scalars().all()
    
    total_revenue = sum(float(o.total_amount or 0) for o in orders)
    commission = total_revenue * COMMISSION_RATE
    net_earnings = total_revenue - commission
    
    # Get pending payouts
    payout_result = await db.execute(
        select(Payout).where(
            Payout.restaurant_id == restaurant_id,
            Payout.status == "pending"
        )
    )
    pending_payouts = payout_result.scalars().all()
    pending_amount = sum(p.net_amount for p in pending_payouts)
    
    return {
        "restaurant_id": restaurant_id,
        "period_days": days,
        "total_orders": len(orders),
        "gross_revenue": round(total_revenue, 2),
        "commission_rate": f"{COMMISSION_RATE * 100}%",
        "commission_amount": round(commission, 2),
        "net_earnings": round(net_earnings, 2),
        "pending_payout": round(pending_amount, 2),
    }


@router.get("/restaurant/{restaurant_id}/history")
async def get_payout_history(
    restaurant_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get payout history for a restaurant.
    """
    if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.RESTAURANT_MANAGER]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    result = await db.execute(
        select(Payout)
        .where(Payout.restaurant_id == restaurant_id)
        .order_by(Payout.created_at.desc())
    )
    payouts = result.scalars().all()
    
    return [
        {
            "id": p.id,
            "amount": p.amount,
            "commission": p.commission,
            "net_amount": p.net_amount,
            "period": f"{p.period_start.strftime('%Y-%m-%d')} to {p.period_end.strftime('%Y-%m-%d')}",
            "status": p.status,
            "paid_at": p.paid_at.isoformat() if p.paid_at else None,
        }
        for p in payouts
    ]


@router.post("/generate")
async def generate_payout(
    restaurant_id: int,
    period_days: int = 7,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Generate payout for a restaurant (Admin).
    """
    period_end = datetime.utcnow()
    period_start = period_end - timedelta(days=period_days)
    
    # Get delivered orders in period
    result = await db.execute(
        select(Order).where(
            Order.restaurant_id == restaurant_id,
            Order.status == OrderStatus.DELIVERED,
            Order.created_at >= period_start,
            Order.created_at <= period_end
        )
    )
    orders = result.scalars().all()
    
    if not orders:
        raise HTTPException(status_code=400, detail="No orders in this period")
    
    total = sum(float(o.total_amount or 0) for o in orders)
    commission = total * COMMISSION_RATE
    net = total - commission
    
    payout = Payout(
        restaurant_id=restaurant_id,
        amount=total,
        commission=commission,
        net_amount=net,
        period_start=period_start,
        period_end=period_end,
        status="pending",
    )
    
    db.add(payout)
    await db.commit()
    await db.refresh(payout)
    
    return {
        "message": "Payout generated",
        "payout_id": payout.id,
        "net_amount": round(net, 2),
    }


@router.patch("/{payout_id}/complete")
async def complete_payout(
    payout_id: int,
    reference_number: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Mark payout as completed (Admin).
    """
    result = await db.execute(select(Payout).where(Payout.id == payout_id))
    payout = result.scalars().first()
    
    if not payout:
        raise HTTPException(status_code=404, detail="Payout not found")
    
    payout.status = "completed"
    payout.reference_number = reference_number
    payout.paid_at = datetime.utcnow()
    
    db.add(payout)
    await db.commit()
    
    return {"message": "Payout marked as completed"}
