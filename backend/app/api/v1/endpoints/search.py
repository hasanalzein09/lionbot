"""
Advanced Search API with filters
"""
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.models.restaurant import Restaurant
from app.models.menu import MenuItem

router = APIRouter()


@router.get("/restaurants")
async def search_restaurants(
    db: AsyncSession = Depends(get_db),
    q: Optional[str] = Query(None, description="Search query"),
    category: Optional[str] = Query(None, description="Category filter"),
    is_open: Optional[bool] = Query(None, description="Open now filter"),
    min_rating: Optional[float] = Query(None, ge=0, le=5),
    free_delivery: Optional[bool] = Query(None),
    sort_by: Optional[str] = Query("popular", description="Sort: popular, rating, distance, newest"),
    skip: int = 0,
    limit: int = 20,
) -> Any:
    """
    Search restaurants with multiple filters.
    """
    query = select(Restaurant).where(Restaurant.is_active == True)
    
    # Text search
    if q:
        search_filter = or_(
            Restaurant.name.ilike(f"%{q}%"),
            Restaurant.description.ilike(f"%{q}%"),
        )
        query = query.where(search_filter)
    
    # Category filter
    if category:
        query = query.where(Restaurant.category == category)
    
    # Open now (simplified - would need proper hours check)
    if is_open is not None:
        query = query.where(Restaurant.is_active == is_open)
    
    # Rating filter
    # Note: Would need to join with reviews for real rating
    
    # Sorting
    if sort_by == "rating":
        query = query.order_by(Restaurant.id.desc())  # Placeholder
    elif sort_by == "newest":
        query = query.order_by(Restaurant.id.desc())
    else:
        query = query.order_by(Restaurant.name)
    
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    restaurants = result.scalars().all()
    
    return {
        "count": len(restaurants),
        "restaurants": [
            {
                "id": r.id,
                "name": r.name,
                "description": r.description,
                "category": r.category,
                "is_active": r.is_active,
                "delivery_time": "30-45 min",  # Could calculate dynamically
                "delivery_fee": 2.0,
            }
            for r in restaurants
        ]
    }


@router.get("/menu-items")
async def search_menu_items(
    db: AsyncSession = Depends(get_db),
    q: Optional[str] = Query(None, description="Search query"),
    restaurant_id: Optional[int] = Query(None),
    category: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    is_available: bool = True,
    skip: int = 0,
    limit: int = 30,
) -> Any:
    """
    Search menu items across restaurants.
    """
    query = select(MenuItem).where(MenuItem.is_available == is_available)
    
    if q:
        search_filter = or_(
            MenuItem.name.ilike(f"%{q}%"),
            MenuItem.description.ilike(f"%{q}%"),
        )
        query = query.where(search_filter)
    
    if restaurant_id:
        query = query.where(MenuItem.restaurant_id == restaurant_id)
    
    if category:
        query = query.where(MenuItem.category == category)
    
    if min_price is not None:
        query = query.where(MenuItem.price >= min_price)
    
    if max_price is not None:
        query = query.where(MenuItem.price <= max_price)
    
    query = query.order_by(MenuItem.name).offset(skip).limit(limit)
    
    result = await db.execute(query)
    items = result.scalars().all()
    
    return {
        "count": len(items),
        "items": [
            {
                "id": i.id,
                "name": i.name,
                "description": i.description,
                "price": float(i.price),
                "category": i.category,
                "restaurant_id": i.restaurant_id,
                "is_available": i.is_available,
            }
            for i in items
        ]
    }


@router.get("/categories")
async def get_categories(
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get all restaurant categories with counts.
    """
    result = await db.execute(
        select(
            Restaurant.category,
            func.count(Restaurant.id).label("count")
        )
        .where(Restaurant.is_active == True)
        .group_by(Restaurant.category)
        .order_by(func.count(Restaurant.id).desc())
    )
    
    categories = []
    for row in result.all():
        if row[0]:  # Skip null categories
            categories.append({
                "name": row[0],
                "display_name": row[0].replace("_", " ").title(),
                "count": row[1],
                "emoji": get_category_emoji(row[0]),
            })
    
    return categories


def get_category_emoji(category: str) -> str:
    """Get emoji for category."""
    emoji_map = {
        "pizza": "🍕",
        "burgers": "🍔",
        "sushi": "🍣",
        "chinese": "🥡",
        "indian": "🍛",
        "mexican": "🌮",
        "italian": "🍝",
        "thai": "🍜",
        "desserts": "🍰",
        "coffee": "☕",
        "salads": "🥗",
        "seafood": "🦐",
        "steaks": "🥩",
        "vegan": "🥬",
        "breakfast": "🍳",
        "sandwiches": "🥪",
    }
    return emoji_map.get(category.lower(), "🍽️")


@router.get("/popular")
async def get_popular(
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get popular restaurants and items.
    """
    # Popular restaurants (would be based on order count in production)
    rest_result = await db.execute(
        select(Restaurant)
        .where(Restaurant.is_active == True)
        .order_by(Restaurant.id.desc())
        .limit(6)
    )
    restaurants = rest_result.scalars().all()
    
    # Popular items (would be based on order count)
    items_result = await db.execute(
        select(MenuItem)
        .where(MenuItem.is_available == True)
        .order_by(MenuItem.id.desc())
        .limit(10)
    )
    items = items_result.scalars().all()
    
    return {
        "popular_restaurants": [
            {"id": r.id, "name": r.name, "category": r.category}
            for r in restaurants
        ],
        "popular_items": [
            {"id": i.id, "name": i.name, "price": float(i.price), "restaurant_id": i.restaurant_id}
            for i in items
        ],
    }
