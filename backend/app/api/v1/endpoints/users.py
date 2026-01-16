from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api import deps
from app.db.session import get_db
from app.models.user import User, UserRole
from app.schemas.user import User as UserSchema, UserCreate, UserUpdate, DriverLocationUpdate, DriverStatusUpdate
from app.core.security import get_password_hash
from app.core.validators import (
    validate_phone_number, validate_email, validate_name,
    validate_coordinates, validate_positive_integer, sanitize_text
)

router = APIRouter()

@router.get("/me", response_model=UserSchema)
async def read_current_user(
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get current logged-in user.
    """
    return current_user

@router.get("/", response_model=List[UserSchema])
async def read_users(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    role: Optional[str] = None,
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Retrieve users. Optionally filter by role.
    """
    query = select(User)
    
    if role:
        query = query.where(User.role == role)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/drivers", response_model=List[UserSchema])
async def read_drivers(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = True,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Retrieve all drivers.
    """
    query = select(User).where(User.role == UserRole.DRIVER)
    
    if is_active is not None:
        query = query.where(User.is_active == is_active)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/managers", response_model=List[UserSchema])
async def read_managers(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Retrieve all restaurant managers.
    """
    result = await db.execute(
        select(User)
        .where(User.role == UserRole.RESTAURANT_MANAGER)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

@router.get("/{user_id}", response_model=UserSchema)
async def read_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Get user by ID.
    """
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/", response_model=UserSchema)
async def create_user(
    *,
    db: AsyncSession = Depends(get_db),
    user_in: UserCreate,
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Create new user (driver, manager, etc.)
    Validates all inputs before processing.
    """
    # Validate inputs
    validate_name(user_in.full_name)
    is_valid, normalized_phone = validate_phone_number(user_in.phone_number)
    if user_in.email:
        validate_email(user_in.email)

    # Sanitize name
    sanitized_name = sanitize_text(user_in.full_name, max_length=100)

    # Check if email exists (using lowercased email)
    normalized_email = user_in.email.lower() if user_in.email else None
    if normalized_email:
        result = await db.execute(
            select(User).where(User.email == normalized_email)
        )
        if result.scalars().first():
            raise HTTPException(status_code=400, detail="Email already registered")

    # Check if phone exists (using normalized phone)
    result = await db.execute(
        select(User).where(User.phone_number == normalized_phone)
    )
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Phone number already registered")

    user_data = user_in.model_dump(exclude={"password"})
    user_data["full_name"] = sanitized_name
    user_data["phone_number"] = normalized_phone
    user_data["email"] = normalized_email
    user_data["hashed_password"] = get_password_hash(user_in.password) if user_in.password else None

    user = User(**user_data)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

@router.put("/{user_id}", response_model=UserSchema)
async def update_user(
    *,
    db: AsyncSession = Depends(get_db),
    user_id: int,
    user_in: UserUpdate,
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update a user.
    """
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = user_in.model_dump(exclude_unset=True, exclude={"password"})
    
    if user_in.password:
        update_data["hashed_password"] = get_password_hash(user_in.password)
    
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Delete a user (deactivate).
    """
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Soft delete - just deactivate
    user.is_active = False
    db.add(user)
    await db.commit()
    
    return {"message": "User deactivated successfully"}

@router.patch("/{user_id}/activate")
async def activate_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Activate a user.
    """
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_active = True
    db.add(user)
    await db.commit()
    
    return {"message": "User activated successfully"}

@router.patch("/drivers/{driver_id}/location")
async def update_driver_location(
    *,
    db: AsyncSession = Depends(get_db),
    driver_id: int,
    location_in: DriverLocationUpdate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Update driver's current location.
    Validates coordinates before saving.
    """
    # Validate coordinates
    validate_coordinates(location_in.latitude, location_in.longitude)

    result = await db.execute(select(User).where(User.id == driver_id))
    driver = result.scalars().first()
    if not driver or driver.role != UserRole.DRIVER:
        raise HTTPException(status_code=404, detail="Driver not found")

    # Check if user is updating their own location or is an admin
    if current_user.id != driver_id and current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized to update this driver's location")

    driver.last_latitude = location_in.latitude
    driver.last_longitude = location_in.longitude
    db.add(driver)
    await db.commit()

    return {"message": "Location updated"}

@router.patch("/drivers/{driver_id}/status")
async def update_driver_status(
    *,
    db: AsyncSession = Depends(get_db),
    driver_id: int,
    status_in: DriverStatusUpdate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Update driver's online/offline status.
    """
    result = await db.execute(select(User).where(User.id == driver_id))
    driver = result.scalars().first()
    if not driver or driver.role != UserRole.DRIVER:
        raise HTTPException(status_code=404, detail="Driver not found")
    
    if current_user.id != driver_id and current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=400, detail="Not enough privileges")

    driver.is_active = status_in.is_active
    db.add(driver)
    await db.commit()
    
    return {"status": "success", "is_active": driver.is_active}
