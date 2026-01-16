"""
Menu Item Customizations/Add-ons API
"""
from typing import Any, Optional, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from datetime import datetime

from app.db.session import get_db
from app.models.user import User
from app.api import deps

# Models
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.base_class import Base


router = APIRouter()


class CustomizationGroup(Base):
    """Group of customizations (e.g., "Size", "Extras", "Sauce")"""
    __tablename__ = "customization_groups"
    
    id = Column(Integer, primary_key=True, index=True)
    menu_item_id = Column(Integer, ForeignKey("menuitem.id"), nullable=False)
    name = Column(String(100), nullable=False)  # "Size", "Add-ons"
    name_ar = Column(String(100), nullable=True)
    selection_type = Column(String(20), default="single")  # single, multiple
    is_required = Column(Boolean, default=False)
    min_selections = Column(Integer, default=0)
    max_selections = Column(Integer, nullable=True)  # Null = unlimited
    position = Column(Integer, default=0)


class CustomizationOption(Base):
    """Individual options within a group"""
    __tablename__ = "customization_options"
    
    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("customization_groups.id"), nullable=False)
    name = Column(String(100), nullable=False)
    name_ar = Column(String(100), nullable=True)
    price_adjustment = Column(Float, default=0)  # Extra cost
    is_default = Column(Boolean, default=False)
    is_available = Column(Boolean, default=True)
    position = Column(Integer, default=0)


# Schemas
class OptionCreate(BaseModel):
    name: str
    name_ar: Optional[str] = None
    price_adjustment: float = 0
    is_default: bool = False


class GroupCreate(BaseModel):
    menu_item_id: int
    name: str
    name_ar: Optional[str] = None
    selection_type: str = "single"
    is_required: bool = False
    min_selections: int = 0
    max_selections: Optional[int] = None
    options: List[OptionCreate] = []


# ==================== Endpoints ====================

@router.get("/menu-item/{menu_item_id}")
async def get_customizations(
    menu_item_id: int,
    db: AsyncSession = Depends(get_db),
    lang: str = "en",
) -> Any:
    """
    Get customization options for a menu item.
    """
    result = await db.execute(
        select(CustomizationGroup)
        .where(CustomizationGroup.menu_item_id == menu_item_id)
        .order_by(CustomizationGroup.position)
    )
    groups = result.scalars().all()
    
    response = []
    for group in groups:
        # Get options for this group
        options_result = await db.execute(
            select(CustomizationOption)
            .where(
                CustomizationOption.group_id == group.id,
                CustomizationOption.is_available == True
            )
            .order_by(CustomizationOption.position)
        )
        options = options_result.scalars().all()
        
        response.append({
            "id": group.id,
            "name": group.name_ar if lang == "ar" and group.name_ar else group.name,
            "selection_type": group.selection_type,
            "is_required": group.is_required,
            "min_selections": group.min_selections,
            "max_selections": group.max_selections,
            "options": [
                {
                    "id": o.id,
                    "name": o.name_ar if lang == "ar" and o.name_ar else o.name,
                    "price_adjustment": o.price_adjustment,
                    "is_default": o.is_default,
                }
                for o in options
            ],
        })
    
    return response


@router.post("/groups")
async def create_customization_group(
    group_in: GroupCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Create a customization group with options (Admin).
    """
    # Create group
    group = CustomizationGroup(
        menu_item_id=group_in.menu_item_id,
        name=group_in.name,
        name_ar=group_in.name_ar,
        selection_type=group_in.selection_type,
        is_required=group_in.is_required,
        min_selections=group_in.min_selections,
        max_selections=group_in.max_selections,
    )
    db.add(group)
    await db.commit()
    await db.refresh(group)
    
    # Create options
    for i, opt in enumerate(group_in.options):
        option = CustomizationOption(
            group_id=group.id,
            name=opt.name,
            name_ar=opt.name_ar,
            price_adjustment=opt.price_adjustment,
            is_default=opt.is_default,
            position=i,
        )
        db.add(option)
    
    await db.commit()
    
    return {"message": "Customization group created", "group_id": group.id}


@router.post("/options/{group_id}")
async def add_option(
    group_id: int,
    option_in: OptionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Add option to existing group (Admin).
    """
    # Check group exists
    result = await db.execute(
        select(CustomizationGroup).where(CustomizationGroup.id == group_id)
    )
    if not result.scalars().first():
        raise HTTPException(status_code=404, detail="Group not found")
    
    option = CustomizationOption(
        group_id=group_id,
        name=option_in.name,
        name_ar=option_in.name_ar,
        price_adjustment=option_in.price_adjustment,
        is_default=option_in.is_default,
    )
    db.add(option)
    await db.commit()
    await db.refresh(option)
    
    return {"message": "Option added", "option_id": option.id}


@router.delete("/groups/{group_id}")
async def delete_group(
    group_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Delete customization group (Admin).
    """
    result = await db.execute(
        select(CustomizationGroup).where(CustomizationGroup.id == group_id)
    )
    group = result.scalars().first()
    
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    # Delete options first
    await db.execute(
        CustomizationOption.__table__.delete().where(
            CustomizationOption.group_id == group_id
        )
    )
    
    await db.delete(group)
    await db.commit()
    
    return {"message": "Group deleted"}
