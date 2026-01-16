"""
FAQ & Help Center API
"""
from typing import Any, Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from datetime import datetime

from app.db.session import get_db
from app.models.user import User
from app.api import deps

# Model
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from app.db.base_class import Base


router = APIRouter()


class FAQ(Base):
    __tablename__ = "faqs"
    
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(50), nullable=False)
    question_en = Column(Text, nullable=False)
    question_ar = Column(Text, nullable=True)
    answer_en = Column(Text, nullable=False)
    answer_ar = Column(Text, nullable=True)
    position = Column(Integer, default=0)
    is_published = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# Default FAQs
DEFAULT_FAQS = [
    {
        "category": "ordering",
        "question_en": "How do I place an order?",
        "question_ar": "كيف أطلب؟",
        "answer_en": "Browse restaurants, add items to your cart, and checkout with your delivery address.",
        "answer_ar": "تصفح المطاعم، أضف الأصناف للسلة، وأتمم الطلب مع عنوان التوصيل.",
    },
    {
        "category": "ordering",
        "question_en": "Can I schedule an order for later?",
        "question_ar": "هل يمكنني جدولة طلب لاحقاً؟",
        "answer_en": "Yes! During checkout, select 'Schedule for Later' and choose your preferred time.",
        "answer_ar": "نعم! عند الدفع، اختر 'جدولة لاحقاً' وحدد الوقت المفضل.",
    },
    {
        "category": "payment",
        "question_en": "What payment methods are available?",
        "question_ar": "ما هي طرق الدفع المتاحة؟",
        "answer_en": "Currently, we accept Cash on Delivery (COD).",
        "answer_ar": "حالياً، نقبل الدفع عند الاستلام.",
    },
    {
        "category": "delivery",
        "question_en": "How long does delivery take?",
        "question_ar": "كم يستغرق التوصيل؟",
        "answer_en": "Delivery usually takes 30-45 minutes depending on distance and restaurant preparation time.",
        "answer_ar": "التوصيل عادة يستغرق 30-45 دقيقة حسب المسافة ووقت تحضير المطعم.",
    },
    {
        "category": "delivery",
        "question_en": "Can I track my order?",
        "question_ar": "هل يمكنني تتبع طلبي؟",
        "answer_en": "Yes! Once a driver is assigned, you can track their location in real-time.",
        "answer_ar": "نعم! بمجرد تعيين سائق، يمكنك تتبع موقعه مباشرة.",
    },
    {
        "category": "cancellation",
        "question_en": "How do I cancel an order?",
        "question_ar": "كيف ألغي طلباً؟",
        "answer_en": "You can cancel within 5 minutes of placing the order. After that, please contact support.",
        "answer_ar": "يمكنك الإلغاء خلال 5 دقائق من الطلب. بعدها، تواصل مع الدعم.",
    },
]


class FAQCreate(BaseModel):
    category: str
    question_en: str
    question_ar: Optional[str] = None
    answer_en: str
    answer_ar: Optional[str] = None
    position: int = 0


# ==================== Endpoints ====================

@router.get("")
async def get_faqs(
    category: Optional[str] = None,
    lang: str = "en",
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get FAQs (public).
    """
    query = select(FAQ).where(FAQ.is_published == True).order_by(FAQ.position)
    
    if category:
        query = query.where(FAQ.category == category)
    
    result = await db.execute(query)
    faqs = result.scalars().all()
    
    # If no FAQs in DB, return defaults
    if not faqs:
        items = DEFAULT_FAQS
        if category:
            items = [f for f in items if f["category"] == category]
        
        return [
            {
                "id": i,
                "category": f["category"],
                "question": f[f"question_{lang}"] or f["question_en"],
                "answer": f[f"answer_{lang}"] or f["answer_en"],
            }
            for i, f in enumerate(items, 1)
        ]
    
    return [
        {
            "id": f.id,
            "category": f.category,
            "question": f.question_ar if lang == "ar" and f.question_ar else f.question_en,
            "answer": f.answer_ar if lang == "ar" and f.answer_ar else f.answer_en,
        }
        for f in faqs
    ]


@router.get("/categories")
async def get_faq_categories(
    lang: str = "en",
) -> Any:
    """
    Get FAQ categories.
    """
    categories = {
        "ordering": {"en": "Ordering", "ar": "الطلب"},
        "payment": {"en": "Payment", "ar": "الدفع"},
        "delivery": {"en": "Delivery", "ar": "التوصيل"},
        "cancellation": {"en": "Cancellation", "ar": "الإلغاء"},
        "account": {"en": "Account", "ar": "الحساب"},
    }
    
    return [
        {"key": k, "name": v[lang]} for k, v in categories.items()
    ]


@router.post("")
async def create_faq(
    faq_in: FAQCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Create FAQ (Admin).
    """
    faq = FAQ(**faq_in.model_dump())
    db.add(faq)
    await db.commit()
    await db.refresh(faq)
    
    return {"message": "FAQ created", "faq_id": faq.id}


@router.delete("/{faq_id}")
async def delete_faq(
    faq_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Delete FAQ (Admin).
    """
    result = await db.execute(select(FAQ).where(FAQ.id == faq_id))
    faq = result.scalars().first()
    
    if not faq:
        raise HTTPException(status_code=404, detail="FAQ not found")
    
    await db.delete(faq)
    await db.commit()
    
    return {"message": "FAQ deleted"}
