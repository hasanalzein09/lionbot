"""
Promo Codes & Coupons System
"""
from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal

from app.db.session import get_db
from app.models.user import User
from app.api import deps

# Model
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from app.db.base_class import Base


router = APIRouter()


class Coupon(Base):
    __tablename__ = "coupons"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(String(200))
    discount_type = Column(String(20), default="percentage")  # percentage, fixed
    discount_value = Column(Float, nullable=False)
    min_order_amount = Column(Float, default=0)
    max_discount = Column(Float, nullable=True)  # For percentage discounts
    usage_limit = Column(Integer, nullable=True)  # Total uses allowed
    used_count = Column(Integer, default=0)
    per_user_limit = Column(Integer, default=1)
    restaurant_id = Column(Integer, ForeignKey("restaurant.id"), nullable=True)  # Null = all restaurants
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class CouponUsage(Base):
    __tablename__ = "coupon_usages"
    
    id = Column(Integer, primary_key=True, index=True)
    coupon_id = Column(Integer, ForeignKey("coupons.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    order_id = Column(Integer, ForeignKey("order.id"), nullable=True)
    used_at = Column(DateTime, default=datetime.utcnow)


# ==================== Schemas ====================

class CouponCreate(BaseModel):
    code: str
    description: Optional[str] = None
    discount_type: str = "percentage"
    discount_value: float
    min_order_amount: float = 0
    max_discount: Optional[float] = None
    usage_limit: Optional[int] = None
    per_user_limit: int = 1
    restaurant_id: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class CouponValidate(BaseModel):
    code: str
    order_total: float
    restaurant_id: int


# ==================== Endpoints ====================

@router.post("/validate")
async def validate_coupon(
    data: CouponValidate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Validate a coupon code and calculate discount.
    """
    result = await db.execute(
        select(Coupon).where(Coupon.code == data.code.upper())
    )
    coupon = result.scalars().first()
    
    if not coupon:
        raise HTTPException(status_code=404, detail="Invalid coupon code")
    
    if not coupon.is_active:
        raise HTTPException(status_code=400, detail="Coupon is not active")
    
    now = datetime.utcnow()
    
    if coupon.start_date and now < coupon.start_date:
        raise HTTPException(status_code=400, detail="Coupon not yet valid")
    
    if coupon.end_date and now > coupon.end_date:
        raise HTTPException(status_code=400, detail="Coupon has expired")
    
    if coupon.usage_limit and coupon.used_count >= coupon.usage_limit:
        raise HTTPException(status_code=400, detail="Coupon usage limit reached")
    
    if coupon.min_order_amount and data.order_total < coupon.min_order_amount:
        raise HTTPException(
            status_code=400, 
            detail=f"Minimum order amount is ${coupon.min_order_amount}"
        )
    
    if coupon.restaurant_id and coupon.restaurant_id != data.restaurant_id:
        raise HTTPException(status_code=400, detail="Coupon not valid for this restaurant")
    
    # Check per-user limit
    usage_result = await db.execute(
        select(CouponUsage).where(
            CouponUsage.coupon_id == coupon.id,
            CouponUsage.user_id == current_user.id
        )
    )
    user_usage_count = len(usage_result.scalars().all())
    
    if user_usage_count >= coupon.per_user_limit:
        raise HTTPException(status_code=400, detail="You have already used this coupon")
    
    # Calculate discount
    if coupon.discount_type == "percentage":
        discount = data.order_total * (coupon.discount_value / 100)
        if coupon.max_discount:
            discount = min(discount, coupon.max_discount)
    else:
        discount = coupon.discount_value
    
    discount = min(discount, data.order_total)  # Can't exceed order total
    
    return {
        "valid": True,
        "code": coupon.code,
        "description": coupon.description,
        "discount_type": coupon.discount_type,
        "discount_value": coupon.discount_value,
        "discount_amount": round(discount, 2),
        "new_total": round(data.order_total - discount, 2),
    }


@router.post("/apply/{order_id}")
async def apply_coupon_to_order(
    order_id: int,
    code: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Apply coupon to an order (internal use).
    """
    from app.models.order import Order
    
    result = await db.execute(
        select(Coupon).where(Coupon.code == code.upper())
    )
    coupon = result.scalars().first()
    
    if not coupon:
        raise HTTPException(status_code=404, detail="Invalid coupon")
    
    # Record usage
    usage = CouponUsage(
        coupon_id=coupon.id,
        user_id=current_user.id,
        order_id=order_id,
    )
    db.add(usage)
    
    coupon.used_count += 1
    db.add(coupon)
    
    await db.commit()
    
    return {"message": "Coupon applied"}


# Admin endpoints
@router.post("", status_code=201)
async def create_coupon(
    coupon_in: CouponCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Create a new coupon (Admin only).
    """
    coupon = Coupon(
        code=coupon_in.code.upper(),
        description=coupon_in.description,
        discount_type=coupon_in.discount_type,
        discount_value=coupon_in.discount_value,
        min_order_amount=coupon_in.min_order_amount,
        max_discount=coupon_in.max_discount,
        usage_limit=coupon_in.usage_limit,
        per_user_limit=coupon_in.per_user_limit,
        restaurant_id=coupon_in.restaurant_id,
        start_date=coupon_in.start_date,
        end_date=coupon_in.end_date,
    )
    
    db.add(coupon)
    await db.commit()
    await db.refresh(coupon)
    
    return {"message": "Coupon created", "coupon_id": coupon.id}


@router.get("")
async def list_coupons(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    List all coupons (Admin only).
    """
    result = await db.execute(
        select(Coupon).order_by(Coupon.created_at.desc())
    )
    coupons = result.scalars().all()
    
    return [
        {
            "id": c.id,
            "code": c.code,
            "description": c.description,
            "discount_type": c.discount_type,
            "discount_value": c.discount_value,
            "used_count": c.used_count,
            "usage_limit": c.usage_limit,
            "is_active": c.is_active,
            "end_date": c.end_date.isoformat() if c.end_date else None,
        }
        for c in coupons
    ]


@router.patch("/{coupon_id}/toggle")
async def toggle_coupon(
    coupon_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Toggle coupon active status (Admin only).
    """
    result = await db.execute(select(Coupon).where(Coupon.id == coupon_id))
    coupon = result.scalars().first()
    
    if not coupon:
        raise HTTPException(status_code=404, detail="Coupon not found")
    
    coupon.is_active = not coupon.is_active
    db.add(coupon)
    await db.commit()
    
    return {"message": f"Coupon {'activated' if coupon.is_active else 'deactivated'}"}
