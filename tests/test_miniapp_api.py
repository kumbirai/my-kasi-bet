"""Contract tests for the read-only Telegram Mini App API."""
import hashlib
import hmac
import json
import time
from decimal import Decimal
from urllib.parse import urlencode

import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_db_session
from app.api.miniapp import _play_guard
from app.config import settings
from app.main import app
from app.models.bet import BetType
from app.models.user import User
from app.models.wallet import Wallet
from app.services.bet_service import BetService
from app.services.miniapp_guard import (
    IdempotencyClaim,
    IdempotencyKeyConflict,
    MiniAppRateLimitExceeded,
)


BOT_TOKEN = "123456:test-token"
client = TestClient(app)


class MemoryRequestGuard:
    """Deterministic in-memory guard used at the HTTP contract boundary."""

    def __init__(self):
        self.requests = {}
        self.rate_limited = False

    def claim(self, user_id, idempotency_key, fingerprint):
        key = (user_id, idempotency_key)
        existing = self.requests.get(key)
        if existing is None:
            self.requests[key] = {
                "fingerprint": fingerprint,
                "response": None,
            }
            return IdempotencyClaim(acquired=True)
        if existing["fingerprint"] != fingerprint:
            raise IdempotencyKeyConflict()
        return IdempotencyClaim(
            acquired=False,
            cached_response=existing["response"],
        )

    def enforce_rate_limit(self, user_id):
        if self.rate_limited:
            raise MiniAppRateLimitExceeded()

    def complete(self, user_id, idempotency_key, fingerprint, response):
        self.requests[(user_id, idempotency_key)] = {
            "fingerprint": fingerprint,
            "response": response,
        }

    def release(self, user_id, idempotency_key, fingerprint):
        key = (user_id, idempotency_key)
        existing = self.requests.get(key)
        if existing and existing["fingerprint"] == fingerprint:
            del self.requests[key]


def signed_init_data(user_id: int, username: str | None = None) -> str:
    """Create a fresh signed Telegram payload for API tests."""
    user = {"id": user_id}
    if username is not None:
        user["username"] = username
    fields = {
        "auth_date": str(int(time.time())),
        "query_id": "AAHdF6IQAAAAAN0XohDhrOrc",
        "user": json.dumps(user, separators=(",", ":")),
    }
    data_check_string = "\n".join(
        f"{key}={value}" for key, value in sorted(fields.items())
    )
    secret_key = hmac.new(
        b"WebAppData", BOT_TOKEN.encode(), hashlib.sha256
    ).digest()
    fields["hash"] = hmac.new(
        secret_key, data_check_string.encode(), hashlib.sha256
    ).hexdigest()
    return urlencode(fields)


@pytest.fixture(autouse=True)
def miniapp_dependencies(test_db, monkeypatch):
    monkeypatch.setattr(settings, "TELEGRAM_BOT_TOKEN", BOT_TOKEN)
    guard = MemoryRequestGuard()
    app.dependency_overrides[get_db_session] = lambda: test_db
    app.dependency_overrides[_play_guard] = lambda: guard
    yield guard
    app.dependency_overrides.clear()


def create_funded_user(test_db, balance=Decimal("100.00")):
    user = User(telegram_chat_id="99887766", username="player")
    test_db.add(user)
    test_db.flush()
    test_db.add(Wallet(user_id=user.id, balance=balance))
    test_db.commit()
    return user


def color_play_payload(
    *,
    stake="10.00",
    color="red",
    key="d9f36ab8-9b2a-40a4-b3de-393677347f36",
):
    return {
        "game": "color",
        "stake": stake,
        "data": {"selected_color": color},
        "idempotency_key": key,
    }


def test_config_returns_public_server_authoritative_game_catalogue():
    response = client.get("/api/miniapp/config")

    assert response.status_code == 200
    payload = response.json()
    assert payload["currency"] == "ZAR"
    assert [game["id"] for game in payload["games"]] == [
        "color",
        "wheel",
        "pick3",
        "football",
    ]
    assert payload["games"][0]["limits"] == {
        "minimum": "5.00",
        "maximum": "500.00",
    }
    assert payload["games"][0]["rules"]["colors"] == [
        "red",
        "green",
        "blue",
        "yellow",
    ]


def test_me_creates_first_time_user_and_zero_balance(test_db):
    response = client.get(
        "/api/miniapp/me",
        headers={"X-Init-Data": signed_init_data(99887766, "kasi_player")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["telegram_chat_id"] == "99887766"
    assert payload["username"] == "kasi_player"
    assert payload["balance"] == "0.00"
    assert test_db.query(User).filter_by(telegram_chat_id="99887766").count() == 1
    assert test_db.query(Wallet).count() == 1


def test_me_returns_existing_users_authoritative_balance(test_db):
    user = User(telegram_chat_id="99887766", username="existing")
    test_db.add(user)
    test_db.flush()
    test_db.add(Wallet(user_id=user.id, balance=Decimal("125.50")))
    test_db.commit()

    response = client.get(
        "/api/miniapp/me",
        headers={"X-Init-Data": signed_init_data(99887766)},
    )

    assert response.status_code == 200
    assert response.json()["balance"] == "125.50"
    assert test_db.query(User).count() == 1


@pytest.mark.parametrize(
    "user_state",
    [{"is_blocked": True}, {"is_active": False}],
)
def test_me_rejects_unavailable_account(test_db, user_state):
    user = User(telegram_chat_id="99887766", **user_state)
    test_db.add(user)
    test_db.flush()
    test_db.add(Wallet(user_id=user.id, balance=Decimal("0.00")))
    test_db.commit()

    response = client.get(
        "/api/miniapp/me",
        headers={"X-Init-Data": signed_init_data(99887766)},
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "account unavailable"}


@pytest.mark.parametrize("headers", [{}, {"X-Init-Data": "forged"}])
def test_me_rejects_missing_or_invalid_init_data(headers):
    response = client.get("/api/miniapp/me", headers=headers)

    assert response.status_code == 401
    assert response.json() == {"detail": "invalid Telegram auth"}


def test_me_surfaces_missing_wallet_as_service_failure(test_db):
    test_db.add(User(telegram_chat_id="99887766"))
    test_db.commit()

    response = client.get(
        "/api/miniapp/me",
        headers={"X-Init-Data": signed_init_data(99887766)},
    )

    assert response.status_code == 503
    assert response.json() == {"detail": "wallet unavailable"}


def test_play_settles_color_bet_and_returns_authoritative_balance(
    test_db,
    monkeypatch,
):
    create_funded_user(test_db)
    monkeypatch.setattr("app.services.games.color_game.secrets.randbelow", lambda _: 0)

    response = client.post(
        "/api/miniapp/play",
        headers={"X-Init-Data": signed_init_data(99887766)},
        json=color_play_payload(),
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["result"] == {
        "selected_color": "red",
        "drawn_color": "red",
        "is_win": True,
        "stake": 10.0,
        "payout": 30.0,
        "multiplier": 3.0,
    }
    assert payload["balance"] == "120.00"
    assert payload["bet_id"] > 0
    assert test_db.query(Wallet).one().balance == Decimal("120.00")


def test_play_replays_same_response_without_second_debit(test_db, monkeypatch):
    create_funded_user(test_db)
    monkeypatch.setattr("app.services.games.color_game.secrets.randbelow", lambda _: 1)
    headers = {"X-Init-Data": signed_init_data(99887766)}
    request = color_play_payload()

    first = client.post("/api/miniapp/play", headers=headers, json=request)
    second = client.post("/api/miniapp/play", headers=headers, json=request)

    assert first.status_code == 200
    assert second.status_code == 200
    assert second.json() == first.json()
    assert test_db.query(Wallet).one().balance == Decimal("90.00")
    assert len(test_db.query(User).one().bets) == 1


def test_play_reports_a_recovered_refund_as_a_definitive_outcome(test_db):
    user = create_funded_user(test_db)
    request = color_play_payload()
    bet = BetService.place_bet(
        user_id=user.id,
        bet_type=BetType.COLOR_GAME,
        stake_amount=Decimal(request["stake"]),
        bet_data=request["data"],
        db=test_db,
        idempotency_key=request["idempotency_key"],
    )
    BetService.refund_bet(bet.id, "settlement recovery", test_db)

    response = client.post(
        "/api/miniapp/play",
        headers={"X-Init-Data": signed_init_data(99887766)},
        json=request,
    )

    assert response.status_code == 409
    assert response.json() == {"detail": "bet refunded"}
    assert test_db.query(Wallet).one().balance == Decimal("100.00")


def test_play_rejects_idempotency_key_reuse_for_different_request(
    test_db,
    monkeypatch,
):
    create_funded_user(test_db)
    monkeypatch.setattr("app.services.games.color_game.secrets.randbelow", lambda _: 1)
    headers = {"X-Init-Data": signed_init_data(99887766)}
    first = client.post(
        "/api/miniapp/play",
        headers=headers,
        json=color_play_payload(color="red"),
    )

    second = client.post(
        "/api/miniapp/play",
        headers=headers,
        json=color_play_payload(color="blue"),
    )

    assert first.status_code == 200
    assert second.status_code == 409
    assert test_db.query(Wallet).one().balance == Decimal("90.00")


@pytest.mark.parametrize(
    "payload",
    [
        color_play_payload(stake="4.99"),
        color_play_payload(stake="500.01"),
        color_play_payload(stake="5.001"),
        color_play_payload(stake="NaN"),
        color_play_payload(stake="Infinity"),
        color_play_payload(stake="-5.00"),
    ],
)
def test_play_rejects_invalid_stakes_without_debit(test_db, payload):
    create_funded_user(test_db, balance=Decimal("1000.00"))

    response = client.post(
        "/api/miniapp/play",
        headers={"X-Init-Data": signed_init_data(99887766)},
        json=payload,
    )

    assert response.status_code == 422
    assert test_db.query(Wallet).one().balance == Decimal("1000.00")


def test_play_rejects_insufficient_balance_without_creating_bet(test_db):
    create_funded_user(test_db, balance=Decimal("5.00"))

    response = client.post(
        "/api/miniapp/play",
        headers={"X-Init-Data": signed_init_data(99887766)},
        json=color_play_payload(stake="10.00"),
    )

    assert response.status_code == 409
    assert response.json() == {"detail": "insufficient balance"}
    assert test_db.query(Wallet).one().balance == Decimal("5.00")
    assert len(test_db.query(User).one().bets) == 0


def test_play_rejects_unknown_game(test_db):
    create_funded_user(test_db)
    payload = color_play_payload()
    payload["game"] = "wheel"

    response = client.post(
        "/api/miniapp/play",
        headers={"X-Init-Data": signed_init_data(99887766)},
        json=payload,
    )

    assert response.status_code == 422
    assert response.json() == {"detail": "unknown game"}


def test_play_enforces_per_user_rate_limit(test_db, miniapp_dependencies):
    create_funded_user(test_db)
    miniapp_dependencies.rate_limited = True

    response = client.post(
        "/api/miniapp/play",
        headers={"X-Init-Data": signed_init_data(99887766)},
        json=color_play_payload(),
    )

    assert response.status_code == 429
    assert response.headers["Retry-After"] == "60"
    assert test_db.query(Wallet).one().balance == Decimal("100.00")
