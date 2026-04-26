"""
Tests for WhatsApp and Telegram webhook endpoints.
"""
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_whatsapp_webhook_verification_success(monkeypatch):
    """WhatsApp GET verify with correct token returns challenge."""
    from app.api import whatsapp_webhook

    monkeypatch.setattr(whatsapp_webhook.settings, "WHATSAPP_VERIFY_TOKEN", "test_token")

    response = client.get(
        "/webhook/whatsapp?hub.mode=subscribe&hub.verify_token=test_token&hub.challenge=test123"
    )

    assert response.status_code == 200
    assert response.text == "test123"


def test_whatsapp_webhook_verification_failure():
    """WhatsApp GET verify with wrong token returns 403."""
    with patch("app.api.whatsapp_webhook.settings") as mock_settings:
        mock_settings.WHATSAPP_VERIFY_TOKEN = "correct_token"

        response = client.get(
            "/webhook/whatsapp?hub.mode=subscribe&hub.verify_token=wrong_token&hub.challenge=test123"
        )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_whatsapp_receive_text_message(test_db):
    """WhatsApp POST with text invokes route_message with normalized flow."""
    from app.api.deps import get_db_session

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

    with patch("app.api.whatsapp_webhook.message_router") as mock_router:
        mock_router.route_message = AsyncMock()

        response = client.post("/webhook/whatsapp", json=webhook_payload)

        assert response.status_code == 200
        assert response.json()["status"] == "ok"
        mock_router.route_message.assert_called_once()

    app.dependency_overrides.clear()


def test_whatsapp_receive_non_waba_object():
    """Non-WABA POST still returns 200."""
    response = client.post("/webhook/whatsapp", json={"object": "invalid"})
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_telegram_get_health():
    """Telegram GET returns ok."""
    response = client.get("/webhook/telegram")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_telegram_receive_text_message(test_db):
    """Telegram POST with text calls route_message_telegram."""
    from app.api.deps import get_db_session

    app.dependency_overrides[get_db_session] = lambda: test_db

    body = {
        "update_id": 1,
        "message": {
            "message_id": 42,
            "chat": {"id": 999001},
            "text": "menu",
            "from": {"id": 999001, "username": "tester"},
        },
    }

    with patch("app.api.telegram_webhook.message_router") as mock_router:
        mock_router.route_message_telegram = AsyncMock()

        response = client.post("/webhook/telegram", json=body)

        assert response.status_code == 200
        assert response.json()["status"] == "ok"
        mock_router.route_message_telegram.assert_called_once()

    app.dependency_overrides.clear()


def test_telegram_post_rejects_wrong_secret_when_configured(monkeypatch):
    """POST returns 403 when TELEGRAM_WEBHOOK_SECRET is set and header mismatches."""
    from app.config import settings

    monkeypatch.setattr(settings, "TELEGRAM_WEBHOOK_SECRET", "correct-secret", raising=False)

    body = {"update_id": 1, "message": {"message_id": 1, "chat": {"id": 1}, "text": "hi"}}
    response = client.post(
        "/webhook/telegram",
        json=body,
        headers={"X-Telegram-Bot-Api-Secret-Token": "wrong-secret"},
    )
    assert response.status_code == 403


def test_telegram_post_accepts_matching_secret(monkeypatch, test_db):
    """POST succeeds when secret header matches configuration."""
    from app.api.deps import get_db_session
    from app.config import settings

    monkeypatch.setattr(settings, "TELEGRAM_WEBHOOK_SECRET", "my-shared-secret", raising=False)

    app.dependency_overrides[get_db_session] = lambda: test_db

    body = {
        "update_id": 1,
        "message": {
            "message_id": 42,
            "chat": {"id": 999001},
            "text": "menu",
            "from": {"id": 999001},
        },
    }

    with patch("app.api.telegram_webhook.message_router") as mock_router:
        mock_router.route_message_telegram = AsyncMock()
        response = client.post(
            "/webhook/telegram",
            json=body,
            headers={"X-Telegram-Bot-Api-Secret-Token": "my-shared-secret"},
        )

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_telegram_post_no_message(test_db):
    """Telegram POST without message returns ok without routing."""
    from app.api.deps import get_db_session

    app.dependency_overrides[get_db_session] = lambda: test_db

    with patch("app.api.telegram_webhook.message_router") as mock_router:
        mock_router.route_message_telegram = AsyncMock()

        response = client.post("/webhook/telegram", json={"update_id": 1})

        assert response.status_code == 200
        mock_router.route_message_telegram.assert_not_called()

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_whatsapp_receive_error_returns_error_body(test_db):
    """WhatsApp POST returns error body when router raises (still 200)."""
    from app.api.deps import get_db_session

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

    with patch("app.api.whatsapp_webhook.message_router") as mock_router:
        mock_router.route_message = AsyncMock(side_effect=Exception("Test error"))

        response = client.post("/webhook/whatsapp", json=webhook_payload)

        assert response.status_code == 200
        assert response.json()["status"] == "error"

    app.dependency_overrides.clear()
