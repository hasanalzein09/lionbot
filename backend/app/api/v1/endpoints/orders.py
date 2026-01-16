from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.api import deps
from app.db.session import get_db
from app.models.order import Order, OrderItem, OrderStatus
from sqlalchemy.orm import joinedload
from app.models.user import User
from app.models.restaurant import Restaurant
from app.models.menu import MenuItem
from app.schemas.order import Order as OrderSchema, OrderStatusUpdate, OrderDetailed, OrderItemDetailed
from app.services.redis_service import redis_service
from app.services.audit_service import get_audit_service
from app.core.constants import lbp_to_usd

router = APIRouter()

@router.get("/", response_model=List[OrderSchema])
async def read_orders(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    restaurant_id: Optional[int] = None,
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Retrieve all orders (Super Admin only).
    Optional filters: status, restaurant_id
    """
    query = select(Order).options(selectinload(Order.items))
    
    if status:
        query = query.where(Order.status == status)
    if restaurant_id:
        query = query.where(Order.restaurant_id == restaurant_id)
    
    query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/restaurant/{restaurant_id}", response_model=List[OrderSchema])
async def read_restaurant_orders(
    restaurant_id: int,
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get orders for a specific restaurant.
    """
    query = (
        select(Order)
        .where(Order.restaurant_id == restaurant_id)
        .options(selectinload(Order.items))
    )
    
    if status:
        query = query.where(Order.status == status)
    
    query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{order_id}", response_model=OrderDetailed)
async def read_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get order by ID with detailed information.
    Uses eager loading to avoid N+1 queries.
    """
    # Get order with all related data in a single query (N+1 fix)
    result = await db.execute(
        select(Order)
        .where(Order.id == order_id)
        .options(
            selectinload(Order.items).selectinload(OrderItem.menu_item),
            selectinload(Order.restaurant),
            selectinload(Order.customer),
            selectinload(Order.driver),
        )
    )
    order = result.scalars().first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Access eagerly loaded relationships
    restaurant = order.restaurant
    customer = order.customer
    driver = order.driver

    # Build item details from eagerly loaded data
    items_detailed = []
    for item in order.items:
        menu_item = item.menu_item
        items_detailed.append(OrderItemDetailed(
            id=item.id,
            menu_item_id=item.menu_item_id,
            name=menu_item.name if menu_item else "Unknown Item",
            name_ar=menu_item.name_ar if menu_item else None,
            quantity=item.quantity,
            unit_price=item.unit_price,
            total_price=item.total_price,
        ))

    # Convert total_amount from LBP to USD (if stored in LBP)
    total_usd = order.total_amount
    if order.total_amount > 1000:  # Likely stored in LBP
        total_usd = lbp_to_usd(order.total_amount)

    return OrderDetailed(
        id=order.id,
        status=order.status,
        total_amount=total_usd,
        delivery_fee=lbp_to_usd(order.delivery_fee) if order.delivery_fee > 100 else order.delivery_fee,
        order_type=order.order_type,
        address=order.address,
        latitude=order.latitude,
        longitude=order.longitude,
        created_at=order.created_at,
        updated_at=order.updated_at,
        restaurant_id=order.restaurant_id,
        restaurant_name=restaurant.name if restaurant else None,
        restaurant_name_ar=restaurant.name_ar if restaurant else None,
        restaurant_phone=restaurant.phone_number if restaurant else None,
        user_id=order.user_id,
        customer_name=customer.full_name if customer else None,
        customer_phone=customer.phone_number if customer else None,
        driver_id=order.driver_id,
        driver_name=driver.full_name if driver else None,
        driver_phone=driver.phone_number if driver else None,
        items=items_detailed,
    )

@router.put("/{order_id}", response_model=OrderSchema)
async def update_order(
    *,
    request: Request,
    db: AsyncSession = Depends(get_db),
    order_id: int,
    status_update: OrderStatusUpdate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Update an order (specifically status).
    """
    result = await db.execute(
        select(Order).where(Order.id == order_id)
    )
    order = result.scalars().first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Capture old status for audit
    old_status = order.status.value if order.status else None

    # Update status
    order.status = status_update.status
    db.add(order)

    # Audit log for status change
    audit = get_audit_service(db)
    await audit.log_status_change(
        entity_type="order",
        entity_id=order_id,
        old_status=old_status,
        new_status=status_update.status.value,
        user=current_user,
        request=request,
    )

    await db.commit()
    await db.refresh(order)

    # Publish real-time update
    await redis_service.publish_order_update(order_id, {
        "type": "status_update",
        "order_id": order_id,
        "new_status": status_update.status.value,
        "updated_by": current_user.id
    })

    return order

@router.patch("/{order_id}/status")
async def update_order_status(
    order_id: int,
    status_update: OrderStatusUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Update order status.
    Valid statuses: new, accepted, preparing, ready, out_for_delivery, delivered, cancelled
    """
    result = await db.execute(
        select(Order).where(Order.id == order_id)
    )
    order = result.scalars().first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Capture old status for audit
    old_status = order.status.value if order.status else None

    # Update status
    order.status = status_update.status
    db.add(order)

    # Audit log for status change
    audit = get_audit_service(db)
    await audit.log_status_change(
        entity_type="order",
        entity_id=order_id,
        old_status=old_status,
        new_status=status_update.status.value,
        user=current_user,
        request=request,
    )

    await db.commit()
    await db.refresh(order)

    # Publish real-time update
    await redis_service.publish_order_update(order_id, {
        "type": "status_update",
        "order_id": order_id,
        "new_status": status_update.status.value,
        "updated_by": current_user.id
    })

    # TODO: Send WhatsApp notification to customer about status change

    return {"message": "Order status updated", "order_id": order_id, "status": status_update.status}

@router.patch("/{order_id}/driver")
async def assign_driver(
    order_id: int,
    driver_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Assign a driver to an order.
    """
    # Check if order exists
    order_result = await db.execute(
        select(Order).where(Order.id == order_id)
    )
    order = order_result.scalars().first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Check if driver exists
    driver_result = await db.execute(
        select(User).where(User.id == driver_id).where(User.role == "driver")
    )
    driver = driver_result.scalars().first()

    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")

    # Capture old values for audit
    old_driver_id = order.driver_id
    old_status = order.status.value if order.status else None

    # Assign driver
    order.driver_id = driver_id
    order.status = OrderStatus.OUT_FOR_DELIVERY
    db.add(order)

    # Audit log for driver assignment
    audit = get_audit_service(db)
    await audit.log_update(
        entity_type="order",
        entity_id=order_id,
        old_values={"driver_id": old_driver_id, "status": old_status},
        new_values={"driver_id": driver_id, "status": OrderStatus.OUT_FOR_DELIVERY.value},
        user=current_user,
        request=request,
    )

    await db.commit()

    # Notify driver
    await redis_service.publish_driver_notification(driver_id, {
        "type": "new_delivery",
        "order_id": order_id,
        "restaurant_id": order.restaurant_id,
        "delivery_address": order.address,
        "lat": order.latitude,
        "lng": order.longitude
    })

    return {"message": "Driver assigned", "order_id": order_id, "driver_id": driver_id}

@router.get("/stats/summary")
async def get_order_stats(
    db: AsyncSession = Depends(get_db),
    restaurant_id: Optional[int] = None,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get order statistics summary.
    """
    base_query = select(Order)
    
    if restaurant_id:
        base_query = base_query.where(Order.restaurant_id == restaurant_id)
    
    # Total orders
    total_result = await db.execute(
        select(func.count(Order.id)).select_from(Order)
    )
    total_orders = total_result.scalar() or 0
    
    # Total revenue
    revenue_result = await db.execute(
        select(func.sum(Order.total_amount)).select_from(Order)
        .where(Order.status == OrderStatus.DELIVERED)
    )
    total_revenue = revenue_result.scalar() or 0
    
    # Pending orders
    pending_result = await db.execute(
        select(func.count(Order.id)).select_from(Order)
        .where(Order.status == OrderStatus.NEW)
    )
    pending_orders = pending_result.scalar() or 0
    
    # Orders by status
    status_query = (
        select(Order.status, func.count(Order.id))
        .group_by(Order.status)
    )
    status_result = await db.execute(status_query)
    orders_by_status = {str(row[0].value): row[1] for row in status_result.fetchall()}
    
    return {
        "total_orders": total_orders,
        "total_revenue": float(total_revenue),
        "pending_orders": pending_orders,
        "orders_by_status": orders_by_status
    }

@router.get("/driver/{driver_id}", response_model=List[OrderSchema])
async def read_driver_orders(
    driver_id: int,
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get orders assigned to a specific driver.
    """
    # Verify access
    if current_user.id != driver_id and current_user.role != "super_admin":
        raise HTTPException(status_code=403, detail="Not authorized to view these orders")

    query = (
        select(Order)
        .where(Order.driver_id == driver_id)
        .options(selectinload(Order.items))
    )
    
    if status:
        query = query.where(Order.status == status)
    
    query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()
