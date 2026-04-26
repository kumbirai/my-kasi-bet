"""
WhatsApp webhook endpoints (Meta Cloud API).

Public path prefix: /webhook/whatsapp
"""
import logging
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session

from app.api.deps import get_db_session
from app.config import settings
from app.services.message_router import message_router

logger = logging.getLogger(__name__)

LOG_PREFIX = "/webhook/whatsapp"

router = APIRouter()


@router.get("")
async def verify_webhook(request: Request) -> Response:
    """
    Verify webhook for WhatsApp Business API (Meta GET challenge).
    """
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == settings.WHATSAPP_VERIFY_TOKEN:
        logger.info("%s Webhook verified successfully", LOG_PREFIX)
        return Response(content=challenge, media_type="text/plain")
    logger.warning(
        "%s Webhook verification failed: mode=%s token_match=%s",
        LOG_PREFIX,
        mode,
        token == settings.WHATSAPP_VERIFY_TOKEN,
    )
    raise HTTPException(status_code=403, detail="Verification failed")


@router.post("")
async def receive_webhook(
    request: Request, db: Session = Depends(get_db_session)
) -> Dict[str, str]:
    """
    Receive incoming WhatsApp messages (POST).
    """
    try:
        body: Dict[str, Any] = await request.json()
        logger.info("%s Webhook received object=%s", LOG_PREFIX, body.get("object", "unknown"))

        if body.get("object") == "whatsapp_business_account":
            for entry in body.get("entry", []):
                for change in entry.get("changes", []):
                    value = change.get("value", {})
                    messages = value.get("messages", [])

                    for message in messages:
                        if message.get("type") == "text":
                            from_number = message.get("from")
                            message_text = message.get("text", {}).get("body", "")
                            message_id = message.get("id")

                            if from_number and message_text and message_id:
                                await message_router.route_message(
                                    from_number,
                                    message_text,
                                    message_id,
                                    db,
                                )

        return {"status": "ok"}

    except Exception as e:
        logger.error("%s Error processing webhook: %s", LOG_PREFIX, e, exc_info=True)
        return {"status": "error", "message": "Internal server error"}
