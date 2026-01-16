import hmac
import hashlib
from fastapi import APIRouter, Request, HTTPException, Query, Header
from fastapi.responses import PlainTextResponse
from app.core.config import settings
from app.core.limiter import limiter
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

def verify_signature(payload: bytes, signature: str) -> bool:
    """Verify that the payload was sent from WhatsApp by checking the signature"""
    if not settings.WHATSAPP_APP_SECRET:
        logger.warning("WHATSAPP_APP_SECRET not set. Skipping signature verification.")
        return True
    
    if not signature:
        return False
    
    # Signature is in format 'sha256=xxx'
    if signature.startswith('sha256='):
        signature = signature.replace('sha256=', '')
    
    expected_signature = hmac.new(
        settings.WHATSAPP_APP_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(expected_signature, signature)

@router.get("/webhook")
async def verify_webhook(
    mode: str = Query(None, alias="hub.mode"),
    token: str = Query(None, alias="hub.verify_token"),
    challenge: str = Query(None, alias="hub.challenge"),
):
    """
    Webhook verification endpoint for WhatsApp.
    """
    logger.info(f"Webhook verification: mode={mode}, token={token}, challenge={challenge}")
    
    if mode and token and challenge:
        if mode == "subscribe" and token == settings.WHATSAPP_VERIFY_TOKEN:
            logger.info("Webhook verified successfully!")
            return PlainTextResponse(content=challenge, status_code=200)
        else:
            logger.warning(f"Verification failed: mode={mode}, token mismatch")
            raise HTTPException(status_code=403, detail="Verification failed")
    
    raise HTTPException(status_code=400, detail="Missing parameters")

from app.controllers.bot_controller import bot_controller

@router.post("/webhook")
@limiter.limit("100/minute")
async def handle_webhook(
    request: Request,
    x_hub_signature_256: str = Header(None)
):
    """
    Handle incoming messages from WhatsApp.
    """
    # 🛡️ Rate limiting (if limiter is setup in main)
    # The limiter decorator needs the request object to be the first positional arg or passed via request
    body_bytes = await request.body()
    
    # 🛡️ Verify signature
    if not verify_signature(body_bytes, x_hub_signature_256):
        logger.error("Invalid webhook signature!")
        raise HTTPException(status_code=403, detail="Invalid signature")

    try:
        body = await request.json()
        if settings.DEBUG:
            logger.debug(f"Received webhook payload: {body}")
        
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
        logger.error(f"Error processing webhook: {e}", exc_info=True)
        # Don't expose internal error details to external clients
        return {"status": "error"}

