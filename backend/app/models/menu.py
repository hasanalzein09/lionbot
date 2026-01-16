from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float, Text, Numeric
from sqlalchemy.orm import relationship
from app.db.base_class import Base

# Use DECIMAL for financial precision (10 digits total, 2 decimal places)
MONEY = Numeric(10, 2)

class Menu(Base):
    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurant.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String, nullable=False, index=True)  # English name
    name_ar = Column(String, nullable=True)  # Arabic name
    is_active = Column(Boolean, default=True, nullable=False)
    order = Column(Integer, default=0, nullable=False)

    restaurant = relationship("Restaurant", back_populates="menus")
    # Cascade delete categories when menu is deleted
    categories = relationship("Category", back_populates="menu", cascade="all, delete-orphan")

class Category(Base):
    id = Column(Integer, primary_key=True, index=True)
    menu_id = Column(Integer, ForeignKey("menu.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String, nullable=False, index=True)  # English name
    name_ar = Column(String, nullable=True)  # Arabic name
    order = Column(Integer, default=0, nullable=False)

    menu = relationship("Menu", back_populates="categories")
    # Cascade delete menu items when category is deleted
    items = relationship("MenuItem", back_populates="category", cascade="all, delete-orphan")

class MenuItem(Base):
    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("category.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String, nullable=False, index=True)  # English name
    name_ar = Column(String, nullable=True)  # Arabic name
    description = Column(Text, nullable=True)  # English description
    description_ar = Column(Text, nullable=True)  # Arabic description

    # Price fields - DECIMAL for financial precision
    price = Column(MONEY, nullable=True)  # Single price (if no variants)
    price_min = Column(MONEY, nullable=True)  # Minimum price (if has variants)
    price_max = Column(MONEY, nullable=True)  # Maximum price (if has variants)
    has_variants = Column(Boolean, default=False, nullable=False)

    image_url = Column(String, nullable=True)
    is_available = Column(Boolean, default=True, nullable=False)
    order = Column(Integer, default=0, nullable=False)

    category = relationship("Category", back_populates="items")
    # Cascade delete variants when menu item is deleted
    variants = relationship("MenuItemVariant", back_populates="menu_item", cascade="all, delete-orphan")


class MenuItemVariant(Base):
    """Size/variant options for menu items (Small, Medium, Large, etc.)"""
    __tablename__ = "menuitemvariant"

    id = Column(Integer, primary_key=True, index=True)
    menu_item_id = Column(Integer, ForeignKey("menuitem.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String, nullable=False)  # "Small", "Medium", "Large"
    name_ar = Column(String, nullable=True)  # "صغير", "وسط", "كبير"
    price = Column(MONEY, nullable=False)  # DECIMAL for financial precision
    order = Column(Integer, default=0, nullable=False)  # Display order

    menu_item = relationship("MenuItem", back_populates="variants")
