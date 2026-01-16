from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional

from app.db.session import get_db
from app.api import deps
from app.models.user import User
from app.services.driver_assignment_service import DriverAssignmentService
from app.core.websocket_manager import ws_manager

router = APIRouter()


class AutoAssignRequest(BaseModel):
    order_id: int
    priority: str = "normal"  # "normal", "high", "urgent"


class AutoAssignResponse(BaseModel):
    success: bool
    driver_id: Optional[int]
    driver_name: Optional[str]
    estimated_arrival: Optional[str]
    message: str


class NearbyDriversRequest(BaseModel):
    latitude: float
    longitude: float
    radius_km: float = 5.0


class DriverInfo(BaseModel):
    id: int
    name: str
    distance_km: float
    rating: Optional[float]
    active_orders: int


@router.post("/auto-assign", response_model=AutoAssignResponse)
async def auto_assign_driver(
    request: AutoAssignRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
):
    """
    Automatically assign the best available driver to an order.
    Only accessible by super admins.
    """
    service = DriverAssignmentService(db)
    driver = await service.auto_assign_order(request.order_id)
    
    if not driver:
        return AutoAssignResponse(
            success=False,
            driver_id=None,
            driver_name=None,
            estimated_arrival=None,
            message="No available drivers found in the area."
        )
    
    # Notify driver via WebSocket
    background_tasks.add_task(
        ws_manager.notify_driver,
        driver.id,
        {
            "type": "new_assignment",
            "order_id": request.order_id,
            "priority": request.priority,
            "message": "You have a new delivery assignment!"
        }
    )
    
    return AutoAssignResponse(
        success=True,
        driver_id=driver.id,
        driver_name=driver.full_name,
        estimated_arrival="10-15 min",  # TODO: Calculate based on distance
        message=f"Order assigned to {driver.full_name}"
    )


@router.post("/nearby")
async def get_nearby_drivers(
    request: NearbyDriversRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
):
    """Get list of nearby available drivers."""
    from sqlalchemy import select
    from app.models.user import User
    
    result = await db.execute(
        select(User)
        .where(User.role == "driver")
        .where(User.is_active == True)
        .where(User.last_latitude != None)
    )
    drivers = result.scalars().all()
    
    service = DriverAssignmentService(db)
    nearby = []
    
    for driver in drivers:
        distance = service._haversine_distance(
            request.latitude, request.longitude,
            driver.last_latitude, driver.last_longitude
        )
        
        if distance <= request.radius_km:
            active_orders = await service._get_driver_active_orders_count(driver.id)
            nearby.append({
                "id": driver.id,
                "name": driver.full_name,
                "distance_km": round(distance, 2),
                "rating": driver.average_rating,
                "active_orders": active_orders,
                "latitude": driver.last_latitude,
                "longitude": driver.last_longitude,
            })
    
    # Sort by distance
    nearby.sort(key=lambda x: x["distance_km"])
    
    return {
        "count": len(nearby),
        "drivers": nearby
    }


@router.post("/manual-assign")
async def manual_assign_driver(
    order_id: int,
    driver_id: int,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
):
    """Manually assign a specific driver to an order."""
    from sqlalchemy import select
    from app.models.order import Order, OrderStatus
    from app.models.user import User
    
    # Verify order exists
    order_result = await db.execute(select(Order).where(Order.id == order_id))
    order = order_result.scalars().first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Verify driver exists and is active
    driver_result = await db.execute(
        select(User)
        .where(User.id == driver_id)
        .where(User.role == "driver")
        .where(User.is_active == True)
    )
    driver = driver_result.scalars().first()
    
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found or inactive")
    
    # Assign
    order.driver_id = driver.id
    order.status = OrderStatus.OUT_FOR_DELIVERY
    await db.commit()
    
    # Notify driver
    background_tasks.add_task(
        ws_manager.notify_driver,
        driver.id,
        {
            "type": "new_assignment",
            "order_id": order_id,
            "message": "You have been assigned a new delivery."
        }
    )
    
    return {
        "success": True,
        "message": f"Order #{order_id} assigned to {driver.full_name}"
    }


@router.get("/stats")
async def get_assignment_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
):
    """Get driver assignment statistics."""
    from sqlalchemy import select, func
    from app.models.order import Order, OrderStatus
    from app.models.user import User
    from datetime import datetime
    
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Online drivers
    online_result = await db.execute(
        select(func.count(User.id))
        .where(User.role == "driver")
        .where(User.is_active == True)
    )
    online_drivers = online_result.scalar() or 0
    
    # Active deliveries
    active_result = await db.execute(
        select(func.count(Order.id))
        .where(Order.status == OrderStatus.OUT_FOR_DELIVERY)
    )
    active_deliveries = active_result.scalar() or 0
    
    # Today's completed
    completed_result = await db.execute(
        select(func.count(Order.id))
        .where(Order.status == OrderStatus.DELIVERED)
        .where(Order.created_at >= today_start)
    )
    completed_today = completed_result.scalar() or 0
    
    # Pending assignments
    pending_result = await db.execute(
        select(func.count(Order.id))
        .where(Order.status == OrderStatus.READY)
        .where(Order.driver_id == None)
    )
    pending_assignments = pending_result.scalar() or 0
    
    return {
        "online_drivers": online_drivers,
        "active_deliveries": active_deliveries,
        "completed_today": completed_today,
        "pending_assignments": pending_assignments,
    }
