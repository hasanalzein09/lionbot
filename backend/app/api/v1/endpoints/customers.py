from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from pydantic import BaseModel

from app.db.session import get_db
from app.models.user import User, UserRole
from app.models.order import Order, OrderStatus
from app.core.security import get_password_hash
from app.core.validators import (
    validate_phone_number, validate_email, validate_name,
    sanitize_text
)
from app.api import deps

router = APIRouter()


# ==================== Schemas ====================

class CustomerRegister(BaseModel):
    full_name: str
    phone_number: str
    password: str
    email: Optional[str] = None


class CustomerProfile(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None


class AddressCreate(BaseModel):
    label: str  # "Home", "Work", etc.
    address: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_default: bool = False


# ==================== Registration ====================

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_customer(
    customer_in: CustomerRegister,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Public endpoint for customer self-registration.
    Validates all inputs before processing.
    """
    # Validate and sanitize inputs
    validate_name(customer_in.full_name)
    is_valid, normalized_phone = validate_phone_number(customer_in.phone_number)
    if customer_in.email:
        validate_email(customer_in.email)

    # Sanitize name
    sanitized_name = sanitize_text(customer_in.full_name, max_length=100)

    # Check if phone exists (using normalized phone)
    result = await db.execute(
        select(User).where(User.phone_number == normalized_phone)
    )
    if result.scalars().first():
        raise HTTPException(
            status_code=400,
            detail="Phone number already registered"
        )

    # Check if email exists (if provided)
    if customer_in.email:
        result = await db.execute(
            select(User).where(User.email == customer_in.email.lower())
        )
        if result.scalars().first():
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )

    # Create customer user with sanitized/normalized data
    user = User(
        full_name=sanitized_name,
        phone_number=normalized_phone,
        email=customer_in.email.lower() if customer_in.email else None,
        hashed_password=get_password_hash(customer_in.password),
        role=UserRole.CUSTOMER,
        is_active=True,
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    return {
        "message": "Registration successful",
        "user_id": user.id,
        "phone_number": user.phone_number,
    }


@router.put("/profile")
async def update_customer_profile(
    profile_in: CustomerProfile,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Update current customer's profile.
    """
    update_data = profile_in.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)
    
    return {"message": "Profile updated", "user": {
        "id": current_user.id,
        "full_name": current_user.full_name,
        "email": current_user.email,
    }}


# ==================== Orders ====================

@router.get("/my-orders")
async def get_my_orders(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
    status_filter: Optional[str] = None,
    limit: int = 50,
) -> Any:
    """
    Get orders for the current logged-in customer.
    Uses eager loading to avoid N+1 queries.
    """
    query = (
        select(Order)
        .where(Order.customer_phone == current_user.phone_number)
        .options(
            selectinload(Order.restaurant),
            selectinload(Order.items),
        )
    )

    if status_filter:
        query = query.where(Order.status == status_filter)

    query = query.order_by(Order.created_at.desc()).limit(limit)

    result = await db.execute(query)
    orders = result.scalars().all()

    return [
        {
            "id": o.id,
            "status": o.status.value if hasattr(o.status, 'value') else o.status,
            "total_amount": float(o.total_amount) if o.total_amount else 0,
            "restaurant_name": o.restaurant.name if o.restaurant else "Unknown",
            "restaurant_id": o.restaurant_id,
            "created_at": o.created_at.isoformat() if o.created_at else None,
            "delivery_address": o.delivery_address,
            "items": o.items or [],
        }
        for o in orders
    ]


@router.get("/my-orders/{order_id}")
async def get_my_order_details(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get specific order details for the current customer.
    Uses eager loading to avoid N+1 queries.
    """
    result = await db.execute(
        select(Order)
        .where(
            Order.id == order_id,
            Order.customer_phone == current_user.phone_number
        )
        .options(
            selectinload(Order.restaurant),
            selectinload(Order.items),
        )
    )
    order = result.scalars().first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return {
        "id": order.id,
        "status": order.status.value if hasattr(order.status, 'value') else order.status,
        "total_amount": float(order.total_amount) if order.total_amount else 0,
        "restaurant_name": order.restaurant.name if order.restaurant else "Unknown",
        "restaurant_id": order.restaurant_id,
        "created_at": order.created_at.isoformat() if order.created_at else None,
        "updated_at": order.updated_at.isoformat() if order.updated_at else None,
        "delivery_address": order.delivery_address,
        "items": order.items or [],
        "customer_phone": order.customer_phone,
        "customer_name": order.customer_name,
        "payment_method": "cash_on_delivery",
        "driver_id": order.driver_id,
    }


@router.get("/my-orders/{order_id}/track")
async def track_my_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Track order status and driver location.
    Uses eager loading to avoid N+1 queries.
    """
    result = await db.execute(
        select(Order)
        .where(
            Order.id == order_id,
            Order.customer_phone == current_user.phone_number
        )
        .options(
            selectinload(Order.restaurant),
            selectinload(Order.driver),
        )
    )
    order = result.scalars().first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    tracking = {
        "order_id": order.id,
        "status": order.status.value if hasattr(order.status, 'value') else order.status,
        "restaurant_name": order.restaurant.name if order.restaurant else "Unknown",
        "estimated_time": "30-45 min",
        "driver": None,
    }

    # Include driver location if assigned and out for delivery
    driver = order.driver
    if driver and order.status in [OrderStatus.OUT_FOR_DELIVERY, OrderStatus.READY]:
        tracking["driver"] = {
            "name": driver.full_name,
            "phone": driver.phone_number,
            "latitude": driver.last_latitude,
            "longitude": driver.last_longitude,
        }

    return tracking
