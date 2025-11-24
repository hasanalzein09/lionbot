from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime, Enum
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from datetime import datetime
import enum

class OrderStatus(str, enum.Enum):
    NEW = "new"
    ACCEPTED = "accepted"
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
    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurant.id"))
    user_id = Column(Integer, ForeignKey("user.id")) # The customer
    driver_id = Column(Integer, ForeignKey("user.id"), nullable=True)
    
    status = Column(Enum(OrderStatus), default=OrderStatus.NEW, index=True)
    order_type = Column(Enum(OrderType), default=OrderType.DELIVERY)
    
    total_amount = Column(Float, default=0.0)
    delivery_fee = Column(Float, default=0.0)
    
    address = Column(String, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    restaurant = relationship("Restaurant")
    customer = relationship("User", foreign_keys=[user_id])
    driver = relationship("User", foreign_keys=[driver_id])
    items = relationship("OrderItem", back_populates="order")

class OrderItem(Base):
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("order.id"))
    menu_item_id = Column(Integer, ForeignKey("menuitem.id"))
    
    quantity = Column(Integer, default=1)
    unit_price = Column(Float, nullable=False) # Price at time of order
    total_price = Column(Float, nullable=False)
    
    order = relationship("Order", back_populates="items")
    menu_item = relationship("MenuItem")
