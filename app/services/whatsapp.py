"""
WhatsApp Business API service.

This module provides functionality to interact with the WhatsApp Business API
for sending messages and managing message status.
"""
import logging
from typing import Any, Dict, Optional

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class WhatsAppService:
    """
    Service for interacting with WhatsApp Business API.

    This service handles all communication with the WhatsApp Business API
    including sending messages, marking messages as read, and handling errors.
    """

    def __init__(self) -> None:
        """
        Initialize WhatsApp service with API credentials.

        Loads configuration from settings and sets up HTTP headers.
        """
        self.api_url = settings.WHATSAPP_API_URL
        self.phone_number_id = settings.WHATSAPP_PHONE_NUMBER_ID
        self.access_token = settings.WHATSAPP_ACCESS_TOKEN
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

    async def send_message(
        self,
        to: str,
        message: str,
        reply_to_message_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Send text message via WhatsApp Business API.

        Args:
            to: Recipient phone number (with country code, no +)
            message: Text message to send
            reply_to_message_id: Optional message ID to reply to

        Returns:
            API response dictionary containing message ID and status

        Raises:
            httpx.HTTPStatusError: If API request fails with HTTP error
            httpx.RequestError: If request fails due to network/connection issues
        """
        url = f"{self.api_url}/{self.phone_number_id}/messages"

        payload: Dict[str, Any] = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": message,
            },
        }

        if reply_to_message_id:
            payload["context"] = {"message_id": reply_to_message_id}

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    url,
                    headers=self.headers,
                    json=payload,
                )
                response.raise_for_status()
                result = response.json()
                message_id = result.get("messages", [{}])[0].get("id", "unknown")
                logger.info(
                    f"Message sent successfully to {to}, message_id: {message_id}"
                )
                return result
        except httpx.HTTPStatusError as e:
            logger.error(
                f"HTTP error sending message to {to}: "
                f"{e.response.status_code} - {e.response.text}"
            )
            raise
        except httpx.RequestError as e:
            logger.error(f"Request error sending message to {to}: {e}")
            raise

    async def mark_as_read(self, message_id: str) -> Dict[str, Any]:
        """
        Mark message as read.

        This is a non-critical operation. If it fails, we log a warning
        but don't raise an exception to avoid disrupting message processing.

        Args:
            message_id: WhatsApp message ID to mark as read

        Returns:
            API response dictionary (empty dict if operation fails)
        """
        url = f"{self.api_url}/{self.phone_number_id}/messages"

        payload = {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message_id,
        }

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(
                    url,
                    headers=self.headers,
                    json=payload,
                )
                response.raise_for_status()
                result = response.json()
                logger.debug(f"Message {message_id} marked as read")
                return result
        except Exception as e:
            logger.warning(
                f"Error marking message {message_id} as read: {e}. "
                "Continuing without failing."
            )
            return {}


# Singleton instance
whatsapp_service = WhatsAppService()
