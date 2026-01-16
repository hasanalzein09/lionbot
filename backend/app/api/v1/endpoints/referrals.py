"""
Referral System - Invite friends and earn rewards
"""
from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel
from datetime import datetime
import secrets
import string

from app.db.session import get_db
from app.models.user import User
from app.api import deps

# Model
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from app.db.base_class import Base


router = APIRouter()


class Referral(Base):
    __tablename__ = "referrals"
    
    id = Column(Integer, primary_key=True, index=True)
    referrer_id = Column(Integer, ForeignKey("user.id"), nullable=False)  # Who invited
    referred_id = Column(Integer, ForeignKey("user.id"), nullable=True)   # Who joined
    referral_code = Column(String(20), unique=True, nullable=False, index=True)
    reward_claimed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    claimed_at = Column(DateTime, nullable=True)


# Settings
REFERRAL_BONUS_POINTS = 500  # Points for referrer
NEW_USER_BONUS_POINTS = 200  # Points for new user


def generate_referral_code(length: int = 8) -> str:
    """Generate unique referral code."""
    chars = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))


# ==================== Endpoints ====================

@router.get("/my-code")
async def get_my_referral_code(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get or generate user's referral code.
    """
    # Check if user already has a code
    result = await db.execute(
        select(Referral).where(
            Referral.referrer_id == current_user.id,
            Referral.referred_id == None  # Unused code
        )
    )
    existing = result.scalars().first()
    
    if existing:
        code = existing.referral_code
    else:
        # Generate new code
        code = generate_referral_code()
        referral = Referral(
            referrer_id=current_user.id,
            referral_code=code,
        )
        db.add(referral)
        await db.commit()
    
    return {
        "code": code,
        "share_text": f"🦁 Use my code {code} to get {NEW_USER_BONUS_POINTS} bonus points on Lion Delivery!",
        "share_link": f"https://liondelivery.app/invite/{code}",
        "bonus_points": REFERRAL_BONUS_POINTS,
    }


@router.post("/apply")
async def apply_referral_code(
    code: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Apply a referral code (for new users).
    """
    # Check if user already used a referral
    existing_use = await db.execute(
        select(Referral).where(Referral.referred_id == current_user.id)
    )
    if existing_use.scalars().first():
        raise HTTPException(status_code=400, detail="You have already used a referral code")
    
    # Find the referral code
    result = await db.execute(
        select(Referral).where(
            Referral.referral_code == code.upper(),
            Referral.referred_id == None  # Unused
        )
    )
    referral = result.scalars().first()
    
    if not referral:
        raise HTTPException(status_code=404, detail="Invalid or already used referral code")
    
    if referral.referrer_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot use your own referral code")
    
    # Apply referral
    referral.referred_id = current_user.id
    referral.reward_claimed = True
    referral.claimed_at = datetime.utcnow()
    
    db.add(referral)
    
    # Add points to both users (would update loyalty_points column)
    # TODO: Integrate with actual loyalty system
    
    await db.commit()
    
    return {
        "message": f"Referral applied! You earned {NEW_USER_BONUS_POINTS} points!",
        "points_earned": NEW_USER_BONUS_POINTS,
    }


@router.get("/my-referrals")
async def get_my_referrals(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get list of users I referred.
    """
    result = await db.execute(
        select(Referral).where(
            Referral.referrer_id == current_user.id,
            Referral.referred_id != None
        ).order_by(Referral.claimed_at.desc())
    )
    referrals = result.scalars().all()
    
    # Get count
    count_result = await db.execute(
        select(func.count(Referral.id)).where(
            Referral.referrer_id == current_user.id,
            Referral.referred_id != None
        )
    )
    total_referrals = count_result.scalar()
    
    return {
        "total_referrals": total_referrals,
        "total_points_earned": total_referrals * REFERRAL_BONUS_POINTS,
        "referrals": [
            {
                "id": r.id,
                "claimed_at": r.claimed_at.isoformat() if r.claimed_at else None,
                "points_earned": REFERRAL_BONUS_POINTS,
            }
            for r in referrals
        ],
    }
