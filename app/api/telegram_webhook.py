"""
Telegram webhook endpoints (Bot API updates).

Public path prefix: /webhook/telegram
"""
import json
import logging
from json import JSONDecodeError
from typing import Any, Dict

import hmac
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.api.deps import get_db_session
from app.config import settings
from app.services.message_router import message_router

logger = logging.getLogger(__name__)

LOG_PREFIX = "/webhook/telegram"
TELEGRAM_SECRET_HEADER = "X-Telegram-Bot-Api-Secret-Token"

router = APIRouter()


def _telegram_webhook_secret_matches(request: Request) -> bool:
    """
    Validate Telegram webhook secret when TELEGRAM_WEBHOOK_SECRET is configured.

    Uses constant-time comparison. If no secret is configured, accepts any request
    (development only — set TELEGRAM_WEBHOOK_SECRET in production).
    """
    expected = settings.TELEGRAM_WEBHOOK_SECRET
    if not expected:
        return True
    got = request.headers.get(TELEGRAM_SECRET_HEADER) or ""
    if len(got) != len(expected):
        return False
    return hmac.compare_digest(
        got.encode("utf-8"),
        expected.encode("utf-8"),
    )


@router.get("")
async def webhook_get() -> Dict[str, str]:
    """Health / URL existence check (Telegram does not use GET verify)."""
    logger.info("%s GET health", LOG_PREFIX)
    return {"status": "ok"}


@router.post("")
async def receive_webhook(
    request: Request, db: Session = Depends(get_db_session)
) -> Dict[str, str]:
    """Receive Telegram Update (POST)."""
    logger.info("%s POST received", LOG_PREFIX)

    if not _telegram_webhook_secret_matches(request):
        logger.warning("%s rejected: invalid webhook secret header", LOG_PREFIX)
        raise HTTPException(status_code=403, detail="Forbidden")

    try:
        raw = await request.body()
        if not raw:
            logger.info("%s empty body, ignoring", LOG_PREFIX)
            return {"status": "ok", "message": "ignored"}
        try:
            body: Dict[str, Any] = json.loads(raw.decode("utf-8"))
        except (JSONDecodeError, UnicodeDecodeError) as e:
            logger.warning("%s invalid JSON body: %s", LOG_PREFIX, e)
            return {"status": "ok", "message": "ignored"}

        logger.info("%s body keys=%s", LOG_PREFIX, list(body.keys()))

        message = body.get("message")
        if not message:
            logger.info("%s no 'message' in update, ignoring", LOG_PREFIX)
            return {"status": "ok"}
        if "text" not in message:
            logger.info("%s message has no 'text', ignoring", LOG_PREFIX)
            return {"status": "ok"}

        chat = message.get("chat", {})
        chat_id = chat.get("id")
        message_text = message.get("text", "")
        message_id = message.get("message_id")
        from_user = message.get("from") or {}
        username = from_user.get("username")

        if not chat_id or not message_id:
            logger.warning("%s missing chat_id or message_id, ignoring", LOG_PREFIX)
            return {"status": "ok"}

        preview = message_text[:80] + "..." if len(message_text) > 80 else message_text
        logger.info(
            "%s routing chat_id=%s message_id=%s text=%r",
            LOG_PREFIX,
            chat_id,
            message_id,
            preview,
        )
        await message_router.route_message_telegram(
            str(chat_id),
            message_text,
            str(message_id),
            db,
            username=username,
        )
        return {"status": "ok"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error("%s Error processing webhook: %s", LOG_PREFIX, e, exc_info=True)
        return {"status": "error", "message": "Internal server error"}
