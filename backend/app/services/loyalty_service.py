from typing import Optional, List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
import secrets
import string

from app.models.loyalty import (
    CustomerLoyalty, PointTransaction, LoyaltyReward, 
    RedeemedReward, LoyaltyTier, PointTransactionType
)
from app.models.order import Order


class LoyaltyService:
    """Service for managing customer loyalty program."""
    
    # Points configuration
    POINTS_PER_DOLLAR = 10  # 10 points per $1 spent
    POINTS_EXPIRY_DAYS = 365
    
    # Tier thresholds (lifetime points)
    TIER_THRESHOLDS = {
        LoyaltyTier.BRONZE: 0,
        LoyaltyTier.SILVER: 1000,
        LoyaltyTier.GOLD: 5000,
        LoyaltyTier.PLATINUM: 15000,
    }
    
    # Tier benefits (bonus multiplier)
    TIER_MULTIPLIERS = {
        LoyaltyTier.BRONZE: 1.0,
        LoyaltyTier.SILVER: 1.25,
        LoyaltyTier.GOLD: 1.5,
        LoyaltyTier.PLATINUM: 2.0,
    }
    
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_or_create_loyalty(self, user_id: int) -> CustomerLoyalty:
        """Get or create loyalty record for a user."""
        result = await self.db.execute(
            select(CustomerLoyalty).where(CustomerLoyalty.user_id == user_id)
        )
        loyalty = result.scalars().first()
        
        if not loyalty:
            loyalty = CustomerLoyalty(
                user_id=user_id,
                referral_code=self._generate_referral_code()
            )
            self.db.add(loyalty)
            await self.db.commit()
            await self.db.refresh(loyalty)
        
        return loyalty

    async def earn_points_from_order(self, user_id: int, order: Order) -> int:
        """Award points for a completed order."""
        loyalty = await self.get_or_create_loyalty(user_id)
        
        # Calculate base points
        base_points = int(float(order.total_amount) * self.POINTS_PER_DOLLAR)
        
        # Apply tier multiplier
        multiplier = self.TIER_MULTIPLIERS.get(loyalty.tier, 1.0)
        final_points = int(base_points * multiplier)
        
        # Create transaction
        transaction = PointTransaction(
            loyalty_id=loyalty.id,
            type=PointTransactionType.EARNED,
            points=final_points,
            balance_after=loyalty.available_points + final_points,
            order_id=order.id,
            description=f"Earned from order #{order.id}",
            expires_at=datetime.utcnow() + timedelta(days=self.POINTS_EXPIRY_DAYS)
        )
        self.db.add(transaction)
        
        # Update loyalty
        loyalty.available_points += final_points
        loyalty.total_points += final_points
        loyalty.lifetime_points += final_points
        loyalty.total_orders += 1
        loyalty.total_spent += float(order.total_amount)
        
        # Check for tier upgrade
        await self._update_tier(loyalty)
        
        await self.db.commit()
        return final_points

    async def redeem_reward(
        self, 
        user_id: int, 
        reward_id: int
    ) -> Optional[RedeemedReward]:
        """Redeem a reward for points."""
        loyalty = await self.get_or_create_loyalty(user_id)
        
        # Get reward
        result = await self.db.execute(
            select(LoyaltyReward).where(LoyaltyReward.id == reward_id)
        )
        reward = result.scalars().first()
        
        if not reward or not reward.is_active:
            return None
        
        # Check tier requirement
        tier_order = list(LoyaltyTier)
        if tier_order.index(loyalty.tier) < tier_order.index(reward.min_tier):
            return None
        
        # Check points
        if loyalty.available_points < reward.points_required:
            return None
        
        # Check stock
        if reward.stock is not None and reward.stock <= 0:
            return None
        
        # Create redemption
        redeemed = RedeemedReward(
            loyalty_id=loyalty.id,
            reward_id=reward.id,
            code=self._generate_redemption_code(),
            expires_at=datetime.utcnow() + timedelta(days=30)
        )
        self.db.add(redeemed)
        
        # Deduct points
        transaction = PointTransaction(
            loyalty_id=loyalty.id,
            type=PointTransactionType.REDEEMED,
            points=-reward.points_required,
            balance_after=loyalty.available_points - reward.points_required,
            description=f"Redeemed: {reward.name}"
        )
        self.db.add(transaction)
        
        loyalty.available_points -= reward.points_required
        
        # Update stock
        if reward.stock is not None:
            reward.stock -= 1
        
        await self.db.commit()
        await self.db.refresh(redeemed)
        
        return redeemed

    async def apply_referral(self, user_id: int, referral_code: str) -> bool:
        """Apply a referral code for bonus points."""
        # Find referrer
        result = await self.db.execute(
            select(CustomerLoyalty).where(CustomerLoyalty.referral_code == referral_code)
        )
        referrer_loyalty = result.scalars().first()
        
        if not referrer_loyalty or referrer_loyalty.user_id == user_id:
            return False
        
        # Get or create loyalty for new user
        loyalty = await self.get_or_create_loyalty(user_id)
        
        if loyalty.referred_by_id:
            return False  # Already referred
        
        # Set referral
        loyalty.referred_by_id = referrer_loyalty.user_id
        
        # Award bonus points to both
        REFERRAL_BONUS = 500
        
        for target_loyalty, desc in [
            (loyalty, "Referral signup bonus"),
            (referrer_loyalty, "Referral reward")
        ]:
            transaction = PointTransaction(
                loyalty_id=target_loyalty.id,
                type=PointTransactionType.REFERRAL,
                points=REFERRAL_BONUS,
                balance_after=target_loyalty.available_points + REFERRAL_BONUS,
                description=desc
            )
            self.db.add(transaction)
            target_loyalty.available_points += REFERRAL_BONUS
            target_loyalty.total_points += REFERRAL_BONUS
            target_loyalty.lifetime_points += REFERRAL_BONUS
        
        referrer_loyalty.referral_count += 1
        
        await self.db.commit()
        return True

    async def get_available_rewards(self, user_id: int) -> List[LoyaltyReward]:
        """Get rewards available for a user based on their tier."""
        loyalty = await self.get_or_create_loyalty(user_id)
        
        tier_order = list(LoyaltyTier)
        user_tier_index = tier_order.index(loyalty.tier)
        
        result = await self.db.execute(
            select(LoyaltyReward)
            .where(LoyaltyReward.is_active == True)
            .where(LoyaltyReward.points_required <= loyalty.available_points)
        )
        rewards = result.scalars().all()
        
        # Filter by tier
        available = []
        for reward in rewards:
            reward_tier_index = tier_order.index(reward.min_tier)
            if user_tier_index >= reward_tier_index:
                available.append(reward)
        
        return available

    async def _update_tier(self, loyalty: CustomerLoyalty):
        """Update customer tier based on lifetime points."""
        new_tier = LoyaltyTier.BRONZE
        
        for tier, threshold in sorted(
            self.TIER_THRESHOLDS.items(), 
            key=lambda x: x[1], 
            reverse=True
        ):
            if loyalty.lifetime_points >= threshold:
                new_tier = tier
                break
        
        if new_tier != loyalty.tier:
            loyalty.tier = new_tier
        
        # Calculate progress to next tier
        tier_list = list(self.TIER_THRESHOLDS.keys())
        current_index = tier_list.index(loyalty.tier)
        
        if current_index < len(tier_list) - 1:
            next_tier = tier_list[current_index + 1]
            current_threshold = self.TIER_THRESHOLDS[loyalty.tier]
            next_threshold = self.TIER_THRESHOLDS[next_tier]
            
            progress = (loyalty.lifetime_points - current_threshold) / (next_threshold - current_threshold) * 100
            loyalty.tier_progress = min(100, max(0, progress))
        else:
            loyalty.tier_progress = 100

    @staticmethod
    def _generate_referral_code() -> str:
        """Generate unique referral code."""
        chars = string.ascii_uppercase + string.digits
        return 'LION' + ''.join(secrets.choice(chars) for _ in range(6))

    @staticmethod
    def _generate_redemption_code() -> str:
        """Generate unique redemption code."""
        chars = string.ascii_uppercase + string.digits
        return 'RWD' + ''.join(secrets.choice(chars) for _ in range(8))
