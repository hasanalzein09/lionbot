"""
Promotional Banners API - Home screen banners and promotions
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

# Model
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from app.db.base_class import Base


router = APIRouter()


class Banner(Base):
    __tablename__ = "banners"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    title_ar = Column(String(100), nullable=True)  # Arabic
    subtitle = Column(String(200), nullable=True)
    subtitle_ar = Column(String(200), nullable=True)
    image_url = Column(Text, nullable=True)
    action_type = Column(String(50), default="none")  # none, restaurant, category, url
    action_value = Column(String(200), nullable=True)  # restaurant_id, category_name, or URL
    background_color = Column(String(20), default="#FF6B00")
    text_color = Column(String(20), default="#FFFFFF")
    position = Column(Integer, default=0)  # Display order
    is_active = Column(Boolean, default=True)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class BannerCreate(BaseModel):
    title: str
    title_ar: Optional[str] = None
    subtitle: Optional[str] = None
    subtitle_ar: Optional[str] = None
    image_url: Optional[str] = None
    action_type: str = "none"
    action_value: Optional[str] = None
    background_color: str = "#FF6B00"
    text_color: str = "#FFFFFF"
    position: int = 0
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


# ==================== Endpoints ====================

@router.get("")
async def get_active_banners(
    db: AsyncSession = Depends(get_db),
    lang: str = "en",
) -> Any:
    """
    Get active promotional banners for home screen.
    """
    now = datetime.utcnow()
    
    result = await db.execute(
        select(Banner)
        .where(
            Banner.is_active == True,
        )
        .order_by(Banner.position)
    )
    banners = result.scalars().all()
    
    # Filter by date
    active_banners = []
    for b in banners:
        if b.start_date and now < b.start_date:
            continue
        if b.end_date and now > b.end_date:
            continue
        
        active_banners.append({
            "id": b.id,
            "title": b.title_ar if lang == "ar" and b.title_ar else b.title,
            "subtitle": b.subtitle_ar if lang == "ar" and b.subtitle_ar else b.subtitle,
            "image_url": b.image_url,
            "action_type": b.action_type,
            "action_value": b.action_value,
            "background_color": b.background_color,
            "text_color": b.text_color,
        })
    
    return active_banners


# Admin endpoints
@router.post("")
async def create_banner(
    banner_in: BannerCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Create a new banner (Admin).
    """
    banner = Banner(**banner_in.model_dump())
    db.add(banner)
    await db.commit()
    await db.refresh(banner)
    
    return {"message": "Banner created", "banner_id": banner.id}


@router.get("/admin/all")
async def get_all_banners(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Get all banners including inactive (Admin).
    """
    result = await db.execute(
        select(Banner).order_by(Banner.position)
    )
    banners = result.scalars().all()
    
    return [
        {
            "id": b.id,
            "title": b.title,
            "subtitle": b.subtitle,
            "action_type": b.action_type,
            "is_active": b.is_active,
            "position": b.position,
        }
        for b in banners
    ]


@router.patch("/{banner_id}/toggle")
async def toggle_banner(
    banner_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Toggle banner active status (Admin).
    """
    result = await db.execute(select(Banner).where(Banner.id == banner_id))
    banner = result.scalars().first()
    
    if not banner:
        raise HTTPException(status_code=404, detail="Banner not found")
    
    banner.is_active = not banner.is_active
    db.add(banner)
    await db.commit()
    
    return {"message": f"Banner {'activated' if banner.is_active else 'deactivated'}"}


@router.delete("/{banner_id}")
async def delete_banner(
    banner_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Delete a banner (Admin).
    """
    result = await db.execute(select(Banner).where(Banner.id == banner_id))
    banner = result.scalars().first()
    
    if not banner:
        raise HTTPException(status_code=404, detail="Banner not found")
    
    await db.delete(banner)
    await db.commit()
    
    return {"message": "Banner deleted"}
