import httpx
from app.core.config import settings
from app.core.exceptions import WhatsAppAPIError
import logging
import json
import asyncio
from typing import Optional

logger = logging.getLogger(__name__)

# Retry configuration
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 1

class WhatsAppService:
    def __init__(self):
        self.api_token = settings.WHATSAPP_API_TOKEN
        self.phone_number_id = settings.WHATSAPP_PHONE_NUMBER_ID
        self.base_url = f"https://graph.facebook.com/v18.0/{self.phone_number_id}/messages"
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }
        self._client: Optional[httpx.AsyncClient] = None

    def _get_client(self) -> httpx.AsyncClient:
        """Get or create singleton httpx client"""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client

    async def close(self):
        """Close the httpx client"""
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    async def send_message(self, to: str, message_data: dict, retry_count: int = 0):
        """
        Send message with retry logic for transient failures.

        Args:
            to: Recipient phone number
            message_data: Message payload
            retry_count: Current retry attempt (internal use)

        Returns:
            API response dict or None on failure

        Raises:
            WhatsAppAPIError: On permanent failures after all retries
        """
        if not self.api_token:
            logger.warning("WhatsApp API Token not set. Skipping message send.")
            return None

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            **message_data
        }

        try:
            client = self._get_client()
            logger.debug(f"Sending WhatsApp message to {to}...")
            response = await client.post(self.base_url, headers=self.headers, json=payload)
            logger.debug(f"WhatsApp API Response Status: {response.status_code}")
            if settings.DEBUG:
                logger.debug(f"WhatsApp API Response Body: {response.text}")
            response.raise_for_status()
            return response.json()
        except httpx.TimeoutException as e:
            # Retry on timeout
            if retry_count < MAX_RETRIES:
                logger.warning(f"WhatsApp timeout, retrying ({retry_count + 1}/{MAX_RETRIES})...")
                await asyncio.sleep(RETRY_DELAY_SECONDS * (retry_count + 1))
                return await self.send_message(to, message_data, retry_count + 1)
            logger.error(f"WhatsApp timeout after {MAX_RETRIES} retries: {e}")
            return None
        except httpx.HTTPStatusError as e:
            # Don't retry on 4xx errors (client errors)
            if 400 <= e.response.status_code < 500:
                error_msg = f"WhatsApp API client error: {e.response.status_code}"
                logger.error(f"{error_msg} - Response: {e.response.text}")
                return None
            # Retry on 5xx errors (server errors)
            if retry_count < MAX_RETRIES:
                logger.warning(f"WhatsApp server error, retrying ({retry_count + 1}/{MAX_RETRIES})...")
                await asyncio.sleep(RETRY_DELAY_SECONDS * (retry_count + 1))
                return await self.send_message(to, message_data, retry_count + 1)
            logger.error(f"WhatsApp server error after {MAX_RETRIES} retries: {e}")
            return None
        except httpx.HTTPError as e:
            logger.error(f"Failed to send WhatsApp message: {e}")
            if hasattr(e, 'response') and e.response:
                logger.error(f"Response: {e.response.text}")
            return None

    async def send_text(self, to: str, text: str):
        return await self.send_message(to, {
            "type": "text",
            "text": {"body": text}
        })

    async def send_interactive_buttons(self, to: str, body_text: str, buttons: list):
        """
        buttons: list of {"id": "unique_id", "title": "Button Title"}
        """
        return await self.send_message(to, {
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {"text": body_text},
                "action": {
                    "buttons": [
                        {
                            "type": "reply",
                            "reply": {"id": btn["id"], "title": btn["title"]}
                        } for btn in buttons
                    ]
                }
            }
        })

    async def send_interactive_list(self, to: str, body_text: str, button_text: str, sections: list):
        """
        sections: list of {"title": "Section Title", "rows": [{"id": "row_id", "title": "Row Title", "description": "Desc"}]}
        """
        return await self.send_message(to, {
            "type": "interactive",
            "interactive": {
                "type": "list",
                "body": {"text": body_text},
                "action": {
                    "button": button_text,
                    "sections": sections
                }
            }
        })

whatsapp_service = WhatsAppService()
