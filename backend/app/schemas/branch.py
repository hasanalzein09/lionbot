from typing import Optional
from pydantic import BaseModel

class BranchBase(BaseModel):
    name: str
    restaurant_id: int
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    phone_number: Optional[str] = None
    is_active: Optional[bool] = True

class BranchCreate(BranchBase):
    pass

class BranchUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    phone_number: Optional[str] = None
    is_active: Optional[bool] = None

class Branch(BranchBase):
    id: int

    class Config:
        from_attributes = True
