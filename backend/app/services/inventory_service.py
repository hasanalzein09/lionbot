from typing import List, Optional, Tuple
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta

from app.models.inventory import (
    InventoryItem, StockMovement, InventoryAlert, 
    SupplierOrder, SupplierOrderItem,
    InventoryUnit, StockMovementType
)
from app.core.websocket_manager import ws_manager


class InventoryService:
    """Service for managing restaurant inventory."""
    
    def __init__(self, db: AsyncSession):
        self.db = db

    # ==================== Inventory Items ====================
    
    async def create_item(
        self,
        restaurant_id: int,
        name: str,
        unit: InventoryUnit = InventoryUnit.PIECES,
        min_quantity: float = 10,
        cost_per_unit: float = 0,
        **kwargs
    ) -> InventoryItem:
        """Create a new inventory item."""
        item = InventoryItem(
            restaurant_id=restaurant_id,
            name=name,
            unit=unit,
            min_quantity=min_quantity,
            cost_per_unit=cost_per_unit,
            **kwargs
        )
        self.db.add(item)
        await self.db.commit()
        await self.db.refresh(item)
        return item

    async def get_item(self, item_id: int) -> Optional[InventoryItem]:
        """Get an inventory item by ID."""
        result = await self.db.execute(
            select(InventoryItem).where(InventoryItem.id == item_id)
        )
        return result.scalars().first()

    async def get_restaurant_inventory(
        self, 
        restaurant_id: int,
        include_inactive: bool = False
    ) -> List[InventoryItem]:
        """Get all inventory items for a restaurant."""
        query = select(InventoryItem).where(
            InventoryItem.restaurant_id == restaurant_id
        )
        if not include_inactive:
            query = query.where(InventoryItem.is_active == True)
        
        result = await self.db.execute(query.order_by(InventoryItem.name))
        return result.scalars().all()

    async def get_low_stock_items(self, restaurant_id: int) -> List[InventoryItem]:
        """Get items that are below minimum quantity."""
        result = await self.db.execute(
            select(InventoryItem)
            .where(InventoryItem.restaurant_id == restaurant_id)
            .where(InventoryItem.is_active == True)
            .where(InventoryItem.current_quantity <= InventoryItem.min_quantity)
        )
        return result.scalars().all()

    # ==================== Stock Management ====================
    
    async def add_stock(
        self,
        item_id: int,
        quantity: float,
        unit_cost: float,
        notes: str = None,
        performed_by: int = None,
        reference_type: str = "manual",
        reference_id: int = None
    ) -> StockMovement:
        """Add stock to an inventory item."""
        item = await self.get_item(item_id)
        if not item:
            raise ValueError("Item not found")
        
        quantity_before = item.current_quantity
        quantity_after = quantity_before + quantity
        
        movement = StockMovement(
            item_id=item_id,
            type=StockMovementType.PURCHASE,
            quantity=quantity,
            quantity_before=quantity_before,
            quantity_after=quantity_after,
            unit_cost=unit_cost,
            total_cost=quantity * unit_cost,
            reference_type=reference_type,
            reference_id=reference_id,
            notes=notes,
            performed_by=performed_by
        )
        self.db.add(movement)
        
        # Update item
        item.current_quantity = quantity_after
        item.last_purchase_price = unit_cost
        item.last_restocked_at = datetime.utcnow()
        
        # Update average cost
        if item.average_cost and item.average_cost > 0:
            total_value = (quantity_before * item.average_cost) + (quantity * unit_cost)
            item.average_cost = total_value / quantity_after if quantity_after > 0 else unit_cost
        else:
            item.average_cost = unit_cost
        
        # Check if no longer low stock
        if item.current_quantity > item.min_quantity:
            item.is_low_stock = False
            await self._resolve_alerts(item_id)
        
        await self.db.commit()
        return movement

    async def deduct_stock(
        self,
        item_id: int,
        quantity: float,
        movement_type: StockMovementType = StockMovementType.SALE,
        notes: str = None,
        performed_by: int = None,
        reference_type: str = "order",
        reference_id: int = None
    ) -> StockMovement:
        """Deduct stock from an inventory item."""
        item = await self.get_item(item_id)
        if not item:
            raise ValueError("Item not found")
        
        quantity_before = item.current_quantity
        quantity_after = max(0, quantity_before - quantity)
        
        movement = StockMovement(
            item_id=item_id,
            type=movement_type,
            quantity=-quantity,  # Negative for deduction
            quantity_before=quantity_before,
            quantity_after=quantity_after,
            unit_cost=item.average_cost,
            total_cost=quantity * item.average_cost,
            reference_type=reference_type,
            reference_id=reference_id,
            notes=notes,
            performed_by=performed_by
        )
        self.db.add(movement)
        
        # Update item
        item.current_quantity = quantity_after
        
        # Check for low stock
        if item.current_quantity <= item.min_quantity:
            item.is_low_stock = True
            await self._create_low_stock_alert(item)
        
        await self.db.commit()
        return movement

    async def adjust_stock(
        self,
        item_id: int,
        new_quantity: float,
        reason: str,
        performed_by: int = None
    ) -> StockMovement:
        """Manually adjust stock count."""
        item = await self.get_item(item_id)
        if not item:
            raise ValueError("Item not found")
        
        quantity_before = item.current_quantity
        difference = new_quantity - quantity_before
        
        movement = StockMovement(
            item_id=item_id,
            type=StockMovementType.ADJUSTMENT,
            quantity=difference,
            quantity_before=quantity_before,
            quantity_after=new_quantity,
            unit_cost=item.average_cost,
            total_cost=abs(difference) * item.average_cost,
            reference_type="manual",
            notes=reason,
            performed_by=performed_by
        )
        self.db.add(movement)
        
        item.current_quantity = new_quantity
        
        # Update low stock status
        if new_quantity <= item.min_quantity:
            item.is_low_stock = True
            await self._create_low_stock_alert(item)
        else:
            item.is_low_stock = False
            await self._resolve_alerts(item_id)
        
        await self.db.commit()
        return movement

    # ==================== Alerts ====================
    
    async def _create_low_stock_alert(self, item: InventoryItem):
        """Create a low stock alert."""
        # Check if alert already exists
        result = await self.db.execute(
            select(InventoryAlert)
            .where(InventoryAlert.item_id == item.id)
            .where(InventoryAlert.alert_type == "low_stock")
            .where(InventoryAlert.is_resolved == False)
        )
        existing = result.scalars().first()
        
        if not existing:
            alert_type = "out_of_stock" if item.current_quantity == 0 else "low_stock"
            alert = InventoryAlert(
                item_id=item.id,
                restaurant_id=item.restaurant_id,
                alert_type=alert_type,
                message=f"{item.name} is {alert_type.replace('_', ' ')}. Current: {item.current_quantity} {item.unit.value}",
                message_ar=f"{item.name_ar or item.name} منخفض المخزون. الحالي: {item.current_quantity}"
            )
            self.db.add(alert)
            
            # Notify restaurant via WebSocket
            await ws_manager.notify_restaurant(
                item.restaurant_id,
                {
                    "type": "inventory_alert",
                    "alert_type": alert_type,
                    "item_name": item.name,
                    "current_quantity": item.current_quantity,
                    "min_quantity": item.min_quantity
                }
            )

    async def _resolve_alerts(self, item_id: int):
        """Resolve all alerts for an item."""
        result = await self.db.execute(
            select(InventoryAlert)
            .where(InventoryAlert.item_id == item_id)
            .where(InventoryAlert.is_resolved == False)
        )
        alerts = result.scalars().all()
        
        for alert in alerts:
            alert.is_resolved = True
            alert.resolved_at = datetime.utcnow()

    async def get_unread_alerts(self, restaurant_id: int) -> List[InventoryAlert]:
        """Get unread alerts for a restaurant."""
        result = await self.db.execute(
            select(InventoryAlert)
            .where(InventoryAlert.restaurant_id == restaurant_id)
            .where(InventoryAlert.is_resolved == False)
            .order_by(InventoryAlert.created_at.desc())
        )
        return result.scalars().all()

    # ==================== Reports ====================
    
    async def get_inventory_value(self, restaurant_id: int) -> dict:
        """Calculate total inventory value."""
        result = await self.db.execute(
            select(
                func.sum(InventoryItem.current_quantity * InventoryItem.average_cost)
            )
            .where(InventoryItem.restaurant_id == restaurant_id)
            .where(InventoryItem.is_active == True)
        )
        total_value = result.scalar() or 0
        
        # Count items
        count_result = await self.db.execute(
            select(func.count(InventoryItem.id))
            .where(InventoryItem.restaurant_id == restaurant_id)
            .where(InventoryItem.is_active == True)
        )
        total_items = count_result.scalar() or 0
        
        # Low stock count
        low_stock_result = await self.db.execute(
            select(func.count(InventoryItem.id))
            .where(InventoryItem.restaurant_id == restaurant_id)
            .where(InventoryItem.is_low_stock == True)
        )
        low_stock_count = low_stock_result.scalar() or 0
        
        return {
            "total_value": float(total_value),
            "total_items": total_items,
            "low_stock_count": low_stock_count,
        }

    async def get_stock_movements(
        self,
        item_id: int,
        days: int = 30
    ) -> List[StockMovement]:
        """Get stock movement history for an item."""
        since = datetime.utcnow() - timedelta(days=days)
        
        result = await self.db.execute(
            select(StockMovement)
            .where(StockMovement.item_id == item_id)
            .where(StockMovement.created_at >= since)
            .order_by(StockMovement.created_at.desc())
        )
        return result.scalars().all()
