from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from app.models.order import OrderStatus, OrderType

# --- Order Item ---
class OrderItemBase(BaseModel):
    menu_item_id: int
    quantity: int

class OrderItemCreate(OrderItemBase):
    pass

class OrderItem(OrderItemBase):
    id: int
    order_id: int
    unit_price: float
    total_price: float

    class Config:
        from_attributes = True

# --- Order ---
class OrderBase(BaseModel):
    restaurant_id: int
    order_type: OrderType = OrderType.DELIVERY
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class OrderCreate(OrderBase):
    items: List[OrderItemCreate]

class Order(OrderBase):
    id: int
    user_id: int
    status: OrderStatus
    total_amount: float
    delivery_fee: float
    created_at: datetime
    items: List[OrderItem] = []

    class Config:
        from_attributes = True
