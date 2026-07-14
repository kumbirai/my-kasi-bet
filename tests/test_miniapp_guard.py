"""Unit tests for Redis-backed Mini App request guards."""
import pytest
from redis.exceptions import ConnectionError

from app.config import settings
from app.services.miniapp_guard import (
    IdempotencyKeyConflict,
    MiniAppInfrastructureUnavailable,
    MiniAppRateLimitExceeded,
    MiniAppRequestGuard,
)


class FakeRedis:
    """Small Redis command model covering the guard's atomic scripts."""

    def __init__(self):
        self.values = {}
        self.counts = {}
        self.fail = False

    def set(self, key, value, ex=None, nx=False):
        if self.fail:
            raise ConnectionError()
        if nx and key in self.values:
            return False
        self.values[key] = value
        return True

    def get(self, key):
        if self.fail:
            raise ConnectionError()
        return self.values.get(key)

    def eval(self, script, key_count, key, *arguments):
        if self.fail:
            raise ConnectionError()
        if "INCR" in script:
            self.counts[key] = self.counts.get(key, 0) + 1
            return self.counts[key]
        expected = arguments[0]
        if self.values.get(key) == expected:
            del self.values[key]
            return 1
        return 0


def test_claim_complete_and_replay_round_trip():
    guard = MiniAppRequestGuard(FakeRedis())

    first = guard.claim(7, "request-id", "fingerprint")
    guard.complete(7, "request-id", "fingerprint", {"bet_id": 42})
    replay = guard.claim(7, "request-id", "fingerprint")

    assert first.acquired is True
    assert replay.acquired is False
    assert replay.cached_response == {"bet_id": 42}


def test_claim_rejects_key_reuse_with_different_fingerprint():
    guard = MiniAppRequestGuard(FakeRedis())
    guard.claim(7, "request-id", "first")

    with pytest.raises(IdempotencyKeyConflict):
        guard.claim(7, "request-id", "second")


def test_release_only_removes_matching_processing_claim():
    client = FakeRedis()
    guard = MiniAppRequestGuard(client)
    guard.claim(7, "request-id", "first")

    guard.release(7, "request-id", "second")
    assert len(client.values) == 1
    guard.release(7, "request-id", "first")
    assert client.values == {}


def test_rate_limit_rejects_requests_over_configured_limit(monkeypatch):
    guard = MiniAppRequestGuard(FakeRedis())
    monkeypatch.setattr(settings, "MINIAPP_RATE_LIMIT_PER_MIN", 2)

    guard.enforce_rate_limit(7)
    guard.enforce_rate_limit(7)
    with pytest.raises(MiniAppRateLimitExceeded):
        guard.enforce_rate_limit(7)


def test_guard_fails_closed_when_redis_disconnects():
    client = FakeRedis()
    client.fail = True
    guard = MiniAppRequestGuard(client)

    with pytest.raises(MiniAppInfrastructureUnavailable):
        guard.claim(7, "request-id", "fingerprint")
