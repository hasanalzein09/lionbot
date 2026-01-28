"""
Public API endpoints - No authentication required
For the customer-facing website: liondelivery-saida.com
"""
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import datetime, timedelta
import logging

from app.db.session import get_db
from app.models.restaurant import Restaurant, RestaurantCategory
from app.models.menu import Menu, Category, MenuItem, MenuItemVariant
from app.models.order import Order, OrderItem, OrderStatus
from app.models.user import User
from app.core.websocket_manager import ws_manager

logger = logging.getLogger(__name__)

router = APIRouter()


# ==================== ORDER SCHEMAS ====================

class OrderItemCreate(BaseModel):
    product_id: int
    name: str
    name_ar: Optional[str] = None
    price: float
    quantity: int = Field(ge=1)
    variant_id: Optional[int] = None
    variant_name: Optional[str] = None
    variant_price: Optional[float] = None
    notes: Optional[str] = None


class CustomerInfo(BaseModel):
    name: str = Field(min_length=2)
    phone: str = Field(min_length=8)
    address: str = Field(min_length=5)


class CreatePublicOrder(BaseModel):
    restaurant_id: int
    items: List[OrderItemCreate]
    customer: CustomerInfo
    notes: Optional[str] = None
    payment_method: str = "cash"
    scheduled_time: Optional[datetime] = None  # For order scheduling


def slugify(text: str) -> str:
    """Generate a slug from text"""
    return text.lower().replace(" ", "-").replace("&", "and")


# ==================== PUBLIC RESTAURANT ENDPOINTS ====================

@router.get("/restaurants/")
async def get_public_restaurants(
    db: AsyncSession = Depends(get_db),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    search: Optional[str] = Query(None, description="Search by name"),
    sort: str = Query("newest", description="Sort by: newest, name"),
    limit: int = Query(50, le=100),
    offset: int = Query(0),
) -> Any:
    """
    Get all active restaurants for the public website.
    No authentication required.
    """
    query = select(Restaurant).options(selectinload(Restaurant.category)).where(Restaurant.is_active == True)

    # Filter by category
    if category_id:
        query = query.where(Restaurant.category_id == category_id)

    # Search
    if search:
        search_term = f"%{search}%"
        query = query.where(
            (Restaurant.name.ilike(search_term)) |
            (Restaurant.name_ar.ilike(search_term))
        )

    # Sort
    if sort == "name":
        query = query.order_by(Restaurant.name)
    else:  # newest (default) - use id as proxy for creation time
        query = query.order_by(Restaurant.id.desc())

    # Pagination
    query = query.offset(offset).limit(limit)

    result = await db.execute(query)
    restaurants = result.scalars().all()

    # Format response
    return {
        "restaurants": [
            {
                "id": r.id,
                "name": r.name,
                "name_ar": r.name_ar,
                "slug": slugify(r.name),
                "description": r.description,
                "description_ar": r.description_ar,
                "image": r.logo_url,
                "category": r.category.name if r.category else None,
                "category_ar": r.category.name_ar if r.category else None,
                "category_id": r.category_id,
                "phone": r.phone_number,
            }
            for r in restaurants
        ],
        "total": len(restaurants),
        "has_more": len(restaurants) == limit,
    }


@router.get("/restaurants/{restaurant_id}")
async def get_public_restaurant(
    restaurant_id: int,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get a single restaurant by ID for the public website.
    No authentication required.
    """
    result = await db.execute(
        select(Restaurant)
        .options(selectinload(Restaurant.category))
        .where(Restaurant.id == restaurant_id, Restaurant.is_active == True)
    )
    restaurant = result.scalars().first()

    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    return {
        "id": restaurant.id,
        "name": restaurant.name,
        "name_ar": restaurant.name_ar,
        "slug": slugify(restaurant.name),
        "description": restaurant.description,
        "description_ar": restaurant.description_ar,
        "image": restaurant.logo_url,
        "category": restaurant.category.name if restaurant.category else None,
        "category_ar": restaurant.category.name_ar if restaurant.category else None,
        "category_id": restaurant.category_id,
        "phone": restaurant.phone_number,
    }


@router.get("/restaurants/slug/{slug}")
async def get_public_restaurant_by_slug(
    slug: str,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get a single restaurant by slug for the public website.
    No authentication required.
    """
    # Since we don't have a slug column, we search by name matching the slug pattern
    result = await db.execute(
        select(Restaurant)
        .options(selectinload(Restaurant.category))
        .where(Restaurant.is_active == True)
    )
    restaurants = result.scalars().all()

    # Find restaurant whose slugified name matches the slug
    restaurant = None
    for r in restaurants:
        if slugify(r.name) == slug:
            restaurant = r
            break

    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    return {
        "id": restaurant.id,
        "name": restaurant.name,
        "name_ar": restaurant.name_ar,
        "slug": slugify(restaurant.name),
        "description": restaurant.description,
        "description_ar": restaurant.description_ar,
        "image": restaurant.logo_url,
        "category": restaurant.category.name if restaurant.category else None,
        "category_ar": restaurant.category.name_ar if restaurant.category else None,
        "category_id": restaurant.category_id,
        "phone": restaurant.phone_number,
    }


# ==================== PUBLIC CATEGORIES ENDPOINTS ====================

@router.get("/categories/")
async def get_public_categories(
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get all restaurant categories for the public website.
    No authentication required.
    """
    result = await db.execute(
        select(RestaurantCategory)
        .where(RestaurantCategory.is_active == True)
        .order_by(RestaurantCategory.order)
    )
    categories = result.scalars().all()

    return [
        {
            "id": c.id,
            "name": c.name,
            "name_ar": c.name_ar,
            "icon": c.icon,
            "slug": slugify(c.name),
        }
        for c in categories
    ]


# ==================== PUBLIC MENU ENDPOINTS ====================

@router.get("/restaurants/{restaurant_id}/menu")
async def get_public_restaurant_menu(
    restaurant_id: int,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get the menu for a restaurant for the public website.
    No authentication required.
    """
    # Verify restaurant exists and is active
    rest_result = await db.execute(
        select(Restaurant).where(Restaurant.id == restaurant_id, Restaurant.is_active == True)
    )
    restaurant = rest_result.scalars().first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    # Get menu with categories and items
    result = await db.execute(
        select(Menu)
        .options(
            selectinload(Menu.categories)
            .selectinload(Category.items)
            .selectinload(MenuItem.variants)
        )
        .where(Menu.restaurant_id == restaurant_id, Menu.is_active == True)
    )
    menu = result.scalars().first()

    if not menu:
        return {"restaurant_id": restaurant_id, "categories": []}

    return {
        "restaurant_id": restaurant_id,
        "categories": [
            {
                "id": cat.id,
                "name": cat.name,
                "name_ar": cat.name_ar,
                "order": cat.order,
                "items": [
                    {
                        "id": item.id,
                        "name": item.name,
                        "name_ar": item.name_ar,
                        "description": item.description,
                        "description_ar": item.description_ar,
                        "price": float(item.price) if item.price is not None else None,
                        "price_min": float(item.price_min) if item.price_min is not None else None,
                        "price_max": float(item.price_max) if item.price_max is not None else None,
                        "image": item.image_url,
                        "is_available": item.is_available,
                        "has_variants": item.has_variants,
                        "variants": [
                            {
                                "id": v.id,
                                "name": v.name,
                                "name_ar": v.name_ar,
                                "price": float(v.price) if v.price is not None else 0,
                            }
                            for v in sorted(item.variants, key=lambda x: x.order or 0)
                        ] if item.variants else [],
                    }
                    for item in sorted(cat.items, key=lambda x: x.order or 0)
                    if item.is_available
                ]
            }
            for cat in sorted(menu.categories, key=lambda x: x.order or 0)
        ]
    }


# ==================== PUBLIC FEATURED ENDPOINTS ====================

@router.get("/featured/restaurants/")
async def get_featured_restaurants(
    db: AsyncSession = Depends(get_db),
    limit: int = Query(6, le=20),
) -> Any:
    """
    Get featured restaurants for the homepage.
    No authentication required.
    Since we don't have is_featured column, return the first N restaurants.
    """
    result = await db.execute(
        select(Restaurant)
        .options(selectinload(Restaurant.category))
        .where(Restaurant.is_active == True)
        .order_by(Restaurant.id)
        .limit(limit)
    )
    restaurants = result.scalars().all()

    return [
        {
            "id": r.id,
            "name": r.name,
            "name_ar": r.name_ar,
            "slug": slugify(r.name),
            "image": r.logo_url,
            "category": r.category.name if r.category else None,
            "category_ar": r.category.name_ar if r.category else None,
            "phone": r.phone_number,
        }
        for r in restaurants
    ]


# ==================== PUBLIC SEARCH ENDPOINT ====================

@router.get("/search/")
async def public_search(
    q: str = Query(..., min_length=2, description="Search query"),
    db: AsyncSession = Depends(get_db),
    limit: int = Query(20, le=50),
) -> Any:
    """
    Search restaurants and menu items.
    No authentication required.
    """
    search_term = f"%{q}%"

    # Search restaurants
    rest_result = await db.execute(
        select(Restaurant)
        .options(selectinload(Restaurant.category))
        .where(
            Restaurant.is_active == True,
            (Restaurant.name.ilike(search_term)) | (Restaurant.name_ar.ilike(search_term))
        )
        .limit(limit)
    )
    restaurants = rest_result.scalars().all()

    # Search menu items
    items_result = await db.execute(
        select(MenuItem)
        .options(selectinload(MenuItem.category).selectinload(Category.menu))
        .where(
            MenuItem.is_available == True,
            (MenuItem.name.ilike(search_term)) | (MenuItem.name_ar.ilike(search_term))
        )
        .limit(limit)
    )
    items = items_result.scalars().all()

    return {
        "restaurants": [
            {
                "id": r.id,
                "name": r.name,
                "name_ar": r.name_ar,
                "slug": slugify(r.name),
                "image": r.logo_url,
                "category": r.category.name if r.category else None,
                "category_ar": r.category.name_ar if r.category else None,
            }
            for r in restaurants
        ],
        "items": [
            {
                "id": item.id,
                "name": item.name,
                "name_ar": item.name_ar,
                "price": float(item.price) if item.price else None,
                "image": item.image_url,
                "restaurant_id": item.category.menu.restaurant_id if item.category and item.category.menu else None,
            }
            for item in items
            if item.category and item.category.menu
        ],
    }


# ==================== PUBLIC SCHEDULING ENDPOINT ====================

@router.get("/restaurants/{restaurant_id}/delivery-slots")
async def get_delivery_slots(
    restaurant_id: int,
    date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format"),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get available delivery time slots for a restaurant.
    No authentication required.
    Returns slots from 10AM to 10PM in 30-minute intervals.
    """
    # Verify restaurant exists
    rest_result = await db.execute(
        select(Restaurant).where(
            Restaurant.id == restaurant_id,
            Restaurant.is_active == True
        )
    )
    restaurant = rest_result.scalars().first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    # Parse target date or use today
    if date:
        try:
            target_date = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    else:
        target_date = datetime.now()

    # Generate slots from 10AM to 10PM
    slots = []
    now = datetime.now()

    for day_offset in range(7):  # Next 7 days
        slot_date = target_date.date() + timedelta(days=day_offset)

        for hour in range(10, 22):  # 10AM to 10PM
            for minute in [0, 30]:
                slot_time = datetime.combine(slot_date, datetime.min.time().replace(hour=hour, minute=minute))

                # Only include slots at least 1 hour from now
                if slot_time > now + timedelta(hours=1):
                    slots.append({
                        "time": slot_time.strftime("%H:%M"),
                        "display": slot_time.strftime("%I:%M %p"),
                        "display_ar": f"{hour}:{minute:02d}",
                        "datetime": slot_time.isoformat(),
                        "date": slot_date.strftime("%Y-%m-%d"),
                        "date_display": slot_date.strftime("%a, %b %d"),
                    })

    # Group slots by date
    slots_by_date = {}
    for slot in slots:
        date_key = slot["date"]
        if date_key not in slots_by_date:
            slots_by_date[date_key] = {
                "date": date_key,
                "date_display": slot["date_display"],
                "slots": []
            }
        slots_by_date[date_key]["slots"].append({
            "time": slot["time"],
            "display": slot["display"],
            "display_ar": slot["display_ar"],
            "datetime": slot["datetime"],
        })

    return {
        "restaurant_id": restaurant_id,
        "dates": list(slots_by_date.values())[:7],  # Max 7 days
    }


# ==================== PUBLIC ORDER ENDPOINT ====================

@router.post("/orders/")
async def create_public_order(
    order_data: CreatePublicOrder,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Create a new order from the public website.
    No authentication required - uses customer phone number for identification.
    """
    # Verify restaurant exists and is active
    rest_result = await db.execute(
        select(Restaurant).where(
            Restaurant.id == order_data.restaurant_id,
            Restaurant.is_active == True
        )
    )
    restaurant = rest_result.scalars().first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    # Find or create customer user by phone number
    phone = order_data.customer.phone.replace(" ", "").replace("-", "")
    if not phone.startswith("+"):
        if phone.startswith("0"):
            phone = "+961" + phone[1:]
        elif phone.startswith("961"):
            phone = "+" + phone
        else:
            phone = "+961" + phone

    user_result = await db.execute(
        select(User).where(User.phone_number == phone)
    )
    user = user_result.scalars().first()

    if not user:
        # Create new customer user
        user = User(
            phone_number=phone,
            full_name=order_data.customer.name,
            role="customer",
            is_active=True,
        )
        db.add(user)
        await db.flush()

    # Calculate totals
    subtotal = Decimal(0)
    for item in order_data.items:
        item_price = Decimal(str(item.variant_price or item.price))
        subtotal += item_price * item.quantity

    delivery_fee = Decimal("2.00")  # Fixed delivery fee in USD
    total = subtotal + delivery_fee

    # Determine if order is scheduled
    is_scheduled = order_data.scheduled_time is not None

    # Create order
    order = Order(
        user_id=user.id,
        restaurant_id=order_data.restaurant_id,
        status=OrderStatus.NEW,
        total_amount=total,
        delivery_fee=delivery_fee,
        order_type="delivery",
        address=order_data.customer.address,
        scheduled_time=order_data.scheduled_time,
        is_scheduled=is_scheduled,
    )
    db.add(order)
    await db.flush()

    # Create order items
    for item in order_data.items:
        item_price = Decimal(str(item.variant_price or item.price))
        order_item = OrderItem(
            order_id=order.id,
            menu_item_id=item.product_id,
            quantity=item.quantity,
            unit_price=item_price,
            total_price=item_price * item.quantity,
            notes=item.notes,
        )
        db.add(order_item)

    await db.commit()
    await db.refresh(order)

    # Generate order number
    order_number = f"LN-{order.id:06d}"

    logger.info(f"New order created: {order_number} from {phone}" + (f" scheduled for {order.scheduled_time}" if is_scheduled else ""))

    # Send WebSocket notification to restaurant
    try:
        await ws_manager.notify_restaurant(order_data.restaurant_id, {
            "type": "new_order",
            "order_id": order.id,
            "order_number": order_number,
            "is_scheduled": is_scheduled,
            "scheduled_time": order.scheduled_time.isoformat() if order.scheduled_time else None,
        })
        # Broadcast to all online drivers
        await ws_manager.broadcast_new_order({
            "order_id": order.id,
            "order_number": order_number,
            "restaurant_id": order_data.restaurant_id,
            "restaurant_name": restaurant.name,
            "address": order_data.customer.address,
            "total": float(total),
            "is_scheduled": is_scheduled,
            "scheduled_time": order.scheduled_time.isoformat() if order.scheduled_time else None,
        })
    except Exception as e:
        logger.warning(f"Failed to send WebSocket notification: {e}")

    return {
        "success": True,
        "order": {
            "id": order.id,
            "order_number": order_number,
            "status": order.status.value,
            "total": float(total),
            "delivery_fee": float(delivery_fee),
            "subtotal": float(subtotal),
            "is_scheduled": is_scheduled,
            "scheduled_time": order.scheduled_time.isoformat() if order.scheduled_time else None,
            "restaurant": {
                "id": restaurant.id,
                "name": restaurant.name,
                "name_ar": restaurant.name_ar,
            },
            "customer": {
                "name": order_data.customer.name,
                "phone": phone,
                "address": order_data.customer.address,
            },
            "created_at": order.created_at.isoformat() if order.created_at else None,
        },
        "message": "Order placed successfully",
    }


@router.get("/orders/{order_number}")
async def get_public_order(
    order_number: str,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Get order details by order number.
    No authentication required.
    """
    # Extract order ID from order number (LN-000001 -> 1)
    try:
        order_id = int(order_number.replace("LN-", "").lstrip("0") or "0")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid order number format")

    result = await db.execute(
        select(Order)
        .options(
            selectinload(Order.items).selectinload(OrderItem.menu_item),
            selectinload(Order.restaurant),
            selectinload(Order.customer),
        )
        .where(Order.id == order_id)
    )
    order = result.scalars().first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return {
        "id": order.id,
        "order_number": f"LN-{order.id:06d}",
        "status": order.status.value,
        "total": float(order.total_amount),
        "delivery_fee": float(order.delivery_fee) if order.delivery_fee else 0,
        "address": order.address,
        "is_scheduled": order.is_scheduled,
        "scheduled_time": order.scheduled_time.isoformat() if order.scheduled_time else None,
        "restaurant": {
            "id": order.restaurant.id,
            "name": order.restaurant.name,
            "name_ar": order.restaurant.name_ar,
            "phone": order.restaurant.phone_number,
        } if order.restaurant else None,
        "customer": {
            "name": order.customer.full_name,
            "phone": order.customer.phone_number,
        } if order.customer else None,
        "items": [
            {
                "id": item.id,
                "name": item.menu_item.name if item.menu_item else "Unknown",
                "name_ar": item.menu_item.name_ar if item.menu_item else None,
                "quantity": item.quantity,
                "unit_price": float(item.unit_price),
                "total_price": float(item.total_price),
            }
            for item in order.items
        ],
        "created_at": order.created_at.isoformat() if order.created_at else None,
    }
