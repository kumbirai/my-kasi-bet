"""Validation for Telegram Mini App initialization data."""
import hashlib
import hmac
import json
import time
from collections.abc import Callable
from typing import Any
from urllib.parse import parse_qsl

from app.config import settings


class InitDataError(ValueError):
    """Telegram Mini App initialization data failed validation."""


def _parse_fields(init_data: str) -> dict[str, str]:
    if not init_data:
        raise InitDataError("empty initData")

    try:
        pairs = parse_qsl(init_data, strict_parsing=True, keep_blank_values=True)
    except ValueError as exc:
        raise InitDataError("malformed initData") from exc

    fields: dict[str, str] = {}
    for key, value in pairs:
        if not key or key in fields:
            raise InitDataError("malformed initData")
        fields[key] = value
    return fields


def _validate_user(raw_user: str) -> dict[str, Any]:
    try:
        user = json.loads(raw_user)
    except (TypeError, json.JSONDecodeError) as exc:
        raise InitDataError("invalid user data") from exc

    if not isinstance(user, dict):
        raise InitDataError("invalid user data")

    user_id = user.get("id")
    if not isinstance(user_id, int) or isinstance(user_id, bool) or user_id <= 0:
        raise InitDataError("invalid user data")

    username = user.get("username")
    if username is not None and not isinstance(username, str):
        raise InitDataError("invalid user data")
    return user


def verify_init_data(
    init_data: str,
    max_age_seconds: int | None = None,
    *,
    now: Callable[[], float] = time.time,
) -> dict[str, Any]:
    """Verify Telegram HMAC, freshness, and the authenticated user payload."""
    fields = _parse_fields(init_data)
    received_hash = fields.pop("hash", None)
    if not received_hash:
        raise InitDataError("missing hash")

    bot_token = settings.TELEGRAM_BOT_TOKEN
    if not bot_token:
        raise InitDataError("Telegram bot token is not configured")

    data_check_string = "\n".join(
        f"{key}={value}" for key, value in sorted(fields.items())
    )
    secret_key = hmac.new(
        b"WebAppData", bot_token.encode("utf-8"), hashlib.sha256
    ).digest()
    computed_hash = hmac.new(
        secret_key, data_check_string.encode("utf-8"), hashlib.sha256
    ).hexdigest()
    if not hmac.compare_digest(computed_hash, received_hash):
        raise InitDataError("bad signature")

    try:
        auth_date = int(fields.get("auth_date", ""))
    except ValueError as exc:
        raise InitDataError("stale or missing auth_date") from exc

    maximum_age = (
        settings.MINIAPP_INITDATA_MAX_AGE_SECONDS
        if max_age_seconds is None
        else max_age_seconds
    )
    if maximum_age < 0:
        raise ValueError("max_age_seconds must not be negative")
    if auth_date <= 0 or now() - auth_date > maximum_age:
        raise InitDataError("stale or missing auth_date")

    raw_user = fields.get("user")
    if raw_user is None:
        raise InitDataError("no user in initData")
    fields["user"] = _validate_user(raw_user)
    return fields
