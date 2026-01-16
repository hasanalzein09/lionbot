"""
Restaurant Working Hours API
"""
from typing import Any, Optional, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from datetime import datetime, time

from app.db.session import get_db
from app.models.user import User
from app.models.restaurant import Restaurant
from app.api import deps

# Model
from sqlalchemy import Column, Integer, String, Time, Boolean, ForeignKey
from app.db.base_class import Base


router = APIRouter()


class WorkingHours(Base):
    __tablename__ = "working_hours"
    
    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurant.id"), nullable=False)
    day_of_week = Column(Integer, nullable=False)  # 0=Monday, 6=Sunday
    open_time = Column(Time, nullable=True)
    close_time = Column(Time, nullable=True)
    is_closed = Column(Boolean, default=False)


DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
DAY_NAMES_AR = ["الاثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت", "الأحد"]


class HoursUpdate(BaseModel):
    day_of_week: int
    open_time: Optional[str] = None  # "09:00"
    close_time: Optional[str] = None  # "22:00"
    is_closed: bool = False


# ==================== Endpoints ====================

@router.get("/{restaurant_id}")
async def get_working_hours(
    restaurant_id: int,
    db: AsyncSession = Depends(get_db),
    lang: str = "en",
) -> Any:
    """
    Get restaurant working hours.
    """
    result = await db.execute(
        select(WorkingHours)
        .where(WorkingHours.restaurant_id == restaurant_id)
        .order_by(WorkingHours.day_of_week)
    )
    hours = result.scalars().all()
    
    # If no hours set, return default (all days open 9am-10pm)
    if not hours:
        return {
            "restaurant_id": restaurant_id,
            "hours": [
                {
                    "day": i,
                    "day_name": DAY_NAMES_AR[i] if lang == "ar" else DAY_NAMES[i],
                    "open_time": "09:00",
                    "close_time": "22:00",
                    "is_closed": False,
                }
                for i in range(7)
            ],
            "is_open_now": is_restaurant_open_now(None),
        }
    
    return {
        "restaurant_id": restaurant_id,
        "hours": [
            {
                "day": h.day_of_week,
                "day_name": DAY_NAMES_AR[h.day_of_week] if lang == "ar" else DAY_NAMES[h.day_of_week],
                "open_time": h.open_time.strftime("%H:%M") if h.open_time else None,
                "close_time": h.close_time.strftime("%H:%M") if h.close_time else None,
                "is_closed": h.is_closed,
            }
            for h in hours
        ],
        "is_open_now": is_restaurant_open_now(hours),
    }


@router.put("/{restaurant_id}")
async def update_working_hours(
    restaurant_id: int,
    hours: List[HoursUpdate],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update restaurant working hours (Admin).
    """
    # Delete existing hours
    await db.execute(
        WorkingHours.__table__.delete().where(
            WorkingHours.restaurant_id == restaurant_id
        )
    )
    
    # Insert new hours
    for h in hours:
        open_time = None
        close_time = None
        
        if h.open_time:
            parts = h.open_time.split(":")
            open_time = time(int(parts[0]), int(parts[1]))
        
        if h.close_time:
            parts = h.close_time.split(":")
            close_time = time(int(parts[0]), int(parts[1]))
        
        db_hours = WorkingHours(
            restaurant_id=restaurant_id,
            day_of_week=h.day_of_week,
            open_time=open_time,
            close_time=close_time,
            is_closed=h.is_closed,
        )
        db.add(db_hours)
    
    await db.commit()
    
    return {"message": "Working hours updated"}


@router.get("/{restaurant_id}/is-open")
async def check_if_open(
    restaurant_id: int,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Check if restaurant is currently open.
    """
    result = await db.execute(
        select(WorkingHours)
        .where(WorkingHours.restaurant_id == restaurant_id)
    )
    hours = result.scalars().all()
    
    return {
        "restaurant_id": restaurant_id,
        "is_open": is_restaurant_open_now(hours),
        "current_time": datetime.now().strftime("%H:%M"),
        "current_day": DAY_NAMES[datetime.now().weekday()],
    }


def is_restaurant_open_now(hours: List[WorkingHours] = None) -> bool:
    """Check if restaurant is open right now."""
    now = datetime.now()
    current_day = now.weekday()
    current_time = now.time()
    
    if not hours:
        # Default hours: 9am-10pm
        return time(9, 0) <= current_time <= time(22, 0)
    
    for h in hours:
        if h.day_of_week == current_day:
            if h.is_closed:
                return False
            if h.open_time and h.close_time:
                return h.open_time <= current_time <= h.close_time
            return True
    
    return True  # Default open
