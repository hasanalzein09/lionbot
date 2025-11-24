from sqlalchemy import Boolean, Column, Integer, String, Enum
from app.db.base_class import Base
import enum

class UserRole(str, enum.Enum):
    SUPER_ADMIN = "super_admin"
    RESTAURANT_MANAGER = "restaurant_manager"
    DRIVER = "driver"
    CUSTOMER = "customer"

class User(Base):
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True)
    email = Column(String, unique=True, index=True, nullable=True)
    phone_number = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True) # Nullable for customers who might just use OTP
    is_active = Column(Boolean(), default=True)
    role = Column(Enum(UserRole), default=UserRole.CUSTOMER)
