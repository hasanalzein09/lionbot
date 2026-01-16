"""
Order Processing Tasks - Background tasks for order management
"""
from celery import shared_task
from app.db.session import AsyncSessionLocal
from app.models.order import Order, OrderStatus
from app.models.user import User, UserRole
from app.services.redis_service import redis_service
from sqlalchemy import select, and_
from datetime import datetime, timedelta
import asyncio
import logging

logger = logging.getLogger(__name__)


def run_async(coro):
    """Helper to run async code in sync context"""
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(coro)


@shared_task(name="app.tasks.order_processing.auto_assign_driver")
def auto_assign_driver(order_id: int, restaurant_lat: float, restaurant_lng: float):
    """
    Automatically assign the nearest available driver to an order.
    """
    async def _assign():
        async with AsyncSessionLocal() as db:
            # Get available drivers (simplified - in production would use location)
            result = await db.execute(
                select(User)
                .where(User.role == UserRole.DRIVER)
                .where(User.is_active == True)
                .limit(1)
            )
            driver = result.scalars().first()
            
            if not driver:
                logger.warning(f"No available drivers for order {order_id}")
                return {"success": False, "reason": "no_drivers_available"}
            
            # Assign driver to order
            order_result = await db.execute(
                select(Order).where(Order.id == order_id)
            )
            order = order_result.scalars().first()
            
            if not order:
                return {"success": False, "reason": "order_not_found"}
            
            order.driver_id = driver.id
            order.status = OrderStatus.OUT_FOR_DELIVERY
            db.add(order)
            await db.commit()
            
            # Notify driver
            await redis_service.publish_driver_notification(driver.id, {
                "type": "new_delivery",
                "order_id": order_id
            })
            
            logger.info(f"Assigned driver {driver.id} to order {order_id}")
            return {"success": True, "driver_id": driver.id}
    
    try:
        return run_async(_assign())
    except Exception as e:
        logger.error(f"Failed to auto-assign driver: {e}")
        return {"success": False, "error": str(e)}


@shared_task(name="app.tasks.order_processing.check_stuck_orders")
def check_stuck_orders():
    """
    Check for orders that have been in 'NEW' status for too long
    and send reminders to restaurants.
    """
    async def _check():
        async with AsyncSessionLocal() as db:
            # Find orders in NEW status for more than 10 minutes
            threshold = datetime.utcnow() - timedelta(minutes=10)
            
            result = await db.execute(
                select(Order)
                .where(Order.status == OrderStatus.NEW)
                .where(Order.created_at < threshold)
            )
            stuck_orders = result.scalars().all()
            
            for order in stuck_orders:
                logger.warning(f"Order {order.id} has been pending for too long")
                # Publish notification for restaurant
                await redis_service.publish_restaurant_notification(
                    order.restaurant_id,
                    {
                        "type": "order_reminder",
                        "order_id": order.id,
                        "message": "This order has been waiting for a response!"
                    }
                )
            
            return {"checked": len(stuck_orders)}
    
    try:
        return run_async(_check())
    except Exception as e:
        logger.error(f"Failed to check stuck orders: {e}")
        return {"success": False, "error": str(e)}


@shared_task(name="app.tasks.order_processing.process_order_completion")
def process_order_completion(order_id: int):
    """
    Process order completion - calculate commission, driver payout, etc.
    """
    async def _process():
        from app.core.pricing import calculate_commission, calculate_driver_payout
        
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(Order).where(Order.id == order_id)
            )
            order = result.scalars().first()
            
            if not order:
                return {"success": False, "reason": "order_not_found"}
            
            # Calculate financials
            commission = calculate_commission(order.total_amount)
            driver_payout = calculate_driver_payout(order.delivery_fee)
            
            # In production, would save these to a transactions table
            logger.info(f"Order {order_id} completed. Commission: ${commission}, Driver payout: ${driver_payout}")
            
            return {
                "success": True,
                "order_id": order_id,
                "commission": commission,
                "driver_payout": driver_payout
            }
    
    try:
        return run_async(_process())
    except Exception as e:
        logger.error(f"Failed to process order completion: {e}")
        return {"success": False, "error": str(e)}
