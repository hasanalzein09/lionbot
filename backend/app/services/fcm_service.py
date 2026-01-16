"""
Firebase Cloud Messaging Service for sending push notifications.
Uses HTTP v1 API with Service Account authentication.
"""
import httpx
import json
import os
import logging
from typing import List, Optional, Dict, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User

logger = logging.getLogger(__name__)

# Try to import google.auth for OAuth token generation
try:
    from google.oauth2 import service_account
    from google.auth.transport.requests import Request
    GOOGLE_AUTH_AVAILABLE = True
except ImportError:
    GOOGLE_AUTH_AVAILABLE = False
    logger.warning("google-auth not installed. FCM notifications will be disabled.")


class FCMService:
    """Service for sending Firebase Cloud Messaging push notifications."""

    # FCM HTTP v1 API endpoint
    FCM_V1_URL = "https://fcm.googleapis.com/v1/projects/{project_id}/messages:send"
    FCM_SCOPES = ["https://www.googleapis.com/auth/firebase.messaging"]

    def __init__(self):
        self._client: Optional[httpx.AsyncClient] = None
        self._credentials = None
        self._project_id: Optional[str] = None
        self._initialized = False
        self._init_credentials()

    def _init_credentials(self):
        """Initialize service account credentials."""
        if not GOOGLE_AUTH_AVAILABLE:
            return

        # Look for service account file
        sa_paths = [
            os.path.join(os.path.dirname(__file__), "../../firebase-service-account.json"),
            "/app/firebase-service-account.json",
            "firebase-service-account.json",
        ]

        for path in sa_paths:
            if os.path.exists(path):
                try:
                    self._credentials = service_account.Credentials.from_service_account_file(
                        path, scopes=self.FCM_SCOPES
                    )
                    with open(path) as f:
                        sa_data = json.load(f)
                        self._project_id = sa_data.get("project_id")
                    self._initialized = True
                    logger.info(f"FCM Service initialized with project: {self._project_id}")
                    return
                except Exception as e:
                    logger.warning(f"Failed to load service account from {path}: {e}")

        logger.warning("FCM Service: No service account found. Push notifications disabled.")

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client

    def _get_access_token(self) -> Optional[str]:
        """Get OAuth2 access token for FCM API."""
        if not self._initialized or not self._credentials:
            return None

        # Refresh token if expired
        if not self._credentials.valid:
            self._credentials.refresh(Request())

        return self._credentials.token

    async def send_to_token(
        self,
        token: str,
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None,
        image_url: Optional[str] = None,
    ) -> bool:
        """Send notification to a specific device token."""
        if not self._initialized:
            logger.debug("FCM not initialized, skipping notification")
            return False

        try:
            access_token = self._get_access_token()
            if not access_token:
                return False

            url = self.FCM_V1_URL.format(project_id=self._project_id)

            message = {
                "message": {
                    "token": token,
                    "notification": {
                        "title": title,
                        "body": body,
                    },
                    "data": {k: str(v) for k, v in (data or {}).items()},
                    "android": {
                        "priority": "high",
                        "notification": {
                            "sound": "default",
                            "channel_id": "orders_channel",
                        }
                    },
                    "apns": {
                        "payload": {
                            "aps": {
                                "sound": "default",
                                "badge": 1,
                            }
                        }
                    }
                }
            }

            if image_url:
                message["message"]["notification"]["image"] = image_url

            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            }

            response = await self.client.post(url, json=message, headers=headers)

            if response.status_code == 200:
                logger.debug(f"FCM sent to token: {token[:20]}...")
                return True
            else:
                logger.error(f"FCM error: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            logger.error(f"FCM Error: {e}")
            return False

    async def send_to_topic(
        self,
        topic: str,
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Send notification to all subscribers of a topic."""
        if not self._initialized:
            logger.debug("FCM not initialized, skipping topic notification")
            return False

        try:
            access_token = self._get_access_token()
            if not access_token:
                return False

            url = self.FCM_V1_URL.format(project_id=self._project_id)

            message = {
                "message": {
                    "topic": topic,
                    "notification": {
                        "title": title,
                        "body": body,
                    },
                    "data": {k: str(v) for k, v in (data or {}).items()},
                    "android": {
                        "priority": "high",
                        "notification": {
                            "sound": "default",
                            "channel_id": "orders_channel",
                        }
                    },
                    "apns": {
                        "payload": {
                            "aps": {
                                "sound": "default",
                                "badge": 1,
                            }
                        }
                    }
                }
            }

            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            }

            response = await self.client.post(url, json=message, headers=headers)

            if response.status_code == 200:
                logger.debug(f"FCM sent to topic: {topic}")
                return True
            else:
                logger.error(f"FCM topic error: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            logger.error(f"FCM Topic Error: {e}")
            return False

    async def send_to_multiple_tokens(
        self,
        tokens: List[str],
        title: str,
        body: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> int:
        """Send notification to multiple device tokens. Returns success count."""
        if not tokens or not self._initialized:
            return 0

        success_count = 0
        for token in tokens[:500]:  # FCM limit
            if await self.send_to_token(token, title, body, data):
                success_count += 1

        return success_count

    # ==================== Business Logic Methods ====================

    async def notify_driver_new_order(
        self,
        db: AsyncSession,
        driver_id: int,
        order_id: int,
        restaurant_name: str,
        delivery_address: str,
    ) -> bool:
        """Notify a driver about a new order assignment."""
        result = await db.execute(
            select(User).where(User.id == driver_id)
        )
        driver = result.scalars().first()

        if not driver or not driver.fcm_token:
            return False

        return await self.send_to_token(
            token=driver.fcm_token,
            title="🚚 New Delivery Assignment!",
            body=f"Pickup from {restaurant_name} to {delivery_address}",
            data={
                "type": "new_order",
                "order_id": str(order_id),
                "click_action": "FLUTTER_NOTIFICATION_CLICK",
            },
        )

    async def notify_restaurant_new_order(
        self,
        db: AsyncSession,
        restaurant_id: int,
        order_id: int,
        customer_name: str,
        total_amount: float,
    ) -> bool:
        """Notify restaurant about a new incoming order."""
        return await self.send_to_topic(
            topic=f"restaurant_{restaurant_id}",
            title="🛒 New Order Received!",
            body=f"Order #{order_id} from {customer_name} - ${total_amount:.2f}",
            data={
                "type": "new_order",
                "order_id": str(order_id),
                "restaurant_id": str(restaurant_id),
            },
        )

    async def notify_customer_order_update(
        self,
        db: AsyncSession,
        user_id: int,
        order_id: int,
        status: str,
    ) -> bool:
        """Notify customer about order status update."""
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalars().first()

        if not user or not user.fcm_token:
            return False

        status_messages = {
            "accepted": "Your order has been accepted! 🎉",
            "preparing": "Your order is being prepared 👨‍🍳",
            "ready": "Your order is ready for pickup 📦",
            "out_for_delivery": "Your order is on its way! 🚚",
            "delivered": "Your order has been delivered! Enjoy! 🎊",
        }

        return await self.send_to_token(
            token=user.fcm_token,
            title=f"Order #{order_id} Update",
            body=status_messages.get(status, f"Status: {status}"),
            data={
                "type": "order_update",
                "order_id": str(order_id),
                "status": status,
            },
        )

    async def notify_admins_new_order(
        self,
        order_id: int,
        restaurant_name: str,
        total_amount: float,
        restaurant_id: int,
    ) -> bool:
        """Send new order notification to all admin app users."""
        return await self.send_to_topic(
            topic="admin_orders",
            title="🛒 طلب جديد!",
            body=f"طلب #{order_id} من {restaurant_name} - ${total_amount:.2f}",
            data={
                "type": "new_order",
                "order_id": str(order_id),
                "restaurant_id": str(restaurant_id),
                "restaurant_name": restaurant_name,
                "total": str(total_amount),
            },
        )

    async def notify_admins_alert(
        self,
        title: str,
        message: str,
        alert_type: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Send alert to all admin users via topic."""
        return await self.send_to_topic(
            topic="admin_alerts",
            title=title,
            body=message,
            data={
                "type": alert_type,
                **(data or {}),
            },
        )

    async def close(self):
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None


# Singleton instance
fcm_service = FCMService()
