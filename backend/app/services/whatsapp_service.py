import httpx
from app.core.config import settings
import logging
import json

logger = logging.getLogger(__name__)

class WhatsAppService:
    def __init__(self):
        self.api_token = settings.WHATSAPP_API_TOKEN
        self.phone_number_id = settings.WHATSAPP_PHONE_NUMBER_ID
        self.base_url = f"https://graph.facebook.com/v18.0/{self.phone_number_id}/messages"
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }

    async def send_message(self, to: str, message_data: dict):
        if not self.api_token:
            logger.warning("WhatsApp API Token not set. Skipping message send.")
            return

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            **message_data
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(self.base_url, headers=self.headers, json=payload)
                response.raise_for_status()
                logger.info(f"Message sent to {to}: {response.json()}")
                return response.json()
            except httpx.HTTPError as e:
                logger.error(f"Failed to send WhatsApp message: {e}")
                if hasattr(e, 'response'):
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
