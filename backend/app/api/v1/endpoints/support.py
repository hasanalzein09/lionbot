"""
Customer Support API - Support tickets and help
"""
from typing import Any, Optional, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from datetime import datetime
from enum import Enum

from app.db.session import get_db
from app.models.user import User, UserRole
from app.api import deps

# Model
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum as SQLEnum
from app.db.base_class import Base


router = APIRouter()


class TicketStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class TicketCategory(str, Enum):
    ORDER_ISSUE = "order_issue"
    PAYMENT = "payment"
    DELIVERY = "delivery"
    ACCOUNT = "account"
    OTHER = "other"


class SupportTicket(Base):
    __tablename__ = "support_tickets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    order_id = Column(Integer, ForeignKey("order.id"), nullable=True)
    category = Column(String(50), default="other")
    subject = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    status = Column(String(20), default="open")
    admin_response = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TicketCreate(BaseModel):
    category: TicketCategory
    subject: str
    message: str
    order_id: Optional[int] = None


class TicketResponse(BaseModel):
    response: str


# ==================== Endpoints ====================

@router.post("")
async def create_ticket(
    ticket_in: TicketCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Create a support ticket.
    """
    ticket = SupportTicket(
        user_id=current_user.id,
        order_id=ticket_in.order_id,
        category=ticket_in.category.value,
        subject=ticket_in.subject,
        message=ticket_in.message,
    )
    
    db.add(ticket)
    await db.commit()
    await db.refresh(ticket)
    
    return {
        "message": "Ticket created. We'll respond within 24 hours.",
        "ticket_id": ticket.id,
    }


@router.get("")
async def get_my_tickets(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get user's support tickets.
    """
    result = await db.execute(
        select(SupportTicket)
        .where(SupportTicket.user_id == current_user.id)
        .order_by(SupportTicket.created_at.desc())
    )
    tickets = result.scalars().all()
    
    return [
        {
            "id": t.id,
            "category": t.category,
            "subject": t.subject,
            "status": t.status,
            "has_response": t.admin_response is not None,
            "created_at": t.created_at.isoformat() if t.created_at else None,
        }
        for t in tickets
    ]


@router.get("/{ticket_id}")
async def get_ticket(
    ticket_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get ticket details.
    """
    result = await db.execute(
        select(SupportTicket).where(
            SupportTicket.id == ticket_id,
            SupportTicket.user_id == current_user.id
        )
    )
    ticket = result.scalars().first()
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    return {
        "id": ticket.id,
        "category": ticket.category,
        "subject": ticket.subject,
        "message": ticket.message,
        "status": ticket.status,
        "order_id": ticket.order_id,
        "admin_response": ticket.admin_response,
        "created_at": ticket.created_at.isoformat() if ticket.created_at else None,
        "updated_at": ticket.updated_at.isoformat() if ticket.updated_at else None,
    }


# Admin endpoints
@router.get("/admin/all")
async def get_all_tickets(
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Get all tickets (Admin).
    """
    query = select(SupportTicket).order_by(SupportTicket.created_at.desc())
    
    if status:
        query = query.where(SupportTicket.status == status)
    
    result = await db.execute(query)
    tickets = result.scalars().all()
    
    return [
        {
            "id": t.id,
            "user_id": t.user_id,
            "category": t.category,
            "subject": t.subject,
            "status": t.status,
            "created_at": t.created_at.isoformat() if t.created_at else None,
        }
        for t in tickets
    ]


@router.post("/admin/{ticket_id}/respond")
async def respond_to_ticket(
    ticket_id: int,
    response: TicketResponse,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Respond to a ticket (Admin).
    """
    result = await db.execute(
        select(SupportTicket).where(SupportTicket.id == ticket_id)
    )
    ticket = result.scalars().first()
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    ticket.admin_response = response.response
    ticket.status = "resolved"
    
    db.add(ticket)
    await db.commit()
    
    # TODO: Send notification to user
    
    return {"message": "Response sent"}


@router.patch("/admin/{ticket_id}/status")
async def update_ticket_status(
    ticket_id: int,
    status: TicketStatus,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update ticket status (Admin).
    """
    result = await db.execute(
        select(SupportTicket).where(SupportTicket.id == ticket_id)
    )
    ticket = result.scalars().first()
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    ticket.status = status.value
    db.add(ticket)
    await db.commit()
    
    return {"message": f"Status updated to {status.value}"}
