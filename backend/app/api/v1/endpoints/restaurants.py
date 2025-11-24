from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api import deps
from app.db.session import get_db
from app.models.restaurant import Restaurant
from app.models.user import User
from app.schemas.restaurant import Restaurant as RestaurantSchema, RestaurantCreate, RestaurantUpdate

router = APIRouter()

@router.get("/", response_model=List[RestaurantSchema])
async def read_restaurants(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Retrieve restaurants.
    """
    result = await db.execute(select(Restaurant).offset(skip).limit(limit))
    return result.scalars().all()

@router.post("/", response_model=RestaurantSchema)
async def create_restaurant(
    *,
    db: AsyncSession = Depends(get_db),
    restaurant_in: RestaurantCreate,
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Create new restaurant.
    """
    restaurant = Restaurant(**restaurant_in.model_dump())
    db.add(restaurant)
    await db.commit()
    await db.refresh(restaurant)
    return restaurant

@router.put("/{restaurant_id}", response_model=RestaurantSchema)
async def update_restaurant(
    *,
    db: AsyncSession = Depends(get_db),
    restaurant_id: int,
    restaurant_in: RestaurantUpdate,
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update a restaurant.
    """
    result = await db.execute(select(Restaurant).where(Restaurant.id == restaurant_id))
    restaurant = result.scalars().first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    
    update_data = restaurant_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(restaurant, field, value)
        
    db.add(restaurant)
    await db.commit()
    await db.refresh(restaurant)
    return restaurant
