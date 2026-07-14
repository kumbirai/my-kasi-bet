"""Tests for Telegram Mini App initialization-data verification."""
import hashlib
import hmac
import json
from urllib.parse import urlencode

import pytest

from app.config import settings
from app.utils.telegram_auth import InitDataError, verify_init_data


BOT_TOKEN = "123456:test-token"
NOW = 1_750_000_000


def signed_init_data(
    *,
    auth_date: int = NOW,
    user: object | None = None,
    signature: str | None = None,
    reverse_secret_arguments: bool = False,
) -> str:
    """Build a Telegram-compatible signed query string for a test user."""
    fields = {
        "auth_date": str(auth_date),
        "query_id": "AAHdF6IQAAAAAN0XohDhrOrc",
    }
    if user is not None:
        fields["user"] = json.dumps(user, separators=(",", ":"))
    if signature is not None:
        fields["signature"] = signature

    data_check_string = "\n".join(
        f"{key}={value}" for key, value in sorted(fields.items())
    )
    if reverse_secret_arguments:
        secret_key = hmac.new(
            BOT_TOKEN.encode(), b"WebAppData", hashlib.sha256
        ).digest()
    else:
        secret_key = hmac.new(
            b"WebAppData", BOT_TOKEN.encode(), hashlib.sha256
        ).digest()
    fields["hash"] = hmac.new(
        secret_key, data_check_string.encode(), hashlib.sha256
    ).hexdigest()
    return urlencode(fields)


@pytest.fixture(autouse=True)
def telegram_bot_token(monkeypatch):
    monkeypatch.setattr(settings, "TELEGRAM_BOT_TOKEN", BOT_TOKEN)


def test_verify_init_data_accepts_valid_payload_with_modern_signature_field():
    init_data = signed_init_data(
        user={"id": 99887766, "username": "kasi_player"},
        signature="third-party-ed25519-signature",
    )

    result = verify_init_data(init_data, now=lambda: NOW)

    assert result["user"] == {"id": 99887766, "username": "kasi_player"}
    assert result["signature"] == "third-party-ed25519-signature"


def test_verify_init_data_rejects_tampered_payload():
    init_data = signed_init_data(user={"id": 99887766}).replace(
        "99887766", "11223344"
    )

    with pytest.raises(InitDataError, match="bad signature"):
        verify_init_data(init_data, now=lambda: NOW)


def test_verify_init_data_rejects_reversed_secret_arguments():
    init_data = signed_init_data(
        user={"id": 99887766}, reverse_secret_arguments=True
    )

    with pytest.raises(InitDataError, match="bad signature"):
        verify_init_data(init_data, now=lambda: NOW)


def test_verify_init_data_rejects_stale_payload():
    init_data = signed_init_data(auth_date=NOW - 61, user={"id": 99887766})

    with pytest.raises(InitDataError, match="stale or missing auth_date"):
        verify_init_data(init_data, max_age_seconds=60, now=lambda: NOW)


@pytest.mark.parametrize(
    ("init_data", "message"),
    [
        ("", "empty initData"),
        ("auth_date", "malformed initData"),
        ("auth_date=1&auth_date=2&hash=value", "malformed initData"),
        ("auth_date=1", "missing hash"),
    ],
)
def test_verify_init_data_rejects_malformed_payloads(init_data, message):
    with pytest.raises(InitDataError, match=message):
        verify_init_data(init_data, now=lambda: NOW)


def test_verify_init_data_rejects_missing_user():
    init_data = signed_init_data()

    with pytest.raises(InitDataError, match="no user in initData"):
        verify_init_data(init_data, now=lambda: NOW)


@pytest.mark.parametrize(
    "user",
    ["not-an-object", {"id": True}, {"id": 0}, {"id": 99887766, "username": 5}],
)
def test_verify_init_data_rejects_invalid_user(user):
    init_data = signed_init_data(user=user)

    with pytest.raises(InitDataError, match="invalid user data"):
        verify_init_data(init_data, now=lambda: NOW)


def test_verify_init_data_fails_closed_without_bot_token(monkeypatch):
    init_data = signed_init_data(user={"id": 99887766})
    monkeypatch.setattr(settings, "TELEGRAM_BOT_TOKEN", None)

    with pytest.raises(InitDataError, match="bot token is not configured"):
        verify_init_data(init_data, now=lambda: NOW)


def test_verify_init_data_rejects_negative_maximum_age():
    init_data = signed_init_data(user={"id": 99887766})

    with pytest.raises(ValueError, match="must not be negative"):
        verify_init_data(init_data, max_age_seconds=-1, now=lambda: NOW)
