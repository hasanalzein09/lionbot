from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api import deps
from app.db.session import get_db
from app.models.menu import Menu, Category, MenuItem
from app.models.user import User, UserRole
from app.schemas.menu import (
    Menu as MenuSchema, MenuCreate, MenuUpdate,
    Category as CategorySchema, CategoryCreate, CategoryUpdate,
    MenuItem as MenuItemSchema, MenuItemCreate, MenuItemUpdate
)

router = APIRouter()

# ==================== HELPER FUNCTIONS ====================

def check_restaurant_access(user: User, restaurant_id: int) -> bool:
    """Check if user has access to this restaurant.
    Super Admin has access to all restaurants.
    Restaurant Manager only has access to their own restaurant.
    """
    if user.role == UserRole.SUPER_ADMIN:
        return True
    if user.role == UserRole.RESTAURANT_MANAGER:
        return user.restaurant_id == restaurant_id
    return False

async def verify_menu_access(db: AsyncSession, user: User, menu_id: int) -> Menu:
    """Verify user has access to this menu and return it."""
    result = await db.execute(select(Menu).where(Menu.id == menu_id))
    menu = result.scalars().first()
    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found")
    if not check_restaurant_access(user, menu.restaurant_id):
        raise HTTPException(status_code=403, detail="Access denied to this restaurant")
    return menu

async def verify_category_access(db: AsyncSession, user: User, category_id: int) -> Category:
    """Verify user has access to this category and return it."""
    result = await db.execute(
        select(Category).options(selectinload(Category.menu)).where(Category.id == category_id)
    )
    category = result.scalars().first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    if not check_restaurant_access(user, category.menu.restaurant_id):
        raise HTTPException(status_code=403, detail="Access denied to this restaurant")
    return category

# ==================== MENUS ====================

@router.get("/", response_model=List[MenuSchema])
async def read_all_menus(
    db: AsyncSession = Depends(get_db),
    restaurant_id: Optional[int] = Query(None),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get menus based on user role:
    - Super Admin: all menus or filtered by restaurant_id
    - Restaurant Manager: only their restaurant's menus
    """
    query = select(Menu).options(selectinload(Menu.categories).selectinload(Category.items))
    
    # Filter based on user role
    if current_user.role == UserRole.SUPER_ADMIN:
        if restaurant_id:
            query = query.where(Menu.restaurant_id == restaurant_id)
    elif current_user.role == UserRole.RESTAURANT_MANAGER:
        if current_user.restaurant_id:
            query = query.where(Menu.restaurant_id == current_user.restaurant_id)
        else:
            return []  # No restaurant assigned
    else:
        raise HTTPException(status_code=403, detail="Access denied")
    
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/", response_model=MenuSchema)
async def create_menu(
    *,
    db: AsyncSession = Depends(get_db),
    menu_in: MenuCreate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Create a new menu.
    - Super Admin: can create for any restaurant
    - Restaurant Manager: can only create for their own restaurant
    """
    # Verify access
    if not check_restaurant_access(current_user, menu_in.restaurant_id):
        raise HTTPException(status_code=403, detail="Access denied to this restaurant")
    
    menu = Menu(**menu_in.model_dump())
    db.add(menu)
    await db.commit()
    await db.refresh(menu)
    
    # Pre-initialize categories to avoid lazy loading issues during serialization
    result = await db.execute(
        select(Menu)
        .where(Menu.id == menu.id)
        .options(selectinload(Menu.categories))
    )
    return result.scalars().first()

@router.get("/restaurant/{restaurant_id}", response_model=List[MenuSchema])
async def read_menus_by_restaurant(
    restaurant_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Get menus for a specific restaurant."""
    if not check_restaurant_access(current_user, restaurant_id):
        raise HTTPException(status_code=403, detail="Access denied to this restaurant")
    
    result = await db.execute(
        select(Menu)
        .where(Menu.restaurant_id == restaurant_id)
        .options(selectinload(Menu.categories).selectinload(Category.items))
    )
    return result.scalars().all()

@router.get("/{menu_id}", response_model=MenuSchema)
async def read_menu(
    menu_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Get a specific menu by ID."""
    menu = await verify_menu_access(db, current_user, menu_id)
    # Reload with relationships
    result = await db.execute(
        select(Menu)
        .where(Menu.id == menu_id)
        .options(selectinload(Menu.categories).selectinload(Category.items))
    )
    return result.scalars().first()

@router.put("/{menu_id}", response_model=MenuSchema)
async def update_menu(
    menu_id: int,
    menu_in: MenuUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Update a menu."""
    menu = await verify_menu_access(db, current_user, menu_id)
    
    update_data = menu_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(menu, field, value)
    
    db.add(menu)
    await db.commit()
    await db.refresh(menu)
    return menu

@router.delete("/{menu_id}")
async def delete_menu(
    menu_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Delete a menu."""
    menu = await verify_menu_access(db, current_user, menu_id)
    
    await db.delete(menu)
    await db.commit()
    return {"message": "Menu deleted successfully"}

# ==================== CATEGORIES ====================

@router.get("/categories/", response_model=List[CategorySchema])
async def read_categories(
    db: AsyncSession = Depends(get_db),
    menu_id: Optional[int] = Query(None),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Get categories. If menu_id provided, verify access first."""
    if menu_id:
        await verify_menu_access(db, current_user, menu_id)
        query = select(Category).where(Category.menu_id == menu_id).options(selectinload(Category.items))
    else:
        if current_user.role == UserRole.SUPER_ADMIN:
            query = select(Category).options(selectinload(Category.items))
        elif current_user.role == UserRole.RESTAURANT_MANAGER and current_user.restaurant_id:
            query = (
                select(Category)
                .join(Menu)
                .where(Menu.restaurant_id == current_user.restaurant_id)
                .options(selectinload(Category.items))
            )
        else:
            raise HTTPException(status_code=403, detail="Access denied")
    
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/categories/", response_model=CategorySchema)
async def create_category(
    *,
    db: AsyncSession = Depends(get_db),
    category_in: CategoryCreate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Create a new category."""
    # Verify access to the menu
    await verify_menu_access(db, current_user, category_in.menu_id)
    
    category = Category(**category_in.model_dump())
    db.add(category)
    await db.commit()
    await db.refresh(category)
    
    # Reload with items to avoid serialization issues
    result = await db.execute(
        select(Category)
        .where(Category.id == category.id)
        .options(selectinload(Category.items))
    )
    return result.scalars().first()

@router.get("/categories/{category_id}", response_model=CategorySchema)
async def read_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Get a specific category by ID."""
    category = await verify_category_access(db, current_user, category_id)
    # Reload with items
    result = await db.execute(
        select(Category)
        .where(Category.id == category_id)
        .options(selectinload(Category.items))
    )
    return result.scalars().first()

@router.put("/categories/{category_id}", response_model=CategorySchema)
async def update_category(
    category_id: int,
    category_in: CategoryUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Update a category."""
    category = await verify_category_access(db, current_user, category_id)
    
    update_data = category_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(category, field, value)
    
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return category

@router.delete("/categories/{category_id}")
async def delete_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Delete a category."""
    category = await verify_category_access(db, current_user, category_id)
    
    await db.delete(category)
    await db.commit()
    return {"message": "Category deleted successfully"}

# ==================== MENU ITEMS ====================

async def verify_menu_item_access(db: AsyncSession, user: User, item_id: int) -> MenuItem:
    """Verify user has access to this menu item and return it."""
    result = await db.execute(
        select(MenuItem)
        .options(selectinload(MenuItem.category).selectinload(Category.menu))
        .where(MenuItem.id == item_id)
    )
    item = result.scalars().first()
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    if not check_restaurant_access(user, item.category.menu.restaurant_id):
        raise HTTPException(status_code=403, detail="Access denied to this restaurant")
    return item

@router.get("/items/", response_model=List[MenuItemSchema])
async def read_menu_items(
    db: AsyncSession = Depends(get_db),
    category_id: Optional[int] = Query(None),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Get menu items. If category_id provided, verify access first."""
    if category_id:
        await verify_category_access(db, current_user, category_id)
        query = select(MenuItem).where(MenuItem.category_id == category_id)
    else:
        if current_user.role == UserRole.SUPER_ADMIN:
            query = select(MenuItem)
        elif current_user.role == UserRole.RESTAURANT_MANAGER and current_user.restaurant_id:
            query = (
                select(MenuItem)
                .join(Category)
                .join(Menu)
                .where(Menu.restaurant_id == current_user.restaurant_id)
            )
        else:
            raise HTTPException(status_code=403, detail="Access denied")
    
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/items/", response_model=MenuItemSchema)
async def create_item(
    *,
    db: AsyncSession = Depends(get_db),
    item_in: MenuItemCreate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Create a new menu item."""
    # Verify access to the category
    await verify_category_access(db, current_user, item_in.category_id)
    
    item = MenuItem(**item_in.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item

@router.get("/items/{item_id}", response_model=MenuItemSchema)
async def read_menu_item(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Get a specific menu item by ID."""
    item = await verify_menu_item_access(db, current_user, item_id)
    return item

@router.put("/items/{item_id}", response_model=MenuItemSchema)
async def update_menu_item(
    item_id: int,
    item_in: MenuItemUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Update a menu item."""
    item = await verify_menu_item_access(db, current_user, item_id)
    
    update_data = item_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)
    
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item

@router.delete("/items/{item_id}")
async def delete_menu_item(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Delete a menu item."""
    item = await verify_menu_item_access(db, current_user, item_id)
    
    await db.delete(item)
    await db.commit()
    return {"message": "Menu item deleted successfully"}
