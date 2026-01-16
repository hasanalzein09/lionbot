"""
Driver Tips API - Tip drivers after delivery
"""
from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel, Field
from datetime import datetime

from app.db.session import get_db
from app.models.user import User, UserRole
from app.models.order import Order, OrderStatus
from app.api import deps

# Model
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, String
from app.db.base_class import Base


router = APIRouter()


class Tip(Base):
    __tablename__ = "tips"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("order.id"), unique=True)
    driver_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    amount = Column(Float, nullable=False)
    message = Column(String(200), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class TipCreate(BaseModel):
    order_id: int
    amount: float = Field(..., gt=0, le=100)
    message: Optional[str] = None


# ==================== Endpoints ====================

@router.post("")
async def add_tip(
    tip_in: TipCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Add tip for driver after delivery.
    """
    # Get order
    result = await db.execute(
        select(Order).where(
            Order.id == tip_in.order_id,
            Order.customer_phone == current_user.phone_number
        )
    )
    order = result.scalars().first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.status != OrderStatus.DELIVERED:
        raise HTTPException(status_code=400, detail="Can only tip delivered orders")
    
    if not order.driver_id:
        raise HTTPException(status_code=400, detail="No driver assigned to this order")
    
    # Check if already tipped
    existing = await db.execute(
        select(Tip).where(Tip.order_id == tip_in.order_id)
    )
    if existing.scalars().first():
        raise HTTPException(status_code=400, detail="Already tipped this order")
    
    tip = Tip(
        order_id=tip_in.order_id,
        driver_id=order.driver_id,
        customer_id=current_user.id,
        amount=tip_in.amount,
        message=tip_in.message,
    )
    
    db.add(tip)
    await db.commit()
    
    # TODO: Send notification to driver
    
    return {
        "message": "Thank you for the tip!",
        "amount": tip_in.amount,
    }


@router.get("/driver/earnings")
async def get_driver_tips(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get driver's tip earnings.
    """
    if current_user.role != UserRole.DRIVER:
        raise HTTPException(status_code=403, detail="Drivers only")
    
    # Total tips
    result = await db.execute(
        select(func.sum(Tip.amount), func.count(Tip.id)).where(
            Tip.driver_id == current_user.id
        )
    )
    row = result.first()
    total_amount = float(row[0] or 0)
    total_count = row[1] or 0
    
    # Recent tips
    recent = await db.execute(
        select(Tip).where(
            Tip.driver_id == current_user.id
        ).order_by(Tip.created_at.desc()).limit(10)
    )
    tips = recent.scalars().all()
    
    return {
        "total_tips": total_count,
        "total_amount": round(total_amount, 2),
        "average_tip": round(total_amount / total_count, 2) if total_count > 0 else 0,
        "recent_tips": [
            {
                "order_id": t.order_id,
                "amount": t.amount,
                "message": t.message,
                "date": t.created_at.isoformat() if t.created_at else None,
            }
            for t in tips
        ],
    }


@router.get("/suggested-amounts")
async def get_suggested_tips(
    order_total: float = 0,
) -> Any:
    """
    Get suggested tip amounts.
    """
    base_tips = [1, 2, 3, 5]
    
    if order_total > 0:
        # Percentage-based suggestions
        suggestions = [
            {"amount": round(order_total * 0.10, 2), "label": "10%"},
            {"amount": round(order_total * 0.15, 2), "label": "15%"},
            {"amount": round(order_total * 0.20, 2), "label": "20%"},
        ]
    else:
        suggestions = [
            {"amount": a, "label": f"${a}"}
            for a in base_tips
        ]
    
    return {
        "suggestions": suggestions,
        "custom_allowed": True,
        "max_amount": 100,
    }
