"""
Customer Favorites System - Save favorite restaurants
"""
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from datetime import datetime

from app.db.session import get_db
from app.models.user import User
from app.models.restaurant import Restaurant
from app.api import deps

# Model
from sqlalchemy import Column, Integer, DateTime, ForeignKey, UniqueConstraint
from app.db.base_class import Base


router = APIRouter()


class Favorite(Base):
    __tablename__ = "favorites"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    restaurant_id = Column(Integer, ForeignKey("restaurant.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint('user_id', 'restaurant_id', name='unique_user_restaurant'),
    )


# ==================== Endpoints ====================

@router.get("")
async def get_favorites(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get user's favorite restaurants.
    """
    result = await db.execute(
        select(Favorite, Restaurant)
        .join(Restaurant, Favorite.restaurant_id == Restaurant.id)
        .where(Favorite.user_id == current_user.id)
        .order_by(Favorite.created_at.desc())
    )
    rows = result.all()
    
    return [
        {
            "id": fav.id,
            "restaurant": {
                "id": rest.id,
                "name": rest.name,
                "is_active": rest.is_active,
            },
            "added_at": fav.created_at.isoformat() if fav.created_at else None,
        }
        for fav, rest in rows
    ]


@router.post("/{restaurant_id}")
async def add_favorite(
    restaurant_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Add restaurant to favorites.
    """
    # Check restaurant exists
    result = await db.execute(
        select(Restaurant).where(Restaurant.id == restaurant_id)
    )
    if not result.scalars().first():
        raise HTTPException(status_code=404, detail="Restaurant not found")
    
    # Check if already favorite
    existing = await db.execute(
        select(Favorite).where(
            Favorite.user_id == current_user.id,
            Favorite.restaurant_id == restaurant_id
        )
    )
    if existing.scalars().first():
        raise HTTPException(status_code=400, detail="Already in favorites")
    
    favorite = Favorite(user_id=current_user.id, restaurant_id=restaurant_id)
    db.add(favorite)
    await db.commit()
    
    return {"message": "Added to favorites"}


@router.delete("/{restaurant_id}")
async def remove_favorite(
    restaurant_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Remove restaurant from favorites.
    """
    result = await db.execute(
        select(Favorite).where(
            Favorite.user_id == current_user.id,
            Favorite.restaurant_id == restaurant_id
        )
    )
    favorite = result.scalars().first()
    
    if not favorite:
        raise HTTPException(status_code=404, detail="Not in favorites")
    
    await db.delete(favorite)
    await db.commit()
    
    return {"message": "Removed from favorites"}


@router.get("/check/{restaurant_id}")
async def check_favorite(
    restaurant_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Check if restaurant is in favorites.
    """
    result = await db.execute(
        select(Favorite).where(
            Favorite.user_id == current_user.id,
            Favorite.restaurant_id == restaurant_id
        )
    )
    
    return {"is_favorite": result.scalars().first() is not None}
