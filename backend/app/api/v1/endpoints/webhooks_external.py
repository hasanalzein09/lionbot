"""
External Webhooks API - Send events to external systems
"""
from typing import Any, Optional, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, HttpUrl
from datetime import datetime
import httpx
import json

from app.db.session import get_db
from app.models.user import User
from app.api import deps

# Model
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON
from app.db.base_class import Base


router = APIRouter()


class Webhook(Base):
    __tablename__ = "webhooks"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    url = Column(Text, nullable=False)
    secret = Column(String(100), nullable=True)  # For signing
    events = Column(JSON, default=[])  # List of events to subscribe
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_triggered = Column(DateTime, nullable=True)
    failure_count = Column(Integer, default=0)


class WebhookLog(Base):
    __tablename__ = "webhook_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    webhook_id = Column(Integer, nullable=False)
    event = Column(String(50), nullable=False)
    payload = Column(JSON, nullable=True)
    response_code = Column(Integer, nullable=True)
    response_body = Column(Text, nullable=True)
    success = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


# Supported events
WEBHOOK_EVENTS = [
    "order.created",
    "order.accepted",
    "order.preparing",
    "order.ready",
    "order.delivered",
    "order.cancelled",
    "customer.registered",
    "restaurant.created",
    "review.created",
]


class WebhookCreate(BaseModel):
    name: str
    url: str
    secret: Optional[str] = None
    events: List[str]


# ==================== Endpoints ====================

@router.get("")
async def list_webhooks(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    List all webhooks (Admin).
    """
    result = await db.execute(select(Webhook))
    webhooks = result.scalars().all()
    
    return [
        {
            "id": w.id,
            "name": w.name,
            "url": w.url,
            "events": w.events,
            "is_active": w.is_active,
            "failure_count": w.failure_count,
            "last_triggered": w.last_triggered.isoformat() if w.last_triggered else None,
        }
        for w in webhooks
    ]


@router.post("")
async def create_webhook(
    webhook_in: WebhookCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Create a new webhook (Admin).
    """
    # Validate events
    for event in webhook_in.events:
        if event not in WEBHOOK_EVENTS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid event: {event}. Valid events: {WEBHOOK_EVENTS}"
            )
    
    webhook = Webhook(
        name=webhook_in.name,
        url=webhook_in.url,
        secret=webhook_in.secret,
        events=webhook_in.events,
    )
    
    db.add(webhook)
    await db.commit()
    await db.refresh(webhook)
    
    return {"message": "Webhook created", "webhook_id": webhook.id}


@router.get("/events")
async def get_available_events() -> Any:
    """
    Get list of available webhook events.
    """
    return {"events": WEBHOOK_EVENTS}


@router.delete("/{webhook_id}")
async def delete_webhook(
    webhook_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Delete a webhook (Admin).
    """
    result = await db.execute(select(Webhook).where(Webhook.id == webhook_id))
    webhook = result.scalars().first()
    
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    await db.delete(webhook)
    await db.commit()
    
    return {"message": "Webhook deleted"}


@router.post("/{webhook_id}/test")
async def test_webhook(
    webhook_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Send test event to webhook (Admin).
    """
    result = await db.execute(select(Webhook).where(Webhook.id == webhook_id))
    webhook = result.scalars().first()
    
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    payload = {
        "event": "test",
        "timestamp": datetime.utcnow().isoformat(),
        "data": {"message": "This is a test webhook from Lion Delivery"},
    }
    
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                webhook.url,
                json=payload,
                headers={"Content-Type": "application/json"},
            )
            
            return {
                "success": response.status_code < 400,
                "status_code": response.status_code,
                "response": response.text[:500],
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


@router.get("/{webhook_id}/logs")
async def get_webhook_logs(
    webhook_id: int,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Get webhook delivery logs (Admin).
    """
    result = await db.execute(
        select(WebhookLog)
        .where(WebhookLog.webhook_id == webhook_id)
        .order_by(WebhookLog.created_at.desc())
        .limit(limit)
    )
    logs = result.scalars().all()
    
    return [
        {
            "id": log.id,
            "event": log.event,
            "success": log.success,
            "response_code": log.response_code,
            "created_at": log.created_at.isoformat() if log.created_at else None,
        }
        for log in logs
    ]


async def trigger_webhook(
    db: AsyncSession,
    event: str,
    payload: dict,
):
    """
    Trigger webhooks for an event (called internally).
    """
    result = await db.execute(
        select(Webhook).where(
            Webhook.is_active == True,
        )
    )
    webhooks = result.scalars().all()
    
    for webhook in webhooks:
        if event in webhook.events or "*" in webhook.events:
            try:
                async with httpx.AsyncClient(timeout=10) as client:
                    full_payload = {
                        "event": event,
                        "timestamp": datetime.utcnow().isoformat(),
                        "data": payload,
                    }
                    
                    response = await client.post(
                        webhook.url,
                        json=full_payload,
                        headers={"Content-Type": "application/json"},
                    )
                    
                    # Log result
                    log = WebhookLog(
                        webhook_id=webhook.id,
                        event=event,
                        payload=payload,
                        response_code=response.status_code,
                        response_body=response.text[:1000],
                        success=response.status_code < 400,
                    )
                    db.add(log)
                    
                    # Update webhook
                    webhook.last_triggered = datetime.utcnow()
                    if response.status_code >= 400:
                        webhook.failure_count += 1
                    else:
                        webhook.failure_count = 0
                    db.add(webhook)
                    
            except Exception as e:
                log = WebhookLog(
                    webhook_id=webhook.id,
                    event=event,
                    payload=payload,
                    success=False,
                    response_body=str(e),
                )
                db.add(log)
                webhook.failure_count += 1
                db.add(webhook)
    
    await db.commit()
