from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import List, Optional

from app.db.session import get_db
from app.api import deps
from app.models.user import User
from app.models.loyalty import LoyaltyTier
from app.services.loyalty_service import LoyaltyService

router = APIRouter()


# ============= Schemas =============

class LoyaltyStatusResponse(BaseModel):
    tier: str
    available_points: int
    lifetime_points: int
    tier_progress: float
    total_orders: int
    total_spent: float
    referral_code: str
    
    class Config:
        from_attributes = True


class RewardResponse(BaseModel):
    id: int
    name: str
    name_ar: str
    description: Optional[str]
    points_required: int
    reward_type: str
    reward_value: float
    min_tier: str
    
    class Config:
        from_attributes = True


class RedeemRequest(BaseModel):
    reward_id: int


class RedeemResponse(BaseModel):
    success: bool
    code: Optional[str]
    expires_at: Optional[str]
    message: str


class ReferralRequest(BaseModel):
    referral_code: str


class PointsHistoryResponse(BaseModel):
    type: str
    points: int
    balance_after: int
    description: str
    created_at: str
    
    class Config:
        from_attributes = True


# ============= Endpoints =============

@router.get("/status", response_model=LoyaltyStatusResponse)
async def get_loyalty_status(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get current user's loyalty program status."""
    service = LoyaltyService(db)
    loyalty = await service.get_or_create_loyalty(current_user.id)
    
    return LoyaltyStatusResponse(
        tier=loyalty.tier.value,
        available_points=loyalty.available_points,
        lifetime_points=loyalty.lifetime_points,
        tier_progress=loyalty.tier_progress,
        total_orders=loyalty.total_orders,
        total_spent=loyalty.total_spent,
        referral_code=loyalty.referral_code,
    )


@router.get("/rewards", response_model=List[RewardResponse])
async def get_available_rewards(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get rewards available for the current user."""
    service = LoyaltyService(db)
    rewards = await service.get_available_rewards(current_user.id)
    
    return [
        RewardResponse(
            id=r.id,
            name=r.name,
            name_ar=r.name_ar,
            description=r.description,
            points_required=r.points_required,
            reward_type=r.reward_type,
            reward_value=r.reward_value,
            min_tier=r.min_tier.value,
        )
        for r in rewards
    ]


@router.post("/redeem", response_model=RedeemResponse)
async def redeem_reward(
    request: RedeemRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Redeem a reward using points."""
    service = LoyaltyService(db)
    redeemed = await service.redeem_reward(current_user.id, request.reward_id)
    
    if not redeemed:
        raise HTTPException(
            status_code=400,
            detail="Unable to redeem reward. Check points balance and tier requirements."
        )
    
    return RedeemResponse(
        success=True,
        code=redeemed.code,
        expires_at=redeemed.expires_at.isoformat(),
        message="Reward redeemed successfully!"
    )


@router.post("/referral")
async def apply_referral_code(
    request: ReferralRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Apply a referral code to earn bonus points."""
    service = LoyaltyService(db)
    success = await service.apply_referral(current_user.id, request.referral_code)
    
    if not success:
        raise HTTPException(
            status_code=400,
            detail="Invalid referral code or you have already been referred."
        )
    
    return {"success": True, "message": "Referral applied! You earned 500 bonus points."}


@router.get("/history", response_model=List[PointsHistoryResponse])
async def get_points_history(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Get points transaction history."""
    from sqlalchemy import select
    from app.models.loyalty import PointTransaction, CustomerLoyalty
    
    # Get loyalty
    result = await db.execute(
        select(CustomerLoyalty).where(CustomerLoyalty.user_id == current_user.id)
    )
    loyalty = result.scalars().first()
    
    if not loyalty:
        return []
    
    # Get transactions
    result = await db.execute(
        select(PointTransaction)
        .where(PointTransaction.loyalty_id == loyalty.id)
        .order_by(PointTransaction.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    transactions = result.scalars().all()
    
    return [
        PointsHistoryResponse(
            type=t.type.value,
            points=t.points,
            balance_after=t.balance_after,
            description=t.description,
            created_at=t.created_at.isoformat(),
        )
        for t in transactions
    ]


@router.get("/tiers")
async def get_tier_info():
    """Get information about loyalty tiers."""
    return {
        "tiers": [
            {
                "name": "bronze",
                "name_ar": "برونزي",
                "points_required": 0,
                "multiplier": 1.0,
                "benefits": ["10 points per $1"]
            },
            {
                "name": "silver", 
                "name_ar": "فضي",
                "points_required": 1000,
                "multiplier": 1.25,
                "benefits": ["12.5 points per $1", "Free delivery on orders over $30"]
            },
            {
                "name": "gold",
                "name_ar": "ذهبي", 
                "points_required": 5000,
                "multiplier": 1.5,
                "benefits": ["15 points per $1", "Free delivery on all orders", "Priority support"]
            },
            {
                "name": "platinum",
                "name_ar": "بلاتيني",
                "points_required": 15000,
                "multiplier": 2.0,
                "benefits": ["20 points per $1", "Free delivery", "Priority support", "Exclusive offers"]
            }
        ]
    }
