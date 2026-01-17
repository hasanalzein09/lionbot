from sqlalchemy import Boolean, Column, Integer, String, Enum, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.db.base_class import Base
import enum

class UserRole(str, enum.Enum):
    SUPER_ADMIN = "super_admin"
    RESTAURANT_MANAGER = "restaurant_manager"
    DRIVER = "driver"
    CUSTOMER = "customer"

class User(Base):
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=True, index=True)
    email = Column(String, unique=True, index=True, nullable=True)
    phone_number = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True)
    is_active = Column(Boolean(), default=True, nullable=False, index=True)  # Index for active user filtering
    role = Column(Enum(UserRole), default=UserRole.CUSTOMER, nullable=False, index=True)  # Index for role-based queries
    # SET NULL when restaurant is deleted - user remains but loses restaurant association
    restaurant_id = Column(Integer, ForeignKey("restaurant.id", ondelete="SET NULL"), nullable=True, index=True)

    # Store customer data for persistence
    default_address = Column(String, nullable=True)
    last_latitude = Column(Float, nullable=True)
    last_longitude = Column(Float, nullable=True)

    # FCM token for push notifications
    fcm_token = Column(String, nullable=True)
