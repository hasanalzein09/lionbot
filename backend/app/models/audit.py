"""
Audit Trail Model for tracking changes and actions in the system.
Provides accountability and traceability for admin actions.
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from datetime import datetime
import enum


class AuditAction(str, enum.Enum):
    """Types of auditable actions."""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    LOGIN_FAILED = "login_failed"
    PASSWORD_CHANGE = "password_change"
    STATUS_CHANGE = "status_change"
    PERMISSION_CHANGE = "permission_change"
    EXPORT = "export"
    IMPORT = "import"
    VIEW = "view"


class AuditLog(Base):
    """
    Audit log for tracking all significant actions in the system.

    This provides:
    - Who did what and when
    - What changed (before/after values)
    - IP address and user agent for security
    """
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, index=True)

    # Who performed the action
    user_id = Column(Integer, ForeignKey("user.id", ondelete="SET NULL"), nullable=True, index=True)
    user_email = Column(String, nullable=True)  # Stored for reference even if user is deleted

    # What action was performed
    action = Column(Enum(AuditAction), nullable=False, index=True)
    entity_type = Column(String, nullable=False, index=True)  # e.g., "restaurant", "order", "user"
    entity_id = Column(Integer, nullable=True, index=True)  # ID of the affected entity

    # Details of the action
    description = Column(String, nullable=True)
    old_values = Column(Text, nullable=True)  # JSON string of previous values
    new_values = Column(Text, nullable=True)  # JSON string of new values

    # Request metadata
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)

    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationship
    user = relationship("User")

    def __repr__(self):
        return f"<AuditLog {self.action} {self.entity_type}:{self.entity_id} by user:{self.user_id}>"
