"""
Notification Templates - Customizable notification messages
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
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from app.db.base_class import Base


router = APIRouter()


class NotificationTemplate(Base):
    __tablename__ = "notification_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(50), unique=True, nullable=False)  # order_confirmed, etc.
    title_en = Column(String(200), nullable=False)
    title_ar = Column(String(200), nullable=True)
    body_en = Column(Text, nullable=False)
    body_ar = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Default templates
DEFAULT_TEMPLATES = {
    "order_confirmed": {
        "title_en": "Order Confirmed! 🎉",
        "title_ar": "تم تأكيد الطلب! 🎉",
        "body_en": "Your order #{order_id} has been confirmed. Preparing now!",
        "body_ar": "تم تأكيد طلبك #{order_id}. جاري التحضير!",
    },
    "order_preparing": {
        "title_en": "Preparing Your Order 👨‍🍳",
        "title_ar": "جاري تحضير طلبك 👨‍🍳",
        "body_en": "The restaurant is preparing your delicious food!",
        "body_ar": "المطعم يحضر طعامك اللذيذ!",
    },
    "order_ready": {
        "title_en": "Order Ready! 📦",
        "title_ar": "الطلب جاهز! 📦",
        "body_en": "Your order is ready and waiting for the driver.",
        "body_ar": "طلبك جاهز وينتظر السائق.",
    },
    "driver_assigned": {
        "title_en": "Driver On The Way! 🚗",
        "title_ar": "السائق في الطريق! 🚗",
        "body_en": "{driver_name} is picking up your order.",
        "body_ar": "{driver_name} يستلم طلبك.",
    },
    "order_delivered": {
        "title_en": "Order Delivered! 🎊",
        "title_ar": "تم التوصيل! 🎊",
        "body_en": "Enjoy your meal! Don't forget to rate your experience.",
        "body_ar": "استمتع بوجبتك! لا تنسَ تقييم تجربتك.",
    },
    "new_promo": {
        "title_en": "Special Offer! 🔥",
        "title_ar": "عرض خاص! 🔥",
        "body_en": "Use code {promo_code} for {discount}% off your next order!",
        "body_ar": "استخدم الكود {promo_code} للحصول على خصم {discount}%!",
    },
}


class TemplateUpdate(BaseModel):
    title_en: Optional[str] = None
    title_ar: Optional[str] = None
    body_en: Optional[str] = None
    body_ar: Optional[str] = None


# ==================== Endpoints ====================

@router.get("")
async def get_templates(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Get all notification templates (Admin).
    """
    result = await db.execute(select(NotificationTemplate))
    templates = result.scalars().all()
    
    # If no templates in DB, return defaults
    if not templates:
        return [
            {"key": k, **v, "is_active": True}
            for k, v in DEFAULT_TEMPLATES.items()
        ]
    
    return [
        {
            "id": t.id,
            "key": t.key,
            "title_en": t.title_en,
            "title_ar": t.title_ar,
            "body_en": t.body_en,
            "body_ar": t.body_ar,
            "is_active": t.is_active,
        }
        for t in templates
    ]


@router.put("/{template_key}")
async def update_template(
    template_key: str,
    template_in: TemplateUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update a notification template (Admin).
    """
    result = await db.execute(
        select(NotificationTemplate).where(NotificationTemplate.key == template_key)
    )
    template = result.scalars().first()
    
    if not template:
        # Create from default
        if template_key not in DEFAULT_TEMPLATES:
            raise HTTPException(status_code=404, detail="Template not found")
        
        default = DEFAULT_TEMPLATES[template_key]
        template = NotificationTemplate(
            key=template_key,
            title_en=default["title_en"],
            title_ar=default["title_ar"],
            body_en=default["body_en"],
            body_ar=default["body_ar"],
        )
        db.add(template)
    
    update_data = template_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            setattr(template, field, value)
    
    db.add(template)
    await db.commit()
    
    return {"message": "Template updated"}


@router.post("/reset/{template_key}")
async def reset_template(
    template_key: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Reset template to default (Admin).
    """
    if template_key not in DEFAULT_TEMPLATES:
        raise HTTPException(status_code=404, detail="Template not found")
    
    result = await db.execute(
        select(NotificationTemplate).where(NotificationTemplate.key == template_key)
    )
    template = result.scalars().first()
    
    if template:
        await db.delete(template)
        await db.commit()
    
    return {"message": "Template reset to default"}


async def get_template_content(
    db: AsyncSession,
    template_key: str,
    lang: str = "en",
    variables: dict = None,
) -> dict:
    """
    Get template content with variable substitution.
    """
    result = await db.execute(
        select(NotificationTemplate).where(NotificationTemplate.key == template_key)
    )
    template = result.scalars().first()
    
    if template:
        title = template.title_ar if lang == "ar" and template.title_ar else template.title_en
        body = template.body_ar if lang == "ar" and template.body_ar else template.body_en
    else:
        default = DEFAULT_TEMPLATES.get(template_key, {})
        title = default.get(f"title_{lang}", default.get("title_en", ""))
        body = default.get(f"body_{lang}", default.get("body_en", ""))
    
    # Variable substitution
    if variables:
        for key, value in variables.items():
            title = title.replace(f"{{{key}}}", str(value))
            body = body.replace(f"{{{key}}}", str(value))
    
    return {"title": title, "body": body}
