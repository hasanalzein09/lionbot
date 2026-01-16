"""
Audit Service for logging all significant actions in the system.
Provides methods to create audit entries and query audit history.
"""
import json
import logging
from typing import Any, Dict, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from starlette.requests import Request

from app.models.audit import AuditLog, AuditAction
from app.models.user import User

logger = logging.getLogger(__name__)


class AuditService:
    """Service for managing audit logs."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def log(
        self,
        action: AuditAction,
        entity_type: str,
        entity_id: Optional[int] = None,
        description: Optional[str] = None,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        user: Optional[User] = None,
        request: Optional[Request] = None,
    ) -> AuditLog:
        """
        Create an audit log entry.

        Args:
            action: The type of action performed
            entity_type: The type of entity affected (e.g., "restaurant", "order")
            entity_id: The ID of the affected entity
            description: Human-readable description of the action
            old_values: Previous values (for updates)
            new_values: New values (for creates/updates)
            user: The user who performed the action
            request: The HTTP request (for IP and user agent)

        Returns:
            The created AuditLog entry
        """
        try:
            audit_log = AuditLog(
                user_id=user.id if user else None,
                user_email=user.email if user else None,
                action=action,
                entity_type=entity_type,
                entity_id=entity_id,
                description=description,
                old_values=json.dumps(old_values) if old_values else None,
                new_values=json.dumps(new_values) if new_values else None,
                ip_address=self._get_client_ip(request) if request else None,
                user_agent=request.headers.get("User-Agent")[:500] if request else None,
            )

            self.db.add(audit_log)
            await self.db.flush()

            logger.info(
                f"Audit: {action.value} {entity_type}:{entity_id} by user:{user.id if user else 'anonymous'}"
            )

            return audit_log

        except Exception as e:
            logger.error(f"Failed to create audit log: {e}")
            # Don't raise - audit logging shouldn't break the main operation
            return None

    async def log_login(
        self,
        user: User,
        success: bool,
        request: Optional[Request] = None,
    ) -> AuditLog:
        """Log a login attempt."""
        action = AuditAction.LOGIN if success else AuditAction.LOGIN_FAILED
        return await self.log(
            action=action,
            entity_type="user",
            entity_id=user.id if user else None,
            description=f"Login {'successful' if success else 'failed'} for {user.email if user else 'unknown'}",
            user=user if success else None,
            request=request,
        )

    async def log_create(
        self,
        entity_type: str,
        entity_id: int,
        new_values: Dict[str, Any],
        user: User,
        request: Optional[Request] = None,
    ) -> AuditLog:
        """Log a create operation."""
        return await self.log(
            action=AuditAction.CREATE,
            entity_type=entity_type,
            entity_id=entity_id,
            description=f"Created {entity_type} #{entity_id}",
            new_values=self._sanitize_values(new_values),
            user=user,
            request=request,
        )

    async def log_update(
        self,
        entity_type: str,
        entity_id: int,
        old_values: Dict[str, Any],
        new_values: Dict[str, Any],
        user: User,
        request: Optional[Request] = None,
    ) -> AuditLog:
        """Log an update operation."""
        # Only log changed values
        changes = self._get_changes(old_values, new_values)
        if not changes:
            return None

        return await self.log(
            action=AuditAction.UPDATE,
            entity_type=entity_type,
            entity_id=entity_id,
            description=f"Updated {entity_type} #{entity_id}",
            old_values=self._sanitize_values(changes["old"]),
            new_values=self._sanitize_values(changes["new"]),
            user=user,
            request=request,
        )

    async def log_delete(
        self,
        entity_type: str,
        entity_id: int,
        old_values: Dict[str, Any],
        user: User,
        request: Optional[Request] = None,
    ) -> AuditLog:
        """Log a delete operation."""
        return await self.log(
            action=AuditAction.DELETE,
            entity_type=entity_type,
            entity_id=entity_id,
            description=f"Deleted {entity_type} #{entity_id}",
            old_values=self._sanitize_values(old_values),
            user=user,
            request=request,
        )

    async def log_status_change(
        self,
        entity_type: str,
        entity_id: int,
        old_status: str,
        new_status: str,
        user: User,
        request: Optional[Request] = None,
    ) -> AuditLog:
        """Log a status change."""
        return await self.log(
            action=AuditAction.STATUS_CHANGE,
            entity_type=entity_type,
            entity_id=entity_id,
            description=f"Changed {entity_type} #{entity_id} status from {old_status} to {new_status}",
            old_values={"status": old_status},
            new_values={"status": new_status},
            user=user,
            request=request,
        )

    async def get_entity_history(
        self,
        entity_type: str,
        entity_id: int,
        limit: int = 50,
    ) -> list:
        """Get audit history for a specific entity."""
        result = await self.db.execute(
            select(AuditLog)
            .where(
                and_(
                    AuditLog.entity_type == entity_type,
                    AuditLog.entity_id == entity_id,
                )
            )
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()

    async def get_user_activity(
        self,
        user_id: int,
        days: int = 30,
        limit: int = 100,
    ) -> list:
        """Get recent activity for a specific user."""
        since = datetime.utcnow() - timedelta(days=days)
        result = await self.db.execute(
            select(AuditLog)
            .where(
                and_(
                    AuditLog.user_id == user_id,
                    AuditLog.created_at >= since,
                )
            )
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()

    async def get_recent_logs(
        self,
        limit: int = 100,
        action: Optional[AuditAction] = None,
        entity_type: Optional[str] = None,
    ) -> list:
        """Get recent audit logs with optional filters."""
        query = select(AuditLog)

        conditions = []
        if action:
            conditions.append(AuditLog.action == action)
        if entity_type:
            conditions.append(AuditLog.entity_type == entity_type)

        if conditions:
            query = query.where(and_(*conditions))

        query = query.order_by(AuditLog.created_at.desc()).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()

    def _get_client_ip(self, request: Request) -> Optional[str]:
        """Extract client IP from request, handling proxies."""
        if not request:
            return None

        # Check X-Forwarded-For header
        x_forwarded_for = request.headers.get("X-Forwarded-For")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()

        # Check X-Real-IP header
        x_real_ip = request.headers.get("X-Real-IP")
        if x_real_ip:
            return x_real_ip

        # Fall back to direct client
        if request.client:
            return request.client.host

        return None

    def _sanitize_values(self, values: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive fields from values before logging."""
        if not values:
            return values

        sensitive_fields = {
            "password", "hashed_password", "secret", "token",
            "api_key", "access_token", "refresh_token", "credit_card",
        }

        return {
            k: "[REDACTED]" if k.lower() in sensitive_fields else v
            for k, v in values.items()
        }

    def _get_changes(
        self,
        old_values: Dict[str, Any],
        new_values: Dict[str, Any],
    ) -> Optional[Dict[str, Dict[str, Any]]]:
        """Get only the fields that changed."""
        if not old_values or not new_values:
            return None

        old_changed = {}
        new_changed = {}

        for key in set(old_values.keys()) | set(new_values.keys()):
            old_val = old_values.get(key)
            new_val = new_values.get(key)

            if old_val != new_val:
                old_changed[key] = old_val
                new_changed[key] = new_val

        if not old_changed:
            return None

        return {"old": old_changed, "new": new_changed}


# Convenience function for creating audit service
def get_audit_service(db: AsyncSession) -> AuditService:
    """Get an AuditService instance."""
    return AuditService(db)
