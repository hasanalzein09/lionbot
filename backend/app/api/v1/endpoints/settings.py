from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api import deps
from app.db.session import get_db
from app.models.settings import SystemSettings
from app.schemas.settings import SystemSettings as SystemSettingsSchema, SystemSettingsUpdate

router = APIRouter()

@router.get("/", response_model=SystemSettingsSchema)
async def get_settings(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Get system settings.
    """
    result = await db.execute(select(SystemSettings).where(SystemSettings.id == 1))
    settings = result.scalars().first()
    
    if not settings:
        # Initialize with default settings if not exists
        settings = SystemSettings(id=1)
        db.add(settings)
        await db.commit()
        await db.refresh(settings)
        
    return settings

@router.put("/", response_model=SystemSettingsSchema)
async def update_settings(
    *,
    db: AsyncSession = Depends(get_db),
    settings_in: SystemSettingsUpdate,
    current_user = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update system settings.
    """
    result = await db.execute(select(SystemSettings).where(SystemSettings.id == 1))
    settings = result.scalars().first()
    
    if not settings:
        settings = SystemSettings(id=1)
        db.add(settings)

    # Update fields
    for field, value in settings_in.model_dump(exclude_unset=True).items():
        setattr(settings, field, value)
        
    db.add(settings)
    await db.commit()
    await db.refresh(settings)
    
    return settings
