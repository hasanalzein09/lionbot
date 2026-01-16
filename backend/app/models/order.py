from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime, Enum, Numeric, Index
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from datetime import datetime
import enum

# Use DECIMAL for financial precision (10 digits total, 2 decimal places)
MONEY = Numeric(10, 2)

class OrderStatus(str, enum.Enum):
    NEW = "new"
    ACCEPTED = "accepted"
    CONFIRMED = "confirmed" # Consistency with some frontends
    PREPARING = "preparing"
    READY = "ready"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class OrderType(str, enum.Enum):
    DELIVERY = "delivery"
    PICKUP = "pickup"
    DINE_IN = "dine_in"

class Order(Base):
    __table_args__ = (
        # Composite indexes for common query patterns
        Index('ix_order_restaurant_status', 'restaurant_id', 'status'),  # Restaurant order listing
        Index('ix_order_user_created', 'user_id', 'created_at'),  # Customer order history
        Index('ix_order_driver_status', 'driver_id', 'status'),  # Driver active orders
    )

    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurant.id", ondelete="SET NULL"), nullable=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="SET NULL"), nullable=True, index=True)  # The customer
    driver_id = Column(Integer, ForeignKey("user.id", ondelete="SET NULL"), nullable=True, index=True)

    status = Column(Enum(OrderStatus), default=OrderStatus.NEW, nullable=False, index=True)
    order_type = Column(Enum(OrderType), default=OrderType.DELIVERY, nullable=False)

    total_amount = Column(MONEY, default=0.0, nullable=False)  # DECIMAL for financial precision
    delivery_fee = Column(MONEY, default=0.0, nullable=False)  # DECIMAL for financial precision

    address = Column(String, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    restaurant = relationship("Restaurant")
    customer = relationship("User", foreign_keys=[user_id])
    driver = relationship("User", foreign_keys=[driver_id])
    # Cascade delete order items when order is deleted
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

class OrderItem(Base):
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("order.id", ondelete="CASCADE"), nullable=False, index=True)
    menu_item_id = Column(Integer, ForeignKey("menuitem.id", ondelete="SET NULL"), nullable=True, index=True)

    quantity = Column(Integer, default=1, nullable=False)
    unit_price = Column(MONEY, nullable=False)  # DECIMAL - Price at time of order
    total_price = Column(MONEY, nullable=False)  # DECIMAL for financial precision

    order = relationship("Order", back_populates="items")
    menu_item = relationship("MenuItem")
