"""
Cart management for customer orders.
Carts are stored in Redis for fast access and automatic expiration.
"""
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
import json

from app.db.session import get_db
from app.models.user import User
from app.models.menu import MenuItem
from app.models.restaurant import Restaurant
from app.api import deps
from app.services.redis_service import redis_service

router = APIRouter()


# ==================== Schemas ====================

class CartItem(BaseModel):
    menu_item_id: int
    quantity: int
    notes: Optional[str] = None


class CartItemUpdate(BaseModel):
    quantity: int


class CartResponse(BaseModel):
    restaurant_id: Optional[int] = None
    restaurant_name: Optional[str] = None
    items: List[dict] = []
    subtotal: float = 0.0
    delivery_fee: float = 2.0
    total: float = 0.0


# ==================== Helpers ====================

def get_cart_key(user_id: int) -> str:
    return f"cart:{user_id}"


# ==================== Endpoints ====================

@router.get("", response_model=CartResponse)
async def get_cart(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get current user's shopping cart.
    """
    cart_key = get_cart_key(current_user.id)
    cart_data = await redis_service.get(cart_key)
    
    if not cart_data:
        return CartResponse()
    
    cart = json.loads(cart_data)
    
    # Calculate totals
    subtotal = sum(item['price'] * item['quantity'] for item in cart.get('items', []))
    delivery_fee = 2.0
    
    return CartResponse(
        restaurant_id=cart.get('restaurant_id'),
        restaurant_name=cart.get('restaurant_name'),
        items=cart.get('items', []),
        subtotal=subtotal,
        delivery_fee=delivery_fee,
        total=subtotal + delivery_fee,
    )


@router.post("/items")
async def add_to_cart(
    item_in: CartItem,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Add item to cart. Creates new cart if empty.
    """
    # Get menu item details
    result = await db.execute(
        select(MenuItem).where(MenuItem.id == item_in.menu_item_id)
    )
    menu_item = result.scalars().first()
    
    if not menu_item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    
    if not menu_item.is_available:
        raise HTTPException(status_code=400, detail="Item not available")
    
    # Get restaurant
    rest_result = await db.execute(
        select(Restaurant).where(Restaurant.id == menu_item.restaurant_id)
    )
    restaurant = rest_result.scalars().first()
    
    cart_key = get_cart_key(current_user.id)
    cart_data = await redis_service.get(cart_key)
    
    if cart_data:
        cart = json.loads(cart_data)
        # Check if adding from same restaurant
        if cart.get('restaurant_id') and cart['restaurant_id'] != menu_item.restaurant_id:
            raise HTTPException(
                status_code=400,
                detail="Can't add items from different restaurants. Clear cart first."
            )
    else:
        cart = {
            'restaurant_id': menu_item.restaurant_id,
            'restaurant_name': restaurant.name if restaurant else 'Unknown',
            'items': [],
        }
    
    # Check if item already in cart
    existing_item = next(
        (i for i in cart['items'] if i['menu_item_id'] == item_in.menu_item_id),
        None
    )
    
    if existing_item:
        existing_item['quantity'] += item_in.quantity
    else:
        cart['items'].append({
            'menu_item_id': menu_item.id,
            'name': menu_item.name,
            'price': float(menu_item.price),
            'quantity': item_in.quantity,
            'notes': item_in.notes,
        })
    
    # Save cart with 24h expiration
    await redis_service.set(cart_key, json.dumps(cart), ex=86400)
    
    return {"message": "Item added to cart", "cart_items": len(cart['items'])}


@router.put("/items/{menu_item_id}")
async def update_cart_item(
    menu_item_id: int,
    item_update: CartItemUpdate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Update item quantity in cart.
    """
    cart_key = get_cart_key(current_user.id)
    cart_data = await redis_service.get(cart_key)
    
    if not cart_data:
        raise HTTPException(status_code=404, detail="Cart is empty")
    
    cart = json.loads(cart_data)
    
    item = next((i for i in cart['items'] if i['menu_item_id'] == menu_item_id), None)
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not in cart")
    
    if item_update.quantity <= 0:
        cart['items'] = [i for i in cart['items'] if i['menu_item_id'] != menu_item_id]
    else:
        item['quantity'] = item_update.quantity
    
    if not cart['items']:
        await redis_service.delete(cart_key)
        return {"message": "Cart cleared"}
    
    await redis_service.set(cart_key, json.dumps(cart), ex=86400)
    
    return {"message": "Cart updated"}


@router.delete("/items/{menu_item_id}")
async def remove_from_cart(
    menu_item_id: int,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Remove item from cart.
    """
    cart_key = get_cart_key(current_user.id)
    cart_data = await redis_service.get(cart_key)
    
    if not cart_data:
        raise HTTPException(status_code=404, detail="Cart is empty")
    
    cart = json.loads(cart_data)
    cart['items'] = [i for i in cart['items'] if i['menu_item_id'] != menu_item_id]
    
    if not cart['items']:
        await redis_service.delete(cart_key)
        return {"message": "Cart cleared"}
    
    await redis_service.set(cart_key, json.dumps(cart), ex=86400)
    
    return {"message": "Item removed"}


@router.delete("")
async def clear_cart(
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Clear entire cart.
    """
    cart_key = get_cart_key(current_user.id)
    await redis_service.delete(cart_key)
    
    return {"message": "Cart cleared"}


@router.post("/checkout")
async def checkout(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
    delivery_address: str = None,
    notes: Optional[str] = None,
) -> Any:
    """
    Convert cart to order. Payment: Cash on Delivery.
    """
    from app.models.order import Order, OrderStatus
    
    cart_key = get_cart_key(current_user.id)
    cart_data = await redis_service.get(cart_key)
    
    if not cart_data:
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    cart = json.loads(cart_data)
    
    if not cart['items']:
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    # Calculate total
    subtotal = sum(item['price'] * item['quantity'] for item in cart['items'])
    delivery_fee = 2.0
    total = subtotal + delivery_fee
    
    # Create order
    order = Order(
        restaurant_id=cart['restaurant_id'],
        customer_phone=current_user.phone_number,
        customer_name=current_user.full_name,
        delivery_address=delivery_address or current_user.address or "Not specified",
        total_amount=total,
        status=OrderStatus.PENDING,
        items=cart['items'],
    )
    
    db.add(order)
    await db.commit()
    await db.refresh(order)
    
    # Clear cart
    await redis_service.delete(cart_key)
    
    return {
        "message": "Order placed successfully",
        "order_id": order.id,
        "total": total,
        "payment_method": "cash_on_delivery",
        "status": "pending",
    }
