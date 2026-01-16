"""
Customer Reviews and Ratings System
"""
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from pydantic import BaseModel, Field
from datetime import datetime

from app.db.session import get_db
from app.models.user import User
from app.models.order import Order
from app.api import deps


router = APIRouter()


# ==================== Model (Add to models/ later) ====================

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class Review(Base):
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("order.id"), unique=True)
    restaurant_id = Column(Integer, ForeignKey("restaurant.id"))
    customer_id = Column(Integer, ForeignKey("user.id"))
    rating = Column(Float, nullable=False)  # 1-5
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relations
    order = relationship("Order", backref="review")
    restaurant = relationship("Restaurant", backref="reviews")
    customer = relationship("User", backref="reviews")


# ==================== Schemas ====================

class ReviewCreate(BaseModel):
    order_id: int
    rating: float = Field(..., ge=1, le=5)
    comment: Optional[str] = None


class ReviewResponse(BaseModel):
    id: int
    order_id: int
    restaurant_id: int
    rating: float
    comment: Optional[str]
    customer_name: str
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== Endpoints ====================

@router.post("", status_code=201)
async def create_review(
    review_in: ReviewCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Create a review for a completed order.
    """
    # Check order exists and belongs to user
    result = await db.execute(
        select(Order).where(
            Order.id == review_in.order_id,
            Order.customer_phone == current_user.phone_number
        )
    )
    order = result.scalars().first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.status != "delivered":
        raise HTTPException(status_code=400, detail="Can only review delivered orders")
    
    # Check if already reviewed
    existing = await db.execute(
        select(Review).where(Review.order_id == review_in.order_id)
    )
    if existing.scalars().first():
        raise HTTPException(status_code=400, detail="Order already reviewed")
    
    review = Review(
        order_id=review_in.order_id,
        restaurant_id=order.restaurant_id,
        customer_id=current_user.id,
        rating=review_in.rating,
        comment=review_in.comment,
    )
    
    db.add(review)
    await db.commit()
    await db.refresh(review)
    
    return {"message": "Review submitted", "review_id": review.id}


@router.get("/restaurant/{restaurant_id}")
async def get_restaurant_reviews(
    restaurant_id: int,
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 20,
) -> Any:
    """
    Get reviews for a restaurant.
    Uses eager loading to avoid N+1 queries.
    """
    result = await db.execute(
        select(Review)
        .where(Review.restaurant_id == restaurant_id)
        .options(selectinload(Review.customer))
        .order_by(Review.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    reviews = result.scalars().all()
    
    # Get average rating
    avg_result = await db.execute(
        select(func.avg(Review.rating), func.count(Review.id))
        .where(Review.restaurant_id == restaurant_id)
    )
    avg_rating, total_reviews = avg_result.first()
    
    return {
        "average_rating": round(float(avg_rating or 0), 1),
        "total_reviews": total_reviews or 0,
        "reviews": [
            {
                "id": r.id,
                "rating": r.rating,
                "comment": r.comment,
                "customer_name": r.customer.full_name if r.customer else "Anonymous",
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in reviews
        ]
    }


@router.get("/my-reviews")
async def get_my_reviews(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get current user's reviews.
    Uses eager loading to avoid N+1 queries.
    """
    result = await db.execute(
        select(Review)
        .where(Review.customer_id == current_user.id)
        .options(selectinload(Review.restaurant))
        .order_by(Review.created_at.desc())
    )
    reviews = result.scalars().all()
    
    return [
        {
            "id": r.id,
            "order_id": r.order_id,
            "restaurant_name": r.restaurant.name if r.restaurant else "Unknown",
            "rating": r.rating,
            "comment": r.comment,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in reviews
    ]
