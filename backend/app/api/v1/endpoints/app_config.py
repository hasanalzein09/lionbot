"""
App Configuration API - Version check, Terms, Privacy, etc.
"""
from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from datetime import datetime

from app.db.session import get_db
from app.models.user import User
from app.api import deps


router = APIRouter()


# App versions
APP_CONFIG = {
    "customer_app": {
        "min_version": "1.0.0",
        "latest_version": "1.0.0",
        "force_update": False,
        "update_url_ios": "https://apps.apple.com/app/lion-delivery",
        "update_url_android": "https://play.google.com/store/apps/details?id=com.liondelivery.customer",
    },
    "driver_app": {
        "min_version": "1.0.0",
        "latest_version": "1.0.0",
        "force_update": False,
    },
    "restaurant_app": {
        "min_version": "1.0.0",
        "latest_version": "1.0.0",
        "force_update": False,
    },
}


class VersionCheck(BaseModel):
    app_type: str  # customer_app, driver_app, restaurant_app
    current_version: str
    platform: str = "android"  # ios, android


# ==================== Endpoints ====================

@router.post("/version-check")
async def check_app_version(
    data: VersionCheck,
) -> Any:
    """
    Check if app version is up to date.
    """
    config = APP_CONFIG.get(data.app_type)
    
    if not config:
        return {"update_required": False}
    
    current = parse_version(data.current_version)
    min_version = parse_version(config["min_version"])
    latest = parse_version(config["latest_version"])
    
    force_update = current < min_version
    update_available = current < latest
    
    return {
        "update_required": force_update,
        "update_available": update_available,
        "latest_version": config["latest_version"],
        "min_version": config["min_version"],
        "update_url": config.get(f"update_url_{data.platform}"),
        "force_update": config["force_update"] and force_update,
    }


@router.get("/terms")
async def get_terms_of_service(
    lang: str = "en",
) -> Any:
    """
    Get Terms of Service.
    """
    terms = {
        "en": """
# Terms of Service

## 1. Introduction
Welcome to Lion Delivery. By using our service, you agree to these terms.

## 2. Service Description
Lion Delivery connects customers with restaurants for food delivery services.

## 3. User Responsibilities
- Provide accurate delivery information
- Be available to receive orders
- Pay for orders upon delivery

## 4. Cancellation Policy
Orders can be cancelled within 5 minutes of placement. After that, contact support.

## 5. Liability
Lion Delivery is not responsible for food quality or restaurant operations.

Last updated: December 2024
        """,
        "ar": """
# شروط الخدمة

## 1. مقدمة
مرحباً بك في Lion Delivery. باستخدام خدمتنا، أنت توافق على هذه الشروط.

## 2. وصف الخدمة
Lion Delivery يربط العملاء بالمطاعم لخدمات توصيل الطعام.

## 3. مسؤوليات المستخدم
- تقديم معلومات توصيل دقيقة
- أن تكون متاحاً لاستلام الطلبات
- دفع ثمن الطلبات عند التوصيل

## 4. سياسة الإلغاء
يمكن إلغاء الطلبات خلال 5 دقائق. بعدها، تواصل مع الدعم.

## 5. المسؤولية
Lion Delivery غير مسؤول عن جودة الطعام أو عمليات المطعم.

آخر تحديث: ديسمبر 2024
        """,
    }
    
    return {
        "content": terms.get(lang, terms["en"]).strip(),
        "last_updated": "2024-12-01",
    }


@router.get("/privacy")
async def get_privacy_policy(
    lang: str = "en",
) -> Any:
    """
    Get Privacy Policy.
    """
    privacy = {
        "en": """
# Privacy Policy

## Data We Collect
- Name, phone number, email
- Delivery addresses
- Order history
- Location data (for delivery)

## How We Use Data
- Process and deliver orders
- Improve our service
- Send notifications about orders
- Marketing (with your consent)

## Data Security
We use industry-standard encryption to protect your data.

## Your Rights
- Access your data
- Request data deletion
- Opt out of marketing

Contact: privacy@liondelivery.app
        """,
        "ar": """
# سياسة الخصوصية

## البيانات التي نجمعها
- الاسم، رقم الهاتف، البريد الإلكتروني
- عناوين التوصيل
- سجل الطلبات
- بيانات الموقع (للتوصيل)

## كيف نستخدم البيانات
- معالجة وتوصيل الطلبات
- تحسين خدمتنا
- إرسال إشعارات عن الطلبات
- التسويق (بموافقتك)

## أمان البيانات
نستخدم تشفيراً قياسياً لحماية بياناتك.

## حقوقك
- الوصول لبياناتك
- طلب حذف البيانات
- إلغاء الاشتراك في التسويق

تواصل: privacy@liondelivery.app
        """,
    }
    
    return {
        "content": privacy.get(lang, privacy["en"]).strip(),
        "last_updated": "2024-12-01",
    }


@router.get("/contact")
async def get_contact_info() -> Any:
    """
    Get contact information.
    """
    return {
        "support_email": "support@liondelivery.app",
        "support_phone": "+961 1 234 567",
        "support_whatsapp": "+961 71 234 567",
        "working_hours": "24/7",
        "social": {
            "facebook": "https://facebook.com/liondelivery",
            "instagram": "https://instagram.com/liondelivery",
            "twitter": "https://twitter.com/liondelivery",
        },
    }


@router.get("/config")
async def get_app_config() -> Any:
    """
    Get general app configuration.
    """
    return {
        "delivery_fee_base": 2.0,
        "free_delivery_threshold": 50.0,
        "max_delivery_distance_km": 15,
        "order_cancellation_window_minutes": 5,
        "referral_bonus_points": 500,
        "new_user_bonus_points": 200,
        "commission_rate": 0.15,
        "supported_languages": ["en", "ar"],
        "currency": "USD",
        "currency_symbol": "$",
    }


def parse_version(version: str) -> tuple:
    """Parse version string to tuple for comparison."""
    try:
        return tuple(int(x) for x in version.split("."))
    except:
        return (0, 0, 0)
