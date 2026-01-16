"""
Order Export API - Export orders to CSV/JSON
"""
from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
import csv
import io
import json

from app.db.session import get_db
from app.models.user import User, UserRole
from app.models.order import Order, OrderStatus
from app.api import deps

router = APIRouter()


@router.get("/orders")
async def export_orders(
    format: str = Query("csv", enum=["csv", "json"]),
    days: int = Query(30, ge=1, le=365),
    status: Optional[str] = None,
    restaurant_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Export orders to CSV or JSON (Admin).
    """
    since = datetime.utcnow() - timedelta(days=days)
    
    query = select(Order).where(Order.created_at >= since)
    
    if status:
        query = query.where(Order.status == status)
    
    if restaurant_id:
        query = query.where(Order.restaurant_id == restaurant_id)
    
    query = query.order_by(Order.created_at.desc())
    
    result = await db.execute(query)
    orders = result.scalars().all()
    
    data = [
        {
            "id": o.id,
            "restaurant_id": o.restaurant_id,
            "customer_name": o.customer_name,
            "customer_phone": o.customer_phone,
            "status": o.status.value if hasattr(o.status, 'value') else o.status,
            "total_amount": float(o.total_amount) if o.total_amount else 0,
            "delivery_address": o.delivery_address,
            "created_at": o.created_at.isoformat() if o.created_at else None,
            "items_count": len(o.items) if o.items else 0,
        }
        for o in orders
    ]
    
    if format == "json":
        return {
            "exported_at": datetime.utcnow().isoformat(),
            "total_orders": len(data),
            "orders": data,
        }
    
    # CSV export
    output = io.StringIO()
    if data:
        writer = csv.DictWriter(output, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    
    output.seek(0)
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=orders_{datetime.now().strftime('%Y%m%d')}.csv"
        }
    )


@router.get("/revenue")
async def export_revenue_report(
    days: int = Query(30, ge=1, le=365),
    restaurant_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Export revenue report (Admin).
    """
    from sqlalchemy import func
    
    since = datetime.utcnow() - timedelta(days=days)
    
    query = select(Order).where(
        Order.created_at >= since,
        Order.status == OrderStatus.DELIVERED
    )
    
    if restaurant_id:
        query = query.where(Order.restaurant_id == restaurant_id)
    
    result = await db.execute(query)
    orders = result.scalars().all()
    
    # Calculate daily revenue
    daily_revenue = {}
    for order in orders:
        if order.created_at:
            date_key = order.created_at.strftime("%Y-%m-%d")
            if date_key not in daily_revenue:
                daily_revenue[date_key] = {"orders": 0, "revenue": 0}
            daily_revenue[date_key]["orders"] += 1
            daily_revenue[date_key]["revenue"] += float(order.total_amount or 0)
    
    # Sort by date
    sorted_days = sorted(daily_revenue.items())
    
    total_revenue = sum(d["revenue"] for d in daily_revenue.values())
    total_orders = sum(d["orders"] for d in daily_revenue.values())
    
    return {
        "period_days": days,
        "restaurant_id": restaurant_id,
        "total_revenue": round(total_revenue, 2),
        "total_orders": total_orders,
        "average_order_value": round(total_revenue / total_orders, 2) if total_orders > 0 else 0,
        "daily_breakdown": [
            {
                "date": date,
                "orders": data["orders"],
                "revenue": round(data["revenue"], 2),
            }
            for date, data in sorted_days
        ],
    }


@router.get("/customers")
async def export_customers(
    format: str = Query("json", enum=["csv", "json"]),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Export customer list (Admin).
    """
    result = await db.execute(
        select(User).where(User.role == UserRole.CUSTOMER)
    )
    customers = result.scalars().all()
    
    data = [
        {
            "id": c.id,
            "name": c.full_name,
            "phone": c.phone_number,
            "email": c.email,
            "is_active": c.is_active,
        }
        for c in customers
    ]
    
    if format == "csv":
        output = io.StringIO()
        if data:
            writer = csv.DictWriter(output, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        output.seek(0)
        
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=customers_{datetime.now().strftime('%Y%m%d')}.csv"
            }
        )
    
    return {
        "total_customers": len(data),
        "customers": data,
    }
