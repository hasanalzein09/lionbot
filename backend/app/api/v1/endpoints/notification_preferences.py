"""
Notification Preferences API - Control what notifications to receive
"""
from typing import Any
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from datetime import datetime

from app.db.session import get_db
from app.models.user import User
from app.api import deps

# Model
from sqlalchemy import Column, Integer, Boolean, DateTime, ForeignKey
from app.db.base_class import Base


router = APIRouter()


class NotificationPreference(Base):
    __tablename__ = "notification_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), unique=True, nullable=False)
    
    # Order notifications
    order_updates = Column(Boolean, default=True)
    order_delivered = Column(Boolean, default=True)
    
    # Marketing
    promotions = Column(Boolean, default=True)
    new_restaurants = Column(Boolean, default=True)
    weekly_deals = Column(Boolean, default=True)
    
    # Account
    account_alerts = Column(Boolean, default=True)
    loyalty_updates = Column(Boolean, default=True)
    
    # Channels
    push_enabled = Column(Boolean, default=True)
    sms_enabled = Column(Boolean, default=False)
    whatsapp_enabled = Column(Boolean, default=True)
    
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PreferencesUpdate(BaseModel):
    order_updates: bool = None
    order_delivered: bool = None
    promotions: bool = None
    new_restaurants: bool = None
    weekly_deals: bool = None
    account_alerts: bool = None
    loyalty_updates: bool = None
    push_enabled: bool = None
    sms_enabled: bool = None
    whatsapp_enabled: bool = None


# ==================== Endpoints ====================

@router.get("")
async def get_preferences(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get user's notification preferences.
    """
    result = await db.execute(
        select(NotificationPreference).where(
            NotificationPreference.user_id == current_user.id
        )
    )
    prefs = result.scalars().first()
    
    if not prefs:
        # Create default preferences
        prefs = NotificationPreference(user_id=current_user.id)
        db.add(prefs)
        await db.commit()
        await db.refresh(prefs)
    
    return {
        "order_notifications": {
            "order_updates": prefs.order_updates,
            "order_delivered": prefs.order_delivered,
        },
        "marketing": {
            "promotions": prefs.promotions,
            "new_restaurants": prefs.new_restaurants,
            "weekly_deals": prefs.weekly_deals,
        },
        "account": {
            "account_alerts": prefs.account_alerts,
            "loyalty_updates": prefs.loyalty_updates,
        },
        "channels": {
            "push_enabled": prefs.push_enabled,
            "sms_enabled": prefs.sms_enabled,
            "whatsapp_enabled": prefs.whatsapp_enabled,
        },
    }


@router.put("")
async def update_preferences(
    prefs_in: PreferencesUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Update notification preferences.
    """
    result = await db.execute(
        select(NotificationPreference).where(
            NotificationPreference.user_id == current_user.id
        )
    )
    prefs = result.scalars().first()
    
    if not prefs:
        prefs = NotificationPreference(user_id=current_user.id)
        db.add(prefs)
    
    update_data = prefs_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            setattr(prefs, field, value)
    
    db.add(prefs)
    await db.commit()
    
    return {"message": "Preferences updated"}


@router.post("/mute-all")
async def mute_all_notifications(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Mute all marketing notifications.
    """
    result = await db.execute(
        select(NotificationPreference).where(
            NotificationPreference.user_id == current_user.id
        )
    )
    prefs = result.scalars().first()
    
    if not prefs:
        prefs = NotificationPreference(user_id=current_user.id)
    
    prefs.promotions = False
    prefs.new_restaurants = False
    prefs.weekly_deals = False
    
    db.add(prefs)
    await db.commit()
    
    return {"message": "Marketing notifications muted"}


@router.post("/unmute-all")
async def unmute_all_notifications(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Unmute all notifications.
    """
    result = await db.execute(
        select(NotificationPreference).where(
            NotificationPreference.user_id == current_user.id
        )
    )
    prefs = result.scalars().first()
    
    if not prefs:
        prefs = NotificationPreference(user_id=current_user.id)
    
    prefs.promotions = True
    prefs.new_restaurants = True
    prefs.weekly_deals = True
    prefs.push_enabled = True
    prefs.whatsapp_enabled = True
    
    db.add(prefs)
    await db.commit()
    
    return {"message": "All notifications enabled"}
