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
    driver_id: Optional[int] = None
    status: OrderStatus
    total_amount: float
    delivery_fee: float
    created_at: datetime
    updated_at: Optional[datetime] = None
    items: List[OrderItem] = []

    class Config:
        from_attributes = True


# --- Detailed Order Item with name ---
class OrderItemDetailed(BaseModel):
    id: int
    menu_item_id: int
    name: str
    name_ar: Optional[str] = None
    quantity: int
    unit_price: float
    total_price: float


# --- Detailed Order Response ---
class OrderDetailed(BaseModel):
    id: int
    status: OrderStatus
    total_amount: float
    delivery_fee: float
    order_type: OrderType
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    # Related data
    restaurant_id: int
    restaurant_name: Optional[str] = None
    restaurant_name_ar: Optional[str] = None
    restaurant_phone: Optional[str] = None

    user_id: int
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None

    driver_id: Optional[int] = None
    driver_name: Optional[str] = None
    driver_phone: Optional[str] = None

    items: List[OrderItemDetailed] = []

    class Config:
        from_attributes = True

# --- Order Status Update ---
class OrderStatusUpdate(BaseModel):
    status: OrderStatus
    note: Optional[str] = None

# --- Order Assignment ---
class OrderDriverAssign(BaseModel):
    driver_id: int

