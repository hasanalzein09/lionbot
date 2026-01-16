"""
Customer Address Management
"""
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from pydantic import BaseModel
from datetime import datetime

from app.db.session import get_db
from app.models.user import User
from app.api import deps

# Model
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from app.db.base_class import Base


router = APIRouter()


class Address(Base):
    __tablename__ = "addresses"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    label = Column(String(50), nullable=False)  # "Home", "Work", etc.
    address = Column(String(500), nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


# ==================== Schemas ====================

class AddressCreate(BaseModel):
    label: str
    address: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_default: bool = False


class AddressUpdate(BaseModel):
    label: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_default: Optional[bool] = None


# ==================== Endpoints ====================

@router.get("")
async def get_addresses(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get user's saved addresses.
    """
    result = await db.execute(
        select(Address)
        .where(Address.user_id == current_user.id)
        .order_by(Address.is_default.desc(), Address.created_at.desc())
    )
    addresses = result.scalars().all()
    
    return [
        {
            "id": a.id,
            "label": a.label,
            "address": a.address,
            "latitude": a.latitude,
            "longitude": a.longitude,
            "is_default": a.is_default,
        }
        for a in addresses
    ]


@router.post("", status_code=201)
async def create_address(
    address_in: AddressCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Add new address.
    """
    # If setting as default, unset other defaults
    if address_in.is_default:
        await db.execute(
            update(Address)
            .where(Address.user_id == current_user.id)
            .values(is_default=False)
        )
    
    address = Address(
        user_id=current_user.id,
        label=address_in.label,
        address=address_in.address,
        latitude=address_in.latitude,
        longitude=address_in.longitude,
        is_default=address_in.is_default,
    )
    
    db.add(address)
    await db.commit()
    await db.refresh(address)
    
    return {"message": "Address added", "address_id": address.id}


@router.put("/{address_id}")
async def update_address(
    address_id: int,
    address_in: AddressUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Update an address.
    """
    result = await db.execute(
        select(Address).where(
            Address.id == address_id,
            Address.user_id == current_user.id
        )
    )
    address = result.scalars().first()
    
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")
    
    # If setting as default, unset other defaults
    if address_in.is_default:
        await db.execute(
            update(Address)
            .where(Address.user_id == current_user.id, Address.id != address_id)
            .values(is_default=False)
        )
    
    update_data = address_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(address, field, value)
    
    db.add(address)
    await db.commit()
    
    return {"message": "Address updated"}


@router.delete("/{address_id}")
async def delete_address(
    address_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Delete an address.
    """
    result = await db.execute(
        select(Address).where(
            Address.id == address_id,
            Address.user_id == current_user.id
        )
    )
    address = result.scalars().first()
    
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")
    
    await db.delete(address)
    await db.commit()
    
    return {"message": "Address deleted"}


@router.post("/{address_id}/set-default")
async def set_default_address(
    address_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Set address as default.
    """
    result = await db.execute(
        select(Address).where(
            Address.id == address_id,
            Address.user_id == current_user.id
        )
    )
    address = result.scalars().first()

    if not address:
        raise HTTPException(status_code=404, detail="Address not found")

    # Unset all defaults
    await db.execute(
        update(Address)
        .where(Address.user_id == current_user.id)
        .values(is_default=False)
    )

    # Set this as default
    address.is_default = True
    db.add(address)
    await db.commit()

    return {"message": "Default address set"}


# ==================== Admin Endpoints ====================

@router.get("/user/{user_id}")
async def get_user_addresses(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Get addresses for a specific user (Admin only).
    """
    result = await db.execute(
        select(Address)
        .where(Address.user_id == user_id)
        .order_by(Address.is_default.desc(), Address.created_at.desc())
    )
    addresses = result.scalars().all()

    return [
        {
            "id": a.id,
            "label": a.label,
            "address": a.address,
            "latitude": a.latitude,
            "longitude": a.longitude,
            "is_default": a.is_default,
        }
        for a in addresses
    ]


@router.post("/user/{user_id}", status_code=201)
async def create_user_address(
    user_id: int,
    address_in: AddressCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Add address for a specific user (Admin only).
    """
    # Verify user exists
    user_result = await db.execute(select(User).where(User.id == user_id))
    if not user_result.scalars().first():
        raise HTTPException(status_code=404, detail="User not found")

    # If setting as default, unset other defaults
    if address_in.is_default:
        await db.execute(
            update(Address)
            .where(Address.user_id == user_id)
            .values(is_default=False)
        )

    address = Address(
        user_id=user_id,
        label=address_in.label,
        address=address_in.address,
        latitude=address_in.latitude,
        longitude=address_in.longitude,
        is_default=address_in.is_default,
    )

    db.add(address)
    await db.commit()
    await db.refresh(address)

    return {"message": "Address added", "address_id": address.id}


@router.put("/admin/{address_id}")
async def update_address_admin(
    address_id: int,
    address_in: AddressUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update any address (Admin only).
    """
    result = await db.execute(
        select(Address).where(Address.id == address_id)
    )
    address = result.scalars().first()

    if not address:
        raise HTTPException(status_code=404, detail="Address not found")

    # If setting as default, unset other defaults for that user
    if address_in.is_default:
        await db.execute(
            update(Address)
            .where(Address.user_id == address.user_id, Address.id != address_id)
            .values(is_default=False)
        )

    update_data = address_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(address, field, value)

    db.add(address)
    await db.commit()

    return {"message": "Address updated"}


@router.delete("/admin/{address_id}")
async def delete_address_admin(
    address_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Delete any address (Admin only).
    """
    result = await db.execute(
        select(Address).where(Address.id == address_id)
    )
    address = result.scalars().first()

    if not address:
        raise HTTPException(status_code=404, detail="Address not found")

    await db.delete(address)
    await db.commit()

    return {"message": "Address deleted"}
