from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional

from app.db.session import get_db
from app.api import deps
from app.models.user import User
from app.services.fcm_service import fcm_service

router = APIRouter()


class TokenRegisterRequest(BaseModel):
    fcm_token: str


class SendNotificationRequest(BaseModel):
    user_id: Optional[int] = None
    topic: Optional[str] = None
    title: str
    body: str
    data: Optional[dict] = None


@router.post("/register-token")
async def register_fcm_token(
    request: TokenRegisterRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Register FCM token for the current user."""
    current_user.fcm_token = request.fcm_token
    await db.commit()
    
    return {"success": True, "message": "FCM token registered successfully"}


@router.delete("/unregister-token")
async def unregister_fcm_token(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    """Unregister FCM token for the current user."""
    current_user.fcm_token = None
    await db.commit()
    
    return {"success": True, "message": "FCM token unregistered"}


@router.post("/send")
async def send_notification(
    request: SendNotificationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
):
    """Send a push notification (admin only)."""
    from sqlalchemy import select
    
    if request.topic:
        # Send to topic
        success = await fcm_service.send_to_topic(
            topic=request.topic,
            title=request.title,
            body=request.body,
            data=request.data,
        )
        return {"success": success, "sent_to": f"topic:{request.topic}"}
    
    elif request.user_id:
        # Send to specific user
        result = await db.execute(
            select(User).where(User.id == request.user_id)
        )
        user = result.scalars().first()
        
        if not user or not user.fcm_token:
            raise HTTPException(status_code=404, detail="User not found or no FCM token")
        
        success = await fcm_service.send_to_token(
            token=user.fcm_token,
            title=request.title,
            body=request.body,
            data=request.data,
        )
        return {"success": success, "sent_to": f"user:{request.user_id}"}
    
    else:
        raise HTTPException(status_code=400, detail="Provide either user_id or topic")


@router.post("/notify-all-drivers")
async def notify_all_drivers(
    title: str,
    body: str,
    current_user: User = Depends(deps.get_current_active_superuser),
):
    """Send notification to all drivers via topic."""
    success = await fcm_service.send_to_topic(
        topic="drivers",
        title=title,
        body=body,
        data={"type": "broadcast"},
    )
    return {"success": success}


@router.post("/notify-all-restaurants")
async def notify_all_restaurants(
    title: str,
    body: str,
    current_user: User = Depends(deps.get_current_active_superuser),
):
    """Send notification to all restaurants via topic."""
    success = await fcm_service.send_to_topic(
        topic="restaurants",
        title=title,
        body=body,
        data={"type": "broadcast"},
    )
    return {"success": success}
