"""
WhatsApp webhook endpoints.

This module handles webhook requests from WhatsApp Business API
for message verification and receiving messages.
"""
import logging
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session

from app.api.deps import get_db_session
from app.config import settings
from app.services.message_router import message_router

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/webhook")
async def verify_webhook(request: Request) -> Response:
    """
    Verify webhook endpoint for WhatsApp Business API.

    WhatsApp will make a GET request with:
    - hub.mode = "subscribe"
    - hub.verify_token = your verification token
    - hub.challenge = challenge string to echo back

    Args:
        request: FastAPI request object

    Returns:
        Response: Challenge string if verification succeeds

    Raises:
        HTTPException: 403 if verification fails
    """
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == settings.WHATSAPP_VERIFY_TOKEN:
        logger.info("Webhook verified successfully")
        return Response(content=challenge, media_type="text/plain")
    else:
        logger.warning(
            f"Webhook verification failed: mode={mode}, "
            f"token_match={token == settings.WHATSAPP_VERIFY_TOKEN}"
        )
        raise HTTPException(status_code=403, detail="Verification failed")


@router.post("/webhook")
async def receive_webhook(
    request: Request, db: Session = Depends(get_db_session)
) -> Dict[str, str]:
    """
    Receive incoming WhatsApp messages.

    This endpoint processes incoming webhook payloads from WhatsApp Business API.
    It extracts message data and routes it to the message router for processing.

    Payload structure:
    {
        "object": "whatsapp_business_account",
        "entry": [{
            "id": "WHATSAPP_BUSINESS_ACCOUNT_ID",
            "changes": [{
                "value": {
                    "messaging_product": "whatsapp",
                    "metadata": {...},
                    "messages": [{
                        "from": "27821234567",
                        "id": "wamid.XXX",
                        "timestamp": "1234567890",
                        "type": "text",
                        "text": {
                            "body": "Hello"
                        }
                    }]
                },
                "field": "messages"
            }]
        }]
    }

    Args:
        request: FastAPI request object
        db: Database session dependency

    Returns:
        dict: Status response (always returns 200 to prevent WhatsApp retries)
    """
    try:
        body: Dict[str, Any] = await request.json()

        # Log incoming webhook for debugging
        logger.info(f"Webhook received: {body.get('object', 'unknown')}")

        # Extract message data
        if body.get("object") == "whatsapp_business_account":
            for entry in body.get("entry", []):
                for change in entry.get("changes", []):
                    value = change.get("value", {})

                    # Check if there are messages
                    messages = value.get("messages", [])

                    for message in messages:
                        # Only process text messages for now
                        if message.get("type") == "text":
                            from_number = message.get("from")
                            message_text = message.get("text", {}).get("body", "")
                            message_id = message.get("id")

                            if from_number and message_text and message_id:
                                # Route message to handler
                                await message_router.route_message(
                                    from_number,
                                    message_text,
                                    message_id,
                                    db,
                                )

        return {"status": "ok"}

    except Exception as e:
        logger.error(f"Error processing webhook: {e}", exc_info=True)
        # Always return 200 to WhatsApp so they don't retry
        # This prevents duplicate message processing
        return {"status": "error", "message": "Internal server error"}
