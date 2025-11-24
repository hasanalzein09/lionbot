from typing import Optional, List
from pydantic import BaseModel

# --- Menu Item ---
class MenuItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    image_url: Optional[str] = None
    is_available: Optional[bool] = True

class MenuItemCreate(MenuItemBase):
    category_id: int

class MenuItem(MenuItemBase):
    id: int
    category_id: int

    class Config:
        from_attributes = True

# --- Category ---
class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase):
    menu_id: int

class Category(CategoryBase):
    id: int
    items: List[MenuItem] = []

    class Config:
        from_attributes = True

# --- Menu ---
class MenuBase(BaseModel):
    name: str
    is_active: Optional[bool] = True

class MenuCreate(MenuBase):
    restaurant_id: int

class Menu(MenuBase):
    id: int
    restaurant_id: int
    categories: List[Category] = []

    class Config:
        from_attributes = True
