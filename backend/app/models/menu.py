from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float, Text
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Menu(Base):
    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurant.id"))
    name = Column(String, index=True) # e.g., "Lunch Menu", "Dinner Menu"
    is_active = Column(Boolean, default=True)
    
    restaurant = relationship("Restaurant", back_populates="menus")
    categories = relationship("Category", back_populates="menu")

class Category(Base):
    id = Column(Integer, primary_key=True, index=True)
    menu_id = Column(Integer, ForeignKey("menu.id"))
    name = Column(String, index=True) # e.g., "Appetizers", "Main Course"
    
    menu = relationship("Menu", back_populates="categories")
    items = relationship("MenuItem", back_populates="category")

class MenuItem(Base):
    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("category.id"))
    name = Column(String, index=True)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    image_url = Column(String, nullable=True)
    is_available = Column(Boolean, default=True)
    
    category = relationship("Category", back_populates="items")
