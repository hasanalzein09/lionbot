from fastapi import APIRouter, Request, HTTPException, Query
from app.core.config import settings
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/webhook")
async def verify_webhook(
    mode: str = Query(..., alias="hub.mode"),
    token: str = Query(..., alias="hub.verify_token"),
    challenge: str = Query(..., alias="hub.challenge"),
):
    """
    Webhook verification endpoint for WhatsApp.
    """
    if mode and token:
        if mode == "subscribe" and token == settings.WHATSAPP_VERIFY_TOKEN:
            logger.info("Webhook verified successfully!")
            return int(challenge)
        else:
            raise HTTPException(status_code=403, detail="Verification failed")
    raise HTTPException(status_code=400, detail="Missing parameters")

from app.controllers.bot_controller import bot_controller

@router.post("/webhook")
async def handle_webhook(request: Request):
    """
    Handle incoming messages from WhatsApp.
    """
    try:
        body = await request.json()
        print(f"DEBUG WEBHOOK BODY: {body}", flush=True)
        logger.info(f"Received webhook: {body}")
        
        entries = body.get("entry", [])
        if not entries:
            return {"status": "received", "detail": "no entries"}
            
        entry = entries[0]
        changes = entry.get("changes", [])
        if not changes:
            return {"status": "received", "detail": "no changes"}
            
        change = changes[0]
        value = change.get("value", {})
        messages = value.get("messages", [])
        
        if messages:
            message = messages[0]
            if message:
                phone_number = message.get("from")
                # Process message asynchronously
                await bot_controller.handle_message(phone_number, message)
        
        return {"status": "received"}
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return {"status": "error", "message": str(e)}
