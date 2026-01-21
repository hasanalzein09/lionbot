"""
Public API endpoints - No authentication required
For the customer-facing website: liondelivery-saida.com
"""
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.models.restaurant import Restaurant, RestaurantCategory
from app.models.menu import Menu, Category, MenuItem, MenuItemVariant

router = APIRouter()


def slugify(text: str) -> str:
    """Generate a slug from text"""
    return text.lower().replace(" ", "-").replace("&", "and")


# ==================== PUBLIC RESTAURANT ENDPOINTS ====================

@router.get("/restaurants/")
async def get_public_restaurants(
    db: AsyncSession = Depends(get_db),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    search: Optional[str] = Query(None, description="Search by name"),
    sort: str = Query("newest", description="Sort by: newest, name"),
    limit: int = Query(50, le=100),
    offset: int = Query(0),
) -> Any:
    """
    Get all active restaurants for the public website.
    No authentication required.
    """
    query = select(Restaurant).options(selectinload(Restaurant.category)).where(Restaurant.is_active == True)

    # Filter by category
    if category_id:
        query = query.where(Restaurant.category_id == category_id)

    # Search
    if search:
        search_term = f"%{search}%"
        query = query.where(
            (Restaurant.name.ilike(search_term)) |
            (Restaurant.name_ar.ilike(search_term))
        )

    # Sort
    if sort == "name":
        query = query.order_by(Restaurant.name)
    else:  # newest (default) - use id as proxy for creation time
        query = query.order_by(Restaurant.id.desc())

    # Pagination
    query = query.offset(offset).limit(limit)

    result = await db.execute(query)
    restaurants = result.scalars().all()

    # Format response
    return {
        "restaurants": [
            {
                "id": r.id,
                "name": r.name,
                "name_ar": r.name_ar,
                "slug": slugify(r.name),
                "description": r.description,
                "description_ar": r.description_ar,
                "image": r.logo_url,
                "category": r.category.name if r.category else None,
                "category_ar": r.category.name_ar if r.category else None,
                "category_id": r.category_id,
                "phone": r.phone_number,
            }
            for r in restaurants
        ],
        "total": len(restaurants),
        "has_more": len(restaurants) == limit,
    }


@router.get("/restaurants/{restaurant_id}")
async def get_public_restaurant(
    restaurant_id: int,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get a single restaurant by ID for the public website.
    No authentication required.
    """
    result = await db.execute(
        select(Restaurant)
        .options(selectinload(Restaurant.category))
        .where(Restaurant.id == restaurant_id, Restaurant.is_active == True)
    )
    restaurant = result.scalars().first()

    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    return {
        "id": restaurant.id,
        "name": restaurant.name,
        "name_ar": restaurant.name_ar,
        "slug": slugify(restaurant.name),
        "description": restaurant.description,
        "description_ar": restaurant.description_ar,
        "image": restaurant.logo_url,
        "category": restaurant.category.name if restaurant.category else None,
        "category_ar": restaurant.category.name_ar if restaurant.category else None,
        "category_id": restaurant.category_id,
        "phone": restaurant.phone_number,
    }


@router.get("/restaurants/slug/{slug}")
async def get_public_restaurant_by_slug(
    slug: str,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get a single restaurant by slug for the public website.
    No authentication required.
    """
    # Since we don't have a slug column, we search by name matching the slug pattern
    result = await db.execute(
        select(Restaurant)
        .options(selectinload(Restaurant.category))
        .where(Restaurant.is_active == True)
    )
    restaurants = result.scalars().all()

    # Find restaurant whose slugified name matches the slug
    restaurant = None
    for r in restaurants:
        if slugify(r.name) == slug:
            restaurant = r
            break

    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    return {
        "id": restaurant.id,
        "name": restaurant.name,
        "name_ar": restaurant.name_ar,
        "slug": slugify(restaurant.name),
        "description": restaurant.description,
        "description_ar": restaurant.description_ar,
        "image": restaurant.logo_url,
        "category": restaurant.category.name if restaurant.category else None,
        "category_ar": restaurant.category.name_ar if restaurant.category else None,
        "category_id": restaurant.category_id,
        "phone": restaurant.phone_number,
    }


# ==================== PUBLIC CATEGORIES ENDPOINTS ====================

@router.get("/categories/")
async def get_public_categories(
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get all restaurant categories for the public website.
    No authentication required.
    """
    result = await db.execute(
        select(RestaurantCategory)
        .where(RestaurantCategory.is_active == True)
        .order_by(RestaurantCategory.order)
    )
    categories = result.scalars().all()

    return [
        {
            "id": c.id,
            "name": c.name,
            "name_ar": c.name_ar,
            "icon": c.icon,
            "slug": slugify(c.name),
        }
        for c in categories
    ]


# ==================== PUBLIC MENU ENDPOINTS ====================

@router.get("/restaurants/{restaurant_id}/menu")
async def get_public_restaurant_menu(
    restaurant_id: int,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get the menu for a restaurant for the public website.
    No authentication required.
    """
    # Verify restaurant exists and is active
    rest_result = await db.execute(
        select(Restaurant).where(Restaurant.id == restaurant_id, Restaurant.is_active == True)
    )
    restaurant = rest_result.scalars().first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    # Get menu with categories and items
    result = await db.execute(
        select(Menu)
        .options(
            selectinload(Menu.categories)
            .selectinload(Category.items)
            .selectinload(MenuItem.variants)
        )
        .where(Menu.restaurant_id == restaurant_id, Menu.is_active == True)
    )
    menu = result.scalars().first()

    if not menu:
        return {"restaurant_id": restaurant_id, "categories": []}

    return {
        "restaurant_id": restaurant_id,
        "categories": [
            {
                "id": cat.id,
                "name": cat.name,
                "name_ar": cat.name_ar,
                "order": cat.order,
                "items": [
                    {
                        "id": item.id,
                        "name": item.name,
                        "name_ar": item.name_ar,
                        "description": item.description,
                        "description_ar": item.description_ar,
                        "price": float(item.price) if item.price else None,
                        "price_min": float(item.price_min) if item.price_min else None,
                        "price_max": float(item.price_max) if item.price_max else None,
                        "image": item.image_url,
                        "is_available": item.is_available,
                        "is_popular": item.is_popular,
                        "has_variants": item.has_variants,
                        "variants": [
                            {
                                "id": v.id,
                                "name": v.name,
                                "name_ar": v.name_ar,
                                "price": float(v.price),
                            }
                            for v in sorted(item.variants, key=lambda x: x.order or 0)
                        ] if item.variants else [],
                    }
                    for item in sorted(cat.items, key=lambda x: x.order or 0)
                    if item.is_available
                ]
            }
            for cat in sorted(menu.categories, key=lambda x: x.order or 0)
        ]
    }


# ==================== PUBLIC FEATURED ENDPOINTS ====================

@router.get("/featured/restaurants/")
async def get_featured_restaurants(
    db: AsyncSession = Depends(get_db),
    limit: int = Query(6, le=20),
) -> Any:
    """
    Get featured restaurants for the homepage.
    No authentication required.
    Since we don't have is_featured column, return the first N restaurants.
    """
    result = await db.execute(
        select(Restaurant)
        .options(selectinload(Restaurant.category))
        .where(Restaurant.is_active == True)
        .order_by(Restaurant.id)
        .limit(limit)
    )
    restaurants = result.scalars().all()

    return [
        {
            "id": r.id,
            "name": r.name,
            "name_ar": r.name_ar,
            "slug": slugify(r.name),
            "image": r.logo_url,
            "category": r.category.name if r.category else None,
            "category_ar": r.category.name_ar if r.category else None,
            "phone": r.phone_number,
        }
        for r in restaurants
    ]


# ==================== PUBLIC SEARCH ENDPOINT ====================

@router.get("/search/")
async def public_search(
    q: str = Query(..., min_length=2, description="Search query"),
    db: AsyncSession = Depends(get_db),
    limit: int = Query(20, le=50),
) -> Any:
    """
    Search restaurants and menu items.
    No authentication required.
    """
    search_term = f"%{q}%"

    # Search restaurants
    rest_result = await db.execute(
        select(Restaurant)
        .options(selectinload(Restaurant.category))
        .where(
            Restaurant.is_active == True,
            (Restaurant.name.ilike(search_term)) | (Restaurant.name_ar.ilike(search_term))
        )
        .limit(limit)
    )
    restaurants = rest_result.scalars().all()

    # Search menu items
    items_result = await db.execute(
        select(MenuItem)
        .options(selectinload(MenuItem.category).selectinload(Category.menu))
        .where(
            MenuItem.is_available == True,
            (MenuItem.name.ilike(search_term)) | (MenuItem.name_ar.ilike(search_term))
        )
        .limit(limit)
    )
    items = items_result.scalars().all()

    return {
        "restaurants": [
            {
                "id": r.id,
                "name": r.name,
                "name_ar": r.name_ar,
                "slug": slugify(r.name),
                "image": r.logo_url,
                "category": r.category.name if r.category else None,
                "category_ar": r.category.name_ar if r.category else None,
            }
            for r in restaurants
        ],
        "items": [
            {
                "id": item.id,
                "name": item.name,
                "name_ar": item.name_ar,
                "price": float(item.price) if item.price else None,
                "image": item.image_url,
                "restaurant_id": item.category.menu.restaurant_id if item.category and item.category.menu else None,
            }
            for item in items
            if item.category and item.category.menu
        ],
    }
