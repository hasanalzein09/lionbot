from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float, Numeric
from sqlalchemy.orm import relationship
from app.db.base_class import Base

# Use DECIMAL for financial precision
MONEY = Numeric(10, 2)
PERCENT = Numeric(5, 2)  # For percentage values like commission


class RestaurantCategory(Base):
    """Categories for restaurants (e.g., Offers, Snacks, Shawarma, Pizza, etc.)"""
    __tablename__ = "restaurant_category"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)  # English name
    name_ar = Column(String, nullable=False)  # Arabic name
    icon = Column(String, default="🍽️", nullable=False)  # Emoji icon
    order = Column(Integer, default=0, nullable=False)  # Display order
    is_active = Column(Boolean, default=True, nullable=False)

    # Don't cascade delete restaurants when category is deleted
    restaurants = relationship("Restaurant", back_populates="category")


class Restaurant(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)  # English name
    name_ar = Column(String, nullable=True)  # Arabic name
    description = Column(String, nullable=True)  # English description
    description_ar = Column(String, nullable=True)  # Arabic description
    logo_url = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)  # للإشعارات عبر WhatsApp
    is_active = Column(Boolean, default=True, nullable=False, index=True)

    # Restaurant Category - SET NULL on delete (don't delete restaurant if category is deleted)
    category_id = Column(Integer, ForeignKey("restaurant_category.id", ondelete="SET NULL"), nullable=True, index=True)
    category = relationship("RestaurantCategory", back_populates="restaurants")

    # Subscription details
    subscription_tier = Column(String, default="basic", nullable=False)  # basic, pro, enterprise
    commission_rate = Column(PERCENT, default=0.0, nullable=False)  # DECIMAL for percentage precision

    # Cascade delete branches and menus when restaurant is deleted
    branches = relationship("Branch", back_populates="restaurant", cascade="all, delete-orphan")
    menus = relationship("Menu", back_populates="restaurant", cascade="all, delete-orphan")


class Branch(Base):
    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurant.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String, nullable=False, index=True)  # e.g., "Downtown Branch"
    address = Column(String, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    phone_number = Column(String, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    restaurant = relationship("Restaurant", back_populates="branches")

