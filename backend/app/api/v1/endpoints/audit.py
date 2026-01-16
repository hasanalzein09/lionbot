"""
Audit Logs API - Track all important actions in the system
"""
from typing import Any, Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timedelta

from app.db.session import get_db
from app.models.user import User
from app.models.audit import AuditLog, AuditAction
from app.api import deps
from app.services.audit_service import get_audit_service

router = APIRouter()


# ==================== Endpoints ====================

@router.get("")
async def get_audit_logs(
    days: int = Query(7, ge=1, le=90),
    action: Optional[str] = None,
    entity_type: Optional[str] = None,
    user_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Get audit logs (Admin only).

    Filters:
    - days: Number of days to look back (default 7, max 90)
    - action: Filter by action type (create, update, delete, login, etc.)
    - entity_type: Filter by entity (order, restaurant, user, etc.)
    - user_id: Filter by user who performed the action
    """
    since = datetime.utcnow() - timedelta(days=days)

    query = select(AuditLog).where(AuditLog.created_at >= since)

    if action:
        try:
            action_enum = AuditAction(action)
            query = query.where(AuditLog.action == action_enum)
        except ValueError:
            pass  # Invalid action, skip filter

    if entity_type:
        query = query.where(AuditLog.entity_type == entity_type)

    if user_id:
        query = query.where(AuditLog.user_id == user_id)

    query = query.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit)

    result = await db.execute(query)
    logs = result.scalars().all()

    return [
        {
            "id": log.id,
            "user_id": log.user_id,
            "user_email": log.user_email,
            "action": log.action.value if log.action else None,
            "entity_type": log.entity_type,
            "entity_id": log.entity_id,
            "description": log.description,
            "old_values": log.old_values,
            "new_values": log.new_values,
            "ip_address": log.ip_address,
            "created_at": log.created_at.isoformat() if log.created_at else None,
        }
        for log in logs
    ]


@router.get("/actions")
async def get_action_types(
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Get list of action types for filtering.
    """
    return {
        "actions": [action.value for action in AuditAction],
        "entity_types": [
            "user",
            "order",
            "restaurant",
            "menu",
            "menu_item",
            "category",
            "branch",
            "coupon",
            "payout",
            "settings",
        ],
    }


@router.get("/summary")
async def get_audit_summary(
    days: int = Query(7, ge=1, le=30),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Get audit log summary (Admin only).
    """
    since = datetime.utcnow() - timedelta(days=days)

    # Count by action
    result = await db.execute(
        select(AuditLog.action, func.count(AuditLog.id))
        .where(AuditLog.created_at >= since)
        .group_by(AuditLog.action)
    )
    action_counts = {row[0].value if row[0] else "unknown": row[1] for row in result.all()}

    # Count by entity type
    entity_result = await db.execute(
        select(AuditLog.entity_type, func.count(AuditLog.id))
        .where(AuditLog.created_at >= since)
        .group_by(AuditLog.entity_type)
    )
    entity_counts = {row[0] or "unknown": row[1] for row in entity_result.all()}

    # Total logs
    total_result = await db.execute(
        select(func.count(AuditLog.id)).where(AuditLog.created_at >= since)
    )
    total = total_result.scalar()

    # Recent logins
    login_result = await db.execute(
        select(func.count(AuditLog.id))
        .where(AuditLog.created_at >= since)
        .where(AuditLog.action == AuditAction.LOGIN)
    )
    login_count = login_result.scalar()

    # Failed logins
    failed_login_result = await db.execute(
        select(func.count(AuditLog.id))
        .where(AuditLog.created_at >= since)
        .where(AuditLog.action == AuditAction.LOGIN_FAILED)
    )
    failed_login_count = failed_login_result.scalar()

    return {
        "period_days": days,
        "total_logs": total,
        "by_action": action_counts,
        "by_entity": entity_counts,
        "login_count": login_count,
        "failed_login_count": failed_login_count,
    }


@router.get("/entity/{entity_type}/{entity_id}")
async def get_entity_history(
    entity_type: str,
    entity_id: int,
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Get audit history for a specific entity (Admin only).
    """
    audit = get_audit_service(db)
    logs = await audit.get_entity_history(entity_type, entity_id, limit)

    return [
        {
            "id": log.id,
            "user_id": log.user_id,
            "user_email": log.user_email,
            "action": log.action.value if log.action else None,
            "description": log.description,
            "old_values": log.old_values,
            "new_values": log.new_values,
            "ip_address": log.ip_address,
            "created_at": log.created_at.isoformat() if log.created_at else None,
        }
        for log in logs
    ]


@router.get("/user/{user_id}/activity")
async def get_user_activity(
    user_id: int,
    days: int = Query(30, ge=1, le=90),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Get recent activity for a specific user (Admin only).
    """
    audit = get_audit_service(db)
    logs = await audit.get_user_activity(user_id, days, limit)

    return [
        {
            "id": log.id,
            "action": log.action.value if log.action else None,
            "entity_type": log.entity_type,
            "entity_id": log.entity_id,
            "description": log.description,
            "ip_address": log.ip_address,
            "created_at": log.created_at.isoformat() if log.created_at else None,
        }
        for log in logs
    ]
