from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text

from app.api import deps
from app.db.session import get_db
from app.models.restaurant import Restaurant, RestaurantCategory
from app.models.user import User
from app.schemas.restaurant import Restaurant as RestaurantSchema, RestaurantCreate, RestaurantUpdate
from app.services.audit_service import get_audit_service

router = APIRouter()


# ============ CLEANUP (Admin Only) ============
@router.delete("/cleanup/all")
async def cleanup_all_restaurants(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Delete ALL restaurants and related data (Admin only).
    USE WITH CAUTION!
    """
    # Delete in order of dependencies (using correct SQLAlchemy table names)
    await db.execute(text("DELETE FROM orderitem"))
    await db.execute(text("DELETE FROM \"order\""))
    await db.execute(text("DELETE FROM menuitem"))
    await db.execute(text("DELETE FROM category"))
    await db.execute(text("DELETE FROM menu"))
    await db.execute(text("DELETE FROM branch"))
    await db.execute(text("DELETE FROM restaurant"))
    await db.commit()

    return {"message": "All restaurants and related data deleted successfully"}


# ============ CATEGORIES ============
@router.get("/categories/", response_model=List[dict])
async def read_restaurant_categories(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Retrieve all restaurant categories.
    """
    result = await db.execute(
        select(RestaurantCategory)
        .where(RestaurantCategory.is_active == True)
        .order_by(RestaurantCategory.order)
    )
    categories = result.scalars().all()
    return [{"id": c.id, "name": c.name, "name_ar": c.name_ar, "icon": c.icon} for c in categories]

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
    request: Request,
    db: AsyncSession = Depends(get_db),
    restaurant_in: RestaurantCreate,
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Create new restaurant.
    """
    restaurant = Restaurant(**restaurant_in.model_dump())
    db.add(restaurant)
    await db.flush()

    # Audit log
    audit = get_audit_service(db)
    await audit.log_create(
        entity_type="restaurant",
        entity_id=restaurant.id,
        new_values=restaurant_in.model_dump(),
        user=current_user,
        request=request,
    )

    await db.commit()
    await db.refresh(restaurant)
    return restaurant

@router.get("/{restaurant_id}", response_model=RestaurantSchema)
async def read_restaurant(
    *,
    db: AsyncSession = Depends(get_db),
    restaurant_id: int,
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Get a specific restaurant by ID.
    """
    result = await db.execute(select(Restaurant).where(Restaurant.id == restaurant_id))
    restaurant = result.scalars().first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return restaurant

@router.put("/{restaurant_id}", response_model=RestaurantSchema)
async def update_restaurant(
    *,
    request: Request,
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

    # Capture old values for audit
    old_values = {
        "name": restaurant.name,
        "name_ar": restaurant.name_ar,
        "description": restaurant.description,
        "is_active": restaurant.is_active,
        "commission_rate": float(restaurant.commission_rate) if restaurant.commission_rate else None,
    }

    update_data = restaurant_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(restaurant, field, value)

    # Audit log
    audit = get_audit_service(db)
    await audit.log_update(
        entity_type="restaurant",
        entity_id=restaurant_id,
        old_values=old_values,
        new_values=update_data,
        user=current_user,
        request=request,
    )

    db.add(restaurant)
    await db.commit()
    await db.refresh(restaurant)
    return restaurant


@router.delete("/{restaurant_id}")
async def delete_restaurant(
    *,
    request: Request,
    db: AsyncSession = Depends(get_db),
    restaurant_id: int,
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Delete a restaurant.
    """
    result = await db.execute(select(Restaurant).where(Restaurant.id == restaurant_id))
    restaurant = result.scalars().first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    # Capture values for audit before deletion
    old_values = {
        "id": restaurant.id,
        "name": restaurant.name,
        "name_ar": restaurant.name_ar,
    }

    # Audit log
    audit = get_audit_service(db)
    await audit.log_delete(
        entity_type="restaurant",
        entity_id=restaurant_id,
        old_values=old_values,
        user=current_user,
        request=request,
    )

    await db.delete(restaurant)
    await db.commit()
    return {"message": "Restaurant deleted successfully"}

