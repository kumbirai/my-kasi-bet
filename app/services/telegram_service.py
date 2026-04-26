"""
Telegram Bot API service.

This module provides functionality to interact with the Telegram Bot API
for sending messages.
"""
import logging
from typing import Any, Dict, Optional, Union

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class TelegramChatNotFoundError(Exception):
    """Raised when Telegram API returns 400 'chat not found'."""


class TelegramService:
    """
    Service for interacting with the Telegram Bot API.

    Handles sending text messages via the Telegram Bot API.
    """

    def __init__(self) -> None:
        self.bot_token = settings.TELEGRAM_BOT_TOKEN
        self.base_url = "https://api.telegram.org"

    def _url(self, method: str) -> str:
        """Build Telegram Bot API URL for the given method."""
        return f"{self.base_url}/bot{self.bot_token}/{method}"

    async def send_message(
        self,
        chat_id: Union[str, int],
        message: str,
        reply_to_message_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Send text message via Telegram Bot API.

        Args:
            chat_id: Telegram chat ID (user or group)
            message: Text message to send
            reply_to_message_id: Optional message ID to reply to

        Returns:
            API response dictionary containing the sent message

        Raises:
            ValueError: If bot token is not configured
            httpx.HTTPStatusError: If API request fails with HTTP error
            httpx.RequestError: If request fails due to network issues
        """
        if not self.bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN is not configured")

        payload: Dict[str, Any] = {
            "chat_id": chat_id,
            "text": message,
        }
        if reply_to_message_id is not None:
            payload["reply_to_message_id"] = reply_to_message_id

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    self._url("sendMessage"),
                    json=payload,
                )
                response.raise_for_status()
                result = response.json()
                if not result.get("ok"):
                    logger.error("Telegram API error: %s", result)
                    raise httpx.HTTPStatusError(
                        "Telegram API returned ok=false",
                        request=response.request,
                        response=response,
                    )
                mid = result.get("result", {}).get("message_id", "unknown")
                logger.info(
                    "Message sent successfully to chat %s, message_id: %s",
                    chat_id,
                    mid,
                )
                return result
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 400 and "chat not found" in (
                e.response.text or ""
            ).lower():
                logger.warning(
                    "Telegram chat not found (chat_id=%s); skipping send",
                    chat_id,
                )
                raise TelegramChatNotFoundError(
                    f"Chat not found: {chat_id}"
                ) from e
            logger.error(
                "HTTP error sending message to %s: %s - %s",
                chat_id,
                e.response.status_code,
                e.response.text,
            )
            raise
        except httpx.RequestError as e:
            logger.error("Request error sending message to %s: %s", chat_id, e)
            raise


telegram_service = TelegramService()
