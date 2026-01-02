"""
Tests for WhatsApp service.

This module tests WhatsApp Business API service functionality.
"""
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from app.services.whatsapp import WhatsAppService


@pytest.fixture
def whatsapp_service_instance():
    """Create WhatsApp service instance with test credentials."""
    with patch("app.services.whatsapp.settings") as mock_settings:
        mock_settings.WHATSAPP_API_URL = "https://graph.facebook.com/v18.0"
        mock_settings.WHATSAPP_PHONE_NUMBER_ID = "test_phone_id"
        mock_settings.WHATSAPP_ACCESS_TOKEN = "test_token"
        service = WhatsAppService()
        return service


@pytest.mark.asyncio
async def test_send_message_success(whatsapp_service_instance):
    """Test successful message sending."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "messages": [{"id": "wamid.test123"}]
    }
    mock_response.raise_for_status = MagicMock()

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response

        result = await whatsapp_service_instance.send_message(
            "27821234567", "Test message"
        )

        assert result["messages"][0]["id"] == "wamid.test123"
        mock_post.assert_called_once()


@pytest.mark.asyncio
async def test_send_message_with_reply(whatsapp_service_instance):
    """Test sending message with reply."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"messages": [{"id": "wamid.test456"}]}
    mock_response.raise_for_status = MagicMock()

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response

        await whatsapp_service_instance.send_message(
            "27821234567", "Reply message", reply_to_message_id="wamid.original"
        )

        # Verify context was included in payload
        call_args = mock_post.call_args
        assert "context" in call_args[1]["json"]
        assert call_args[1]["json"]["context"]["message_id"] == "wamid.original"


@pytest.mark.asyncio
async def test_send_message_http_error(whatsapp_service_instance):
    """Test handling HTTP errors."""
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.text = "Bad Request"
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Bad Request", request=MagicMock(), response=mock_response
    )

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response

        with pytest.raises(httpx.HTTPStatusError):
            await whatsapp_service_instance.send_message(
                "27821234567", "Test message"
            )


@pytest.mark.asyncio
async def test_mark_as_read_success(whatsapp_service_instance):
    """Test successful mark as read."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"success": True}
    mock_response.raise_for_status = MagicMock()

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response

        result = await whatsapp_service_instance.mark_as_read("wamid.test123")

        assert result["success"] is True


@pytest.mark.asyncio
async def test_mark_as_read_failure_does_not_raise(whatsapp_service_instance):
    """Test that mark as read failure doesn't raise exception."""
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.side_effect = Exception("Network error")

        # Should not raise
        result = await whatsapp_service_instance.mark_as_read("wamid.test123")

        assert result == {}
