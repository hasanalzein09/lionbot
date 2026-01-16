"""
Order Receipts API - Generate and send receipts
"""
from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from app.db.session import get_db
from app.models.user import User
from app.models.order import Order
from app.api import deps

router = APIRouter()


@router.get("/{order_id}")
async def get_order_receipt(
    order_id: int,
    lang: str = "en",
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get order receipt.
    """
    result = await db.execute(
        select(Order).where(
            Order.id == order_id,
            Order.customer_phone == current_user.phone_number
        )
    )
    order = result.scalars().first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Calculate totals
    items = order.items or []
    subtotal = sum(item.get('price', 0) * item.get('quantity', 1) for item in items)
    delivery_fee = 2.0
    total = float(order.total_amount) if order.total_amount else subtotal + delivery_fee
    
    labels = {
        "en": {
            "receipt_title": "Order Receipt",
            "order_number": "Order #",
            "date": "Date",
            "items": "Items",
            "subtotal": "Subtotal",
            "delivery_fee": "Delivery Fee",
            "discount": "Discount",
            "total": "Total",
            "payment_method": "Payment Method",
            "cash_on_delivery": "Cash on Delivery",
            "delivery_address": "Delivery Address",
            "thank_you": "Thank you for ordering with Lion Delivery! 🦁",
        },
        "ar": {
            "receipt_title": "إيصال الطلب",
            "order_number": "رقم الطلب #",
            "date": "التاريخ",
            "items": "الأصناف",
            "subtotal": "المجموع الفرعي",
            "delivery_fee": "رسوم التوصيل",
            "discount": "الخصم",
            "total": "الإجمالي",
            "payment_method": "طريقة الدفع",
            "cash_on_delivery": "الدفع عند الاستلام",
            "delivery_address": "عنوان التوصيل",
            "thank_you": "شكراً لطلبك من Lion Delivery! 🦁",
        },
    }
    
    l = labels.get(lang, labels["en"])
    
    return {
        "receipt": {
            "order_id": order.id,
            "order_number": f"LD-{order.id:06d}",
            "date": order.created_at.strftime("%Y-%m-%d %H:%M") if order.created_at else None,
            "customer_name": order.customer_name,
            "customer_phone": order.customer_phone,
            "delivery_address": order.delivery_address,
            "restaurant_name": order.restaurant.name if order.restaurant else "Unknown",
            "items": [
                {
                    "name": item.get('name', 'Item'),
                    "quantity": item.get('quantity', 1),
                    "price": item.get('price', 0),
                    "total": item.get('price', 0) * item.get('quantity', 1),
                }
                for item in items
            ],
            "subtotal": round(subtotal, 2),
            "delivery_fee": delivery_fee,
            "discount": 0,
            "total": round(total, 2),
            "payment_method": l["cash_on_delivery"],
            "status": order.status.value if hasattr(order.status, 'value') else order.status,
        },
        "labels": l,
        "formatted": format_receipt_text(order, items, l, lang),
    }


def format_receipt_text(order, items, labels, lang):
    """Format receipt as text for sharing."""
    lines = [
        "=" * 40,
        "🦁 LION DELIVERY",
        "=" * 40,
        "",
        f"{labels['order_number']}{order.id}",
        f"{labels['date']}: {order.created_at.strftime('%Y-%m-%d %H:%M') if order.created_at else '-'}",
        "",
        "-" * 40,
        labels["items"],
        "-" * 40,
    ]
    
    subtotal = 0
    for item in items:
        qty = item.get('quantity', 1)
        price = item.get('price', 0)
        total = qty * price
        subtotal += total
        lines.append(f"{item.get('name', 'Item')} x{qty} - ${total:.2f}")
    
    lines.extend([
        "-" * 40,
        f"{labels['subtotal']}: ${subtotal:.2f}",
        f"{labels['delivery_fee']}: $2.00",
        "-" * 40,
        f"{labels['total']}: ${(subtotal + 2):.2f}",
        "",
        f"{labels['payment_method']}: {labels['cash_on_delivery']}",
        f"{labels['delivery_address']}: {order.delivery_address or '-'}",
        "",
        "=" * 40,
        labels["thank_you"],
        "=" * 40,
    ])
    
    return "\n".join(lines)


@router.post("/{order_id}/send")
async def send_receipt(
    order_id: int,
    method: str = "whatsapp",  # whatsapp, email, sms
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Send receipt via WhatsApp/Email/SMS.
    """
    result = await db.execute(
        select(Order).where(
            Order.id == order_id,
            Order.customer_phone == current_user.phone_number
        )
    )
    order = result.scalars().first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # TODO: Implement actual sending via WhatsApp/Email/SMS
    
    return {
        "message": f"Receipt sent via {method}",
        "order_id": order_id,
    }
