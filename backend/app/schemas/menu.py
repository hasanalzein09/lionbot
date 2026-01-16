from typing import Optional, List
from pydantic import BaseModel

# --- Menu Item ---
class MenuItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    image_url: Optional[str] = None
    is_available: Optional[bool] = True
    order: Optional[int] = 0

class MenuItemCreate(MenuItemBase):
    category_id: int

class MenuItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    image_url: Optional[str] = None
    is_available: Optional[bool] = None
    order: Optional[int] = None

class MenuItem(MenuItemBase):
    id: int
    category_id: int

    class Config:
        from_attributes = True

# --- Category ---
class CategoryBase(BaseModel):
    name: str
    order: Optional[int] = 0

class CategoryCreate(CategoryBase):
    menu_id: int

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    order: Optional[int] = None

class Category(CategoryBase):
    id: int
    menu_id: int
    items: List[MenuItem] = []

    class Config:
        from_attributes = True

# --- Menu ---
class MenuBase(BaseModel):
    name: str
    is_active: Optional[bool] = True
    order: Optional[int] = 0

class MenuCreate(MenuBase):
    restaurant_id: int

class MenuUpdate(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None
    order: Optional[int] = None

class Menu(MenuBase):
    id: int
    restaurant_id: int
    categories: List[Category] = []

    class Config:
        from_attributes = True
