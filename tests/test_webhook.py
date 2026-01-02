"""
Tests for webhook endpoints.

This module tests WhatsApp webhook verification and message receiving.
"""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_webhook_verification_success(monkeypatch):
    """Test successful webhook verification."""
    from app.api import webhook
    
    # Patch the settings attribute in the webhook module
    monkeypatch.setattr(webhook.settings, "WHATSAPP_VERIFY_TOKEN", "test_token")

    response = client.get(
        "/webhook?hub.mode=subscribe&hub.verify_token=test_token&hub.challenge=test123"
    )

    assert response.status_code == 200
    assert response.text == "test123"


def test_webhook_verification_failure():
    """Test failed webhook verification."""
    with patch("app.config.settings") as mock_settings:
        mock_settings.WHATSAPP_VERIFY_TOKEN = "correct_token"

        response = client.get(
            "/webhook?hub.mode=subscribe&hub.verify_token=wrong_token&hub.challenge=test123"
        )

        assert response.status_code == 403


@pytest.mark.asyncio
async def test_receive_webhook_text_message(test_db):
    """Test receiving text message via webhook."""
    from app.api.deps import get_db_session
    from app.main import app
    
    # Override database dependency
    app.dependency_overrides[get_db_session] = lambda: test_db
    
    webhook_payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "test_entry",
                "changes": [
                    {
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "1234567890",
                                "phone_number_id": "test_phone_id",
                            },
                            "messages": [
                                {
                                    "from": "27821234567",
                                    "id": "wamid.test123",
                                    "timestamp": "1234567890",
                                    "type": "text",
                                    "text": {"body": "Hello"},
                                }
                            ],
                        },
                        "field": "messages",
                    }
                ],
            }
        ],
    }

    with patch("app.api.webhook.message_router") as mock_router:
        mock_router.route_message = AsyncMock()

        response = client.post("/webhook", json=webhook_payload)

        assert response.status_code == 200
        assert response.json()["status"] == "ok"
        mock_router.route_message.assert_called_once()
    
    # Clean up
    app.dependency_overrides.clear()


def test_receive_webhook_invalid_payload():
    """Test receiving invalid webhook payload."""
    invalid_payload = {"object": "invalid"}

    response = client.post("/webhook", json=invalid_payload)

    # Should still return 200 to prevent WhatsApp retries
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_receive_webhook_error_handling(test_db):
    """Test webhook error handling."""
    from app.api.deps import get_db_session
    from app.main import app
    
    # Override database dependency
    app.dependency_overrides[get_db_session] = lambda: test_db
    
    webhook_payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "test_entry",
                "changes": [
                    {
                        "value": {
                            "messaging_product": "whatsapp",
                            "messages": [
                                {
                                    "from": "27821234567",
                                    "id": "wamid.test123",
                                    "type": "text",
                                    "text": {"body": "Hello"},
                                }
                            ],
                        },
                        "field": "messages",
                    }
                ],
            }
        ],
    }

    with patch("app.api.webhook.message_router") as mock_router:
        mock_router.route_message = AsyncMock(side_effect=Exception("Test error"))

        response = client.post("/webhook", json=webhook_payload)

        # Should return 200 even on error to prevent retries
        assert response.status_code == 200
        assert response.json()["status"] == "error"
    
    # Clean up
    app.dependency_overrides.clear()
