from typing import Optional, List
from pydantic import BaseModel

# Shared properties
class RestaurantBase(BaseModel):
    name: str
    description: Optional[str] = None
    logo_url: Optional[str] = None
    is_active: Optional[bool] = True
    subscription_tier: Optional[str] = "basic"
    commission_rate: Optional[float] = 0.0

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
