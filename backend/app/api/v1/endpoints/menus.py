from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api import deps
from app.db.session import get_db
from app.models.menu import Menu, Category, MenuItem
from app.models.user import User
from app.schemas.menu import Menu as MenuSchema, MenuCreate, CategoryCreate, MenuItemCreate

router = APIRouter()

# --- Menus ---
@router.post("/", response_model=MenuSchema)
async def create_menu(
    *,
    db: AsyncSession = Depends(get_db),
    menu_in: MenuCreate,
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    menu = Menu(**menu_in.model_dump())
    db.add(menu)
    await db.commit()
    await db.refresh(menu)
    return menu

@router.get("/restaurant/{restaurant_id}", response_model=List[MenuSchema])
async def read_menus_by_restaurant(
    restaurant_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    result = await db.execute(
        select(Menu)
        .where(Menu.restaurant_id == restaurant_id)
        .options(selectinload(Menu.categories).selectinload(Category.items))
    )
    return result.scalars().all()

# --- Categories ---
@router.post("/categories", response_model=Any) # Use schema later
async def create_category(
    *,
    db: AsyncSession = Depends(get_db),
    category_in: CategoryCreate,
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    category = Category(**category_in.model_dump())
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return category

# --- Items ---
@router.post("/items", response_model=Any) # Use schema later
async def create_item(
    *,
    db: AsyncSession = Depends(get_db),
    item_in: MenuItemCreate,
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    item = MenuItem(**item_in.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item
