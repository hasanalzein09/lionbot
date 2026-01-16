from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from app.db.session import get_db
from app.api import deps
from app.models.user import User
from app.models.inventory import InventoryUnit, StockMovementType
from app.services.inventory_service import InventoryService

router = APIRouter()


# ============= Schemas =============

class InventoryItemCreate(BaseModel):
    name: str
    name_ar: Optional[str] = None
    sku: Optional[str] = None
    category: Optional[str] = None
    unit: str = "pieces"
    min_quantity: float = 10
    cost_per_unit: float = 0
    supplier_name: Optional[str] = None
    supplier_phone: Optional[str] = None


class InventoryItemResponse(BaseModel):
    id: int
    name: str
    name_ar: Optional[str]
    sku: Optional[str]
    category: Optional[str]
    unit: str
    current_quantity: float
    min_quantity: float
    cost_per_unit: float
    average_cost: float
    is_low_stock: bool
    last_restocked_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class AddStockRequest(BaseModel):
    quantity: float = Field(gt=0)
    unit_cost: float = Field(ge=0)
    notes: Optional[str] = None


class DeductStockRequest(BaseModel):
    quantity: float = Field(gt=0)
    reason: str = "sale"  # sale, waste, adjustment
    notes: Optional[str] = None


class AdjustStockRequest(BaseModel):
    new_quantity: float = Field(ge=0)
    reason: str


class StockMovementResponse(BaseModel):
    id: int
    type: str
    quantity: float
    quantity_before: float
    quantity_after: float
    unit_cost: Optional[float]
    total_cost: Optional[float]
    notes: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class AlertResponse(BaseModel):
    id: int
    alert_type: str
    message: str
    is_read: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============= Endpoints =============

@router.post("/{restaurant_id}/items", response_model=InventoryItemResponse)
async def create_inventory_item(
    restaurant_id: int,
    item_data: InventoryItemCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Create a new inventory item for a restaurant."""
    service = InventoryService(db)
    
    try:
        unit = InventoryUnit(item_data.unit)
    except ValueError:
        unit = InventoryUnit.PIECES
    
    item = await service.create_item(
        restaurant_id=restaurant_id,
        name=item_data.name,
        name_ar=item_data.name_ar,
        sku=item_data.sku,
        category=item_data.category,
        unit=unit,
        min_quantity=item_data.min_quantity,
        cost_per_unit=item_data.cost_per_unit,
        supplier_name=item_data.supplier_name,
        supplier_phone=item_data.supplier_phone,
    )
    
    return InventoryItemResponse(
        id=item.id,
        name=item.name,
        name_ar=item.name_ar,
        sku=item.sku,
        category=item.category,
        unit=item.unit.value,
        current_quantity=item.current_quantity,
        min_quantity=item.min_quantity,
        cost_per_unit=item.cost_per_unit,
        average_cost=item.average_cost,
        is_low_stock=item.is_low_stock,
        last_restocked_at=item.last_restocked_at,
    )


@router.get("/{restaurant_id}/items", response_model=List[InventoryItemResponse])
async def get_restaurant_inventory(
    restaurant_id: int,
    include_inactive: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get all inventory items for a restaurant."""
    service = InventoryService(db)
    items = await service.get_restaurant_inventory(restaurant_id, include_inactive)
    
    return [
        InventoryItemResponse(
            id=item.id,
            name=item.name,
            name_ar=item.name_ar,
            sku=item.sku,
            category=item.category,
            unit=item.unit.value,
            current_quantity=item.current_quantity,
            min_quantity=item.min_quantity,
            cost_per_unit=item.cost_per_unit,
            average_cost=item.average_cost,
            is_low_stock=item.is_low_stock,
            last_restocked_at=item.last_restocked_at,
        )
        for item in items
    ]


@router.get("/{restaurant_id}/low-stock", response_model=List[InventoryItemResponse])
async def get_low_stock_items(
    restaurant_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get all items that are low on stock."""
    service = InventoryService(db)
    items = await service.get_low_stock_items(restaurant_id)
    
    return [
        InventoryItemResponse(
            id=item.id,
            name=item.name,
            name_ar=item.name_ar,
            sku=item.sku,
            category=item.category,
            unit=item.unit.value,
            current_quantity=item.current_quantity,
            min_quantity=item.min_quantity,
            cost_per_unit=item.cost_per_unit,
            average_cost=item.average_cost,
            is_low_stock=item.is_low_stock,
            last_restocked_at=item.last_restocked_at,
        )
        for item in items
    ]


@router.post("/items/{item_id}/add-stock", response_model=StockMovementResponse)
async def add_stock(
    item_id: int,
    request: AddStockRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Add stock to an inventory item."""
    service = InventoryService(db)
    
    try:
        movement = await service.add_stock(
            item_id=item_id,
            quantity=request.quantity,
            unit_cost=request.unit_cost,
            notes=request.notes,
            performed_by=current_user.id,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    return StockMovementResponse(
        id=movement.id,
        type=movement.type.value,
        quantity=movement.quantity,
        quantity_before=movement.quantity_before,
        quantity_after=movement.quantity_after,
        unit_cost=movement.unit_cost,
        total_cost=movement.total_cost,
        notes=movement.notes,
        created_at=movement.created_at,
    )


@router.post("/items/{item_id}/deduct-stock", response_model=StockMovementResponse)
async def deduct_stock(
    item_id: int,
    request: DeductStockRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Deduct stock from an inventory item."""
    service = InventoryService(db)
    
    movement_type = StockMovementType.SALE
    if request.reason == "waste":
        movement_type = StockMovementType.WASTE
    elif request.reason == "adjustment":
        movement_type = StockMovementType.ADJUSTMENT
    
    try:
        movement = await service.deduct_stock(
            item_id=item_id,
            quantity=request.quantity,
            movement_type=movement_type,
            notes=request.notes,
            performed_by=current_user.id,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    return StockMovementResponse(
        id=movement.id,
        type=movement.type.value,
        quantity=movement.quantity,
        quantity_before=movement.quantity_before,
        quantity_after=movement.quantity_after,
        unit_cost=movement.unit_cost,
        total_cost=movement.total_cost,
        notes=movement.notes,
        created_at=movement.created_at,
    )


@router.post("/items/{item_id}/adjust", response_model=StockMovementResponse)
async def adjust_stock(
    item_id: int,
    request: AdjustStockRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Manually adjust stock count."""
    service = InventoryService(db)
    
    try:
        movement = await service.adjust_stock(
            item_id=item_id,
            new_quantity=request.new_quantity,
            reason=request.reason,
            performed_by=current_user.id,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    return StockMovementResponse(
        id=movement.id,
        type=movement.type.value,
        quantity=movement.quantity,
        quantity_before=movement.quantity_before,
        quantity_after=movement.quantity_after,
        unit_cost=movement.unit_cost,
        total_cost=movement.total_cost,
        notes=movement.notes,
        created_at=movement.created_at,
    )


@router.get("/items/{item_id}/history", response_model=List[StockMovementResponse])
async def get_stock_history(
    item_id: int,
    days: int = Query(default=30, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get stock movement history for an item."""
    service = InventoryService(db)
    movements = await service.get_stock_movements(item_id, days)
    
    return [
        StockMovementResponse(
            id=m.id,
            type=m.type.value,
            quantity=m.quantity,
            quantity_before=m.quantity_before,
            quantity_after=m.quantity_after,
            unit_cost=m.unit_cost,
            total_cost=m.total_cost,
            notes=m.notes,
            created_at=m.created_at,
        )
        for m in movements
    ]


@router.get("/{restaurant_id}/value")
async def get_inventory_value(
    restaurant_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get total inventory value and statistics."""
    service = InventoryService(db)
    return await service.get_inventory_value(restaurant_id)


@router.get("/{restaurant_id}/alerts", response_model=List[AlertResponse])
async def get_inventory_alerts(
    restaurant_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get unread inventory alerts for a restaurant."""
    service = InventoryService(db)
    alerts = await service.get_unread_alerts(restaurant_id)
    
    return [
        AlertResponse(
            id=alert.id,
            alert_type=alert.alert_type,
            message=alert.message,
            is_read=alert.is_read,
            created_at=alert.created_at,
        )
        for alert in alerts
    ]
