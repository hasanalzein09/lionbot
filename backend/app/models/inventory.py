from sqlalchemy import Column, Integer, Float, String, Boolean, ForeignKey, DateTime, Enum as SQLEnum, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.db.base_class import Base


class InventoryUnit(str, enum.Enum):
    """Units of measurement for inventory items."""
    PIECES = "pieces"
    KG = "kg"
    GRAMS = "grams"
    LITERS = "liters"
    ML = "ml"
    BOXES = "boxes"
    PACKS = "packs"


class StockMovementType(str, enum.Enum):
    """Types of stock movements."""
    PURCHASE = "purchase"      # Stock added from supplier
    SALE = "sale"              # Stock used in order
    ADJUSTMENT = "adjustment"  # Manual adjustment
    WASTE = "waste"            # Expired/damaged
    TRANSFER = "transfer"      # Between branches
    RETURN = "return"          # Returned to supplier


class InventoryItem(Base):
    """Inventory item (ingredient/supply) for a restaurant."""
    __tablename__ = "inventory_items"
    
    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurant.id"), index=True)
    
    # Basic Info
    name = Column(String, nullable=False)
    name_ar = Column(String)
    sku = Column(String, index=True)  # Stock Keeping Unit
    barcode = Column(String, index=True)
    category = Column(String)
    
    # Stock Info
    unit = Column(SQLEnum(InventoryUnit), default=InventoryUnit.PIECES)
    current_quantity = Column(Float, default=0)
    min_quantity = Column(Float, default=10)  # Alert threshold
    max_quantity = Column(Float, nullable=True)  # Optimal max stock
    
    # Cost
    cost_per_unit = Column(Float, default=0)
    last_purchase_price = Column(Float)
    average_cost = Column(Float, default=0)
    
    # Meta
    supplier_name = Column(String)
    supplier_phone = Column(String)
    notes = Column(Text)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_low_stock = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_restocked_at = Column(DateTime)
    
    # Relationships
    restaurant = relationship("Restaurant", backref="inventory_items")
    movements = relationship("StockMovement", back_populates="item")
    alerts = relationship("InventoryAlert", back_populates="item")


class StockMovement(Base):
    """Record of stock movement (in/out)."""
    __tablename__ = "stock_movements"
    
    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("inventory_items.id"), index=True)
    
    type = Column(SQLEnum(StockMovementType))
    quantity = Column(Float)  # Positive for in, negative for out
    quantity_before = Column(Float)
    quantity_after = Column(Float)
    
    # Cost tracking
    unit_cost = Column(Float)
    total_cost = Column(Float)
    
    # Reference
    reference_type = Column(String)  # "order", "manual", "supplier"
    reference_id = Column(Integer)   # Order ID, etc.
    
    # Details
    notes = Column(Text)
    performed_by = Column(Integer, ForeignKey("user.id"))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    item = relationship("InventoryItem", back_populates="movements")
    user = relationship("User", backref="stock_movements")


class InventoryAlert(Base):
    """Low stock and expiry alerts."""
    __tablename__ = "inventory_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("inventory_items.id"), index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurant.id"), index=True)
    
    alert_type = Column(String)  # "low_stock", "out_of_stock", "expiring"
    message = Column(String)
    message_ar = Column(String)
    
    # Status
    is_read = Column(Boolean, default=False)
    is_resolved = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime)
    
    # Relationships
    item = relationship("InventoryItem", back_populates="alerts")


class SupplierOrder(Base):
    """Order placed to suppliers for restocking."""
    __tablename__ = "supplier_orders"
    
    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurant.id"), index=True)
    
    # Supplier
    supplier_name = Column(String)
    supplier_phone = Column(String)
    supplier_email = Column(String)
    
    # Order details
    order_number = Column(String, unique=True)
    status = Column(String, default="pending")  # pending, ordered, shipped, received, cancelled
    
    # Totals
    subtotal = Column(Float, default=0)
    tax = Column(Float, default=0)
    total = Column(Float, default=0)
    
    # Notes
    notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    ordered_at = Column(DateTime)
    expected_delivery = Column(DateTime)
    received_at = Column(DateTime)
    
    # Relationships
    items = relationship("SupplierOrderItem", back_populates="order")


class SupplierOrderItem(Base):
    """Item in a supplier order."""
    __tablename__ = "supplier_order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("supplier_orders.id"), index=True)
    item_id = Column(Integer, ForeignKey("inventory_items.id"))
    
    quantity_ordered = Column(Float)
    quantity_received = Column(Float, default=0)
    unit_price = Column(Float)
    total_price = Column(Float)
    
    # Relationships
    order = relationship("SupplierOrder", back_populates="items")
    item = relationship("InventoryItem")
