"""
Feature Flags API - Toggle features on/off
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
from app.services.redis_service import redis_service
import json

# Model
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from app.db.base_class import Base


router = APIRouter()


class FeatureFlag(Base):
    __tablename__ = "feature_flags"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    is_enabled = Column(Boolean, default=False)
    rollout_percentage = Column(Integer, default=100)  # 0-100
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Default feature flags
DEFAULT_FLAGS = {
    "scheduled_orders": {"name": "Scheduled Orders", "enabled": True},
    "live_tracking": {"name": "Live Driver Tracking", "enabled": True},
    "referral_program": {"name": "Referral Program", "enabled": True},
    "promo_codes": {"name": "Promo Codes", "enabled": True},
    "reviews": {"name": "Reviews & Ratings", "enabled": True},
    "tips": {"name": "Driver Tips", "enabled": True},
    "dark_mode": {"name": "Dark Mode", "enabled": True},
    "push_notifications": {"name": "Push Notifications", "enabled": True},
    "whatsapp_notifications": {"name": "WhatsApp Notifications", "enabled": True},
    "order_scheduling": {"name": "Order Scheduling", "enabled": True},
    "new_ui": {"name": "New UI Design", "enabled": False},
    "beta_features": {"name": "Beta Features", "enabled": False},
}


class FlagUpdate(BaseModel):
    is_enabled: Optional[bool] = None
    rollout_percentage: Optional[int] = None


# ==================== Endpoints ====================

@router.get("")
async def get_feature_flags(
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get all feature flags (for apps).
    """
    # Try cache first
    cached = await redis_service.get("feature_flags")
    if cached:
        return json.loads(cached)
    
    result = await db.execute(select(FeatureFlag))
    flags = result.scalars().all()
    
    if not flags:
        # Return defaults
        response = {k: v["enabled"] for k, v in DEFAULT_FLAGS.items()}
    else:
        response = {f.key: f.is_enabled for f in flags}
    
    # Cache for 5 minutes
    await redis_service.set("feature_flags", json.dumps(response), ex=300)
    
    return response


@router.get("/admin")
async def get_all_flags_admin(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Get all feature flags with details (Admin).
    """
    result = await db.execute(select(FeatureFlag))
    flags = result.scalars().all()
    
    # Merge with defaults
    all_flags = {}
    for key, default in DEFAULT_FLAGS.items():
        all_flags[key] = {
            "key": key,
            "name": default["name"],
            "is_enabled": default["enabled"],
            "rollout_percentage": 100,
            "in_db": False,
        }
    
    for flag in flags:
        all_flags[flag.key] = {
            "id": flag.id,
            "key": flag.key,
            "name": flag.name,
            "description": flag.description,
            "is_enabled": flag.is_enabled,
            "rollout_percentage": flag.rollout_percentage,
            "in_db": True,
            "updated_at": flag.updated_at.isoformat() if flag.updated_at else None,
        }
    
    return list(all_flags.values())


@router.put("/{flag_key}")
async def update_feature_flag(
    flag_key: str,
    flag_in: FlagUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update a feature flag (Admin).
    """
    result = await db.execute(
        select(FeatureFlag).where(FeatureFlag.key == flag_key)
    )
    flag = result.scalars().first()
    
    if not flag:
        # Create new flag
        if flag_key not in DEFAULT_FLAGS:
            raise HTTPException(status_code=404, detail="Unknown feature flag")
        
        default = DEFAULT_FLAGS[flag_key]
        flag = FeatureFlag(
            key=flag_key,
            name=default["name"],
            is_enabled=default["enabled"],
        )
        db.add(flag)
    
    if flag_in.is_enabled is not None:
        flag.is_enabled = flag_in.is_enabled
    
    if flag_in.rollout_percentage is not None:
        flag.rollout_percentage = max(0, min(100, flag_in.rollout_percentage))
    
    db.add(flag)
    await db.commit()
    
    # Clear cache
    await redis_service.delete("feature_flags")
    
    return {"message": f"Feature '{flag_key}' updated"}


@router.post("/{flag_key}/toggle")
async def toggle_feature_flag(
    flag_key: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Toggle a feature flag on/off (Admin).
    """
    result = await db.execute(
        select(FeatureFlag).where(FeatureFlag.key == flag_key)
    )
    flag = result.scalars().first()
    
    if not flag:
        if flag_key not in DEFAULT_FLAGS:
            raise HTTPException(status_code=404, detail="Unknown feature flag")
        
        default = DEFAULT_FLAGS[flag_key]
        flag = FeatureFlag(
            key=flag_key,
            name=default["name"],
            is_enabled=not default["enabled"],
        )
    else:
        flag.is_enabled = not flag.is_enabled
    
    db.add(flag)
    await db.commit()
    
    # Clear cache
    await redis_service.delete("feature_flags")
    
    return {
        "message": f"Feature '{flag_key}' is now {'enabled' if flag.is_enabled else 'disabled'}",
        "is_enabled": flag.is_enabled,
    }


async def is_feature_enabled(flag_key: str, user_id: int = None) -> bool:
    """
    Check if a feature is enabled (helper function).
    """
    # Get flags from cache
    cached = await redis_service.get("feature_flags")
    if cached:
        flags = json.loads(cached)
        return flags.get(flag_key, DEFAULT_FLAGS.get(flag_key, {}).get("enabled", False))
    
    return DEFAULT_FLAGS.get(flag_key, {}).get("enabled", False)
