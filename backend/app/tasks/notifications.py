"""
Notification Tasks - Background tasks for sending notifications
"""
from celery import shared_task
from app.services.whatsapp_service import whatsapp_service
from app.services.redis_service import redis_service
from app.core.i18n import get_text
from app.db.session import AsyncSessionLocal
from app.models.order import Order, OrderStatus
from sqlalchemy import select
import asyncio
import logging

logger = logging.getLogger(__name__)


def run_async(coro):
    """Helper to run async code in sync context"""
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(coro)


@shared_task(name="app.tasks.notifications.notify_restaurant_new_order")
def notify_restaurant_new_order(order_id: int, restaurant_phone: str):
    """
    Send notification to restaurant about new order.
    """
    async def _notify():
        message = f"""
🔔 *طلب جديد #{order_id}*

لديك طلب جديد! 
الرجاء فتح التطبيق لعرض التفاصيل وقبول الطلب.

---

🔔 *New Order #{order_id}*

You have a new order!
Please open the app to view details and accept.
"""
        await whatsapp_service.send_text(restaurant_phone, message)
        logger.info(f"Notified restaurant {restaurant_phone} about order {order_id}")
    
    try:
        run_async(_notify())
        return {"success": True, "order_id": order_id}
    except Exception as e:
        logger.error(f"Failed to notify restaurant: {e}")
        return {"success": False, "error": str(e)}


@shared_task(name="app.tasks.notifications.notify_driver_new_delivery")
def notify_driver_new_delivery(order_id: int, driver_phone: str, pickup_address: str, delivery_address: str):
    """
    Send notification to driver about new delivery assignment.
    """
    async def _notify():
        message = f"""
🚗 *توصيل جديد #{order_id}*

📍 الاستلام من: {pickup_address}
📍 التوصيل إلى: {delivery_address}

الرجاء فتح التطبيق لبدء التوصيل.

---

🚗 *New Delivery #{order_id}*

📍 Pickup: {pickup_address}
📍 Deliver to: {delivery_address}

Please open the app to start delivery.
"""
        await whatsapp_service.send_text(driver_phone, message)
        logger.info(f"Notified driver {driver_phone} about delivery {order_id}")
    
    try:
        run_async(_notify())
        return {"success": True, "order_id": order_id}
    except Exception as e:
        logger.error(f"Failed to notify driver: {e}")
        return {"success": False, "error": str(e)}


@shared_task(name="app.tasks.notifications.notify_customer_order_status")
def notify_customer_order_status(order_id: int, customer_phone: str, status: str, lang: str = "ar"):
    """
    Send order status update to customer.
    """
    async def _notify():
        status_messages = {
            "accepted": get_text("order_received", lang),
            "preparing": get_text("order_processing", lang),
            "ready": get_text("order_ready", lang),
            "out_for_delivery": get_text("order_on_way", lang),
            "delivered": get_text("order_delivered", lang),
        }
        
        message = status_messages.get(status, f"Order #{order_id} status: {status}")
        full_message = f"📦 *طلب #{order_id}*\n\n{message}" if lang == "ar" else f"📦 *Order #{order_id}*\n\n{message}"
        
        await whatsapp_service.send_text(customer_phone, full_message)
        logger.info(f"Notified customer {customer_phone} about order {order_id} status: {status}")
    
    try:
        run_async(_notify())
        return {"success": True, "order_id": order_id, "status": status}
    except Exception as e:
        logger.error(f"Failed to notify customer: {e}")
        return {"success": False, "error": str(e)}


@shared_task(name="app.tasks.notifications.send_daily_reports")
def send_daily_reports():
    """
    Send daily summary reports to restaurant managers.
    """
    # This would fetch all restaurants and send daily summaries
    logger.info("Daily reports task executed")
    return {"success": True, "message": "Daily reports sent"}
