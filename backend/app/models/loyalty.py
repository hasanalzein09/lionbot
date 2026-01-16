from sqlalchemy import Column, Integer, Float, String, Boolean, ForeignKey, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.db.base_class import Base


class LoyaltyTier(str, enum.Enum):
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"


class PointTransactionType(str, enum.Enum):
    EARNED = "earned"
    REDEEMED = "redeemed"
    EXPIRED = "expired"
    BONUS = "bonus"
    REFERRAL = "referral"


class CustomerLoyalty(Base):
    """Customer loyalty program membership."""
    __tablename__ = "customer_loyalty"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), unique=True, index=True)
    
    # Points
    total_points = Column(Integer, default=0)
    available_points = Column(Integer, default=0)
    lifetime_points = Column(Integer, default=0)
    
    # Tier
    tier = Column(SQLEnum(LoyaltyTier), default=LoyaltyTier.BRONZE)
    tier_progress = Column(Float, default=0.0)  # Progress to next tier (0-100)
    
    # Stats
    total_orders = Column(Integer, default=0)
    total_spent = Column(Float, default=0.0)
    
    # Referral
    referral_code = Column(String, unique=True, index=True)
    referred_by_id = Column(Integer, ForeignKey("user.id"), nullable=True)
    referral_count = Column(Integer, default=0)
    
    # Timestamps
    joined_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], backref="loyalty")
    transactions = relationship("PointTransaction", back_populates="loyalty")


class PointTransaction(Base):
    """Individual point transaction record."""
    __tablename__ = "point_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    loyalty_id = Column(Integer, ForeignKey("customer_loyalty.id"), index=True)
    
    type = Column(SQLEnum(PointTransactionType))
    points = Column(Integer)  # Positive for earned, negative for redeemed
    balance_after = Column(Integer)
    
    # Reference
    order_id = Column(Integer, ForeignKey("order.id"), nullable=True)
    description = Column(String)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)  # For earned points
    
    # Relationships
    loyalty = relationship("CustomerLoyalty", back_populates="transactions")


class LoyaltyReward(Base):
    """Available rewards that can be redeemed."""
    __tablename__ = "loyalty_rewards"
    
    id = Column(Integer, primary_key=True, index=True)
    
    name = Column(String, nullable=False)
    name_ar = Column(String, nullable=False)
    description = Column(String)
    description_ar = Column(String)
    
    # Cost
    points_required = Column(Integer, nullable=False)
    
    # Type
    reward_type = Column(String)  # "discount_percent", "discount_amount", "free_delivery", "free_item"
    reward_value = Column(Float)  # 10 for 10%, 5 for $5, etc.
    
    # Restrictions
    min_order_amount = Column(Float, default=0.0)
    min_tier = Column(SQLEnum(LoyaltyTier), default=LoyaltyTier.BRONZE)
    
    # Availability
    is_active = Column(Boolean, default=True)
    stock = Column(Integer, nullable=True)  # None = unlimited
    
    # Validity
    valid_from = Column(DateTime, nullable=True)
    valid_until = Column(DateTime, nullable=True)


class RedeemedReward(Base):
    """Rewards redeemed by customers."""
    __tablename__ = "redeemed_rewards"
    
    id = Column(Integer, primary_key=True, index=True)
    loyalty_id = Column(Integer, ForeignKey("customer_loyalty.id"), index=True)
    reward_id = Column(Integer, ForeignKey("loyalty_rewards.id"))
    
    # Redemption code
    code = Column(String, unique=True, index=True)
    
    # Status
    is_used = Column(Boolean, default=False)
    used_on_order_id = Column(Integer, ForeignKey("order.id"), nullable=True)
    
    # Timestamps
    redeemed_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    used_at = Column(DateTime, nullable=True)
