"""
Order Cancellation API
"""
from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta

from app.db.session import get_db
from app.models.user import User
from app.models.order import Order, OrderStatus
from app.api import deps

router = APIRouter()


CANCELLATION_WINDOW_MINUTES = 5  # Can cancel within 5 minutes


@router.post("/{order_id}")
async def cancel_order(
    order_id: int,
    reason: str = "Customer requested",
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Cancel an order (within allowed window).
    """
    result = await db.execute(
        select(Order).where(
            Order.id == order_id,
            Order.customer_phone == current_user.phone_number
        )
    )
    order = result.scalars().first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Check if already cancelled or delivered
    if order.status in [OrderStatus.CANCELLED, OrderStatus.DELIVERED]:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot cancel order with status: {order.status}"
        )
    
    # Check if within cancellation window
    if order.created_at:
        time_since_order = datetime.utcnow() - order.created_at
        if time_since_order > timedelta(minutes=CANCELLATION_WINDOW_MINUTES):
            # After window, need to contact support
            if order.status not in [OrderStatus.PENDING]:
                raise HTTPException(
                    status_code=400,
                    detail="Order is being prepared. Please contact support to cancel."
                )
    
    # Cancel the order
    order.status = OrderStatus.CANCELLED
    order.notes = f"Cancelled by customer: {reason}"
    
    db.add(order)
    await db.commit()
    
    # TODO: Trigger refund if payment was made
    # TODO: Notify restaurant
    # TODO: Notify driver if assigned
    
    return {
        "message": "Order cancelled successfully",
        "order_id": order_id,
        "refund_status": "N/A - Cash on Delivery",
    }


@router.get("/{order_id}/can-cancel")
async def can_cancel_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Check if order can be cancelled.
    """
    result = await db.execute(
        select(Order).where(
            Order.id == order_id,
            Order.customer_phone == current_user.phone_number
        )
    )
    order = result.scalars().first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    can_cancel = True
    reason = None
    
    if order.status in [OrderStatus.CANCELLED, OrderStatus.DELIVERED]:
        can_cancel = False
        reason = f"Order is already {order.status}"
    elif order.status in [OrderStatus.OUT_FOR_DELIVERY]:
        can_cancel = False
        reason = "Order is out for delivery"
    elif order.created_at:
        time_since_order = datetime.utcnow() - order.created_at
        if time_since_order > timedelta(minutes=CANCELLATION_WINDOW_MINUTES):
            if order.status != OrderStatus.PENDING:
                can_cancel = False
                reason = "Cancellation window expired. Contact support."
    
    return {
        "order_id": order_id,
        "can_cancel": can_cancel,
        "reason": reason,
        "current_status": order.status.value if hasattr(order.status, 'value') else order.status,
    }
