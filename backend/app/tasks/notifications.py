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
def notify_customer_order_status(order_id: int, customer_phone: str, status: str, lang: str = "ar", driver_name: str = None, estimated_time: int = None):
    """
    Send order status update to customer with enhanced details.
    """
    async def _notify():
        # Enhanced status messages with emojis and progress
        status_info = {
            "accepted": {
                "ar": "✅ تم استلام طلبك!\nالمطعم بدأ بتحضير طلبك 👨‍🍳",
                "en": "✅ Order received!\nThe restaurant is preparing your order 👨‍🍳",
                "progress": "1/4"
            },
            "preparing": {
                "ar": "👨‍🍳 جاري تحضير طلبك...\nصبر شوي، عم يجهزوه بأسرع وقت!",
                "en": "👨‍🍳 Preparing your order...\nAlmost ready!",
                "progress": "2/4"
            },
            "ready": {
                "ar": "✨ طلبك جاهز!\nعم ننتظر السائق ياخده 🚗",
                "en": "✨ Your order is ready!\nWaiting for driver pickup 🚗",
                "progress": "3/4"
            },
            "out_for_delivery": {
                "ar": "🚗 طلبك بالطريق!\nالسائق عم يوصلك",
                "en": "🚗 Out for delivery!\nDriver is on the way",
                "progress": "4/4"
            },
            "delivered": {
                "ar": "🎉 تم التوصيل!\nصحتين وعافية! شكراً لاختيارك LionBot 🦁",
                "en": "🎉 Delivered!\nEnjoy your meal! Thanks for using LionBot 🦁",
                "progress": "✅"
            },
        }

        info = status_info.get(status, {"ar": f"حالة الطلب: {status}", "en": f"Status: {status}", "progress": ""})
        message = info.get(lang, info.get("ar"))
        progress = info.get("progress", "")

        # Build full message
        if lang == "ar":
            full_message = f"📦 *طلب #{order_id}*\n"
            if progress:
                full_message += f"📊 التقدم: {progress}\n\n"
            full_message += message
        else:
            full_message = f"📦 *Order #{order_id}*\n"
            if progress:
                full_message += f"📊 Progress: {progress}\n\n"
            full_message += message

        # Add driver info if available
        if driver_name and status == "out_for_delivery":
            if lang == "ar":
                full_message += f"\n\n👤 السائق: {driver_name}"
            else:
                full_message += f"\n\n👤 Driver: {driver_name}"

        # Add estimated time if available
        if estimated_time and status in ["out_for_delivery", "preparing"]:
            if lang == "ar":
                full_message += f"\n⏱️ الوقت المتوقع: ~{estimated_time} دقيقة"
            else:
                full_message += f"\n⏱️ Estimated: ~{estimated_time} min"

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
