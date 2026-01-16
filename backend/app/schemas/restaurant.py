from typing import Optional, List
from pydantic import BaseModel

# Shared properties
class RestaurantBase(BaseModel):
    name: str
    name_ar: Optional[str] = None
    description: Optional[str] = None
    description_ar: Optional[str] = None
    logo_url: Optional[str] = None
    phone_number: Optional[str] = None  # للإشعارات عبر WhatsApp
    is_active: Optional[bool] = True
    subscription_tier: Optional[str] = "basic"
    commission_rate: Optional[float] = 0.0
    category_id: Optional[int] = None

# Properties to receive on creation
class RestaurantCreate(RestaurantBase):
    pass

# Properties to receive on update
class RestaurantUpdate(RestaurantBase):
    pass

# Properties to return to client
class Restaurant(RestaurantBase):
    id: int

    class Config:
        from_attributes = True

