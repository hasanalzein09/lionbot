from typing import Optional
from pydantic import BaseModel, EmailStr
from app.models.user import UserRole

class UserBase(BaseModel):
    full_name: str
    email: Optional[EmailStr] = None
    phone_number: str
    is_active: Optional[bool] = True
    role: Optional[UserRole] = UserRole.CUSTOMER
    restaurant_id: Optional[int] = None

class UserCreate(UserBase):
    password: Optional[str] = None

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    is_active: Optional[bool] = None
    role: Optional[UserRole] = None
    restaurant_id: Optional[int] = None
    password: Optional[str] = None

class User(UserBase):
    id: int

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: Optional[int] = None

class DriverLocationUpdate(BaseModel):
    latitude: float
    longitude: float

class DriverStatusUpdate(BaseModel):
    is_active: bool
