"""Redis-backed abuse and duplicate-request guards for Mini App betting."""
import json
import time
from dataclasses import dataclass
from typing import Any

from redis import Redis
from redis.exceptions import RedisError

from app.config import settings
from app.redis_client import get_redis_client


RATE_LIMIT_SCRIPT = """
local count = redis.call('INCR', KEYS[1])
if count == 1 then
    redis.call('EXPIRE', KEYS[1], ARGV[1])
end
return count
"""

RELEASE_CLAIM_SCRIPT = """
if redis.call('GET', KEYS[1]) == ARGV[1] then
    return redis.call('DEL', KEYS[1])
end
return 0
"""


class MiniAppGuardError(RuntimeError):
    """Base error for Mini App request guarding."""


class MiniAppInfrastructureUnavailable(MiniAppGuardError):
    """The authoritative Redis guard is unavailable."""


class MiniAppRateLimitExceeded(MiniAppGuardError):
    """A user exceeded the configured play-request limit."""


class IdempotencyKeyConflict(MiniAppGuardError):
    """An idempotency key was reused for a different request."""


@dataclass(frozen=True)
class IdempotencyClaim:
    """Result of atomically claiming an idempotency key."""

    acquired: bool
    cached_response: dict[str, Any] | None = None


class MiniAppRequestGuard:
    """Coordinate per-user rate limits and short-lived response replay."""

    IDEMPOTENCY_TTL_SECONDS = 3600
    RATE_WINDOW_TTL_SECONDS = 120

    def __init__(self, client: Redis):
        self._client = client

    @staticmethod
    def _idempotency_redis_key(user_id: int, idempotency_key: str) -> str:
        return f"miniapp:idempotency:{user_id}:{idempotency_key}"

    @staticmethod
    def _processing_payload(fingerprint: str) -> str:
        return json.dumps(
            {"state": "processing", "fingerprint": fingerprint},
            separators=(",", ":"),
            sort_keys=True,
        )

    def enforce_rate_limit(self, user_id: int) -> None:
        """Apply an atomic fixed-window play limit for one verified user."""
        minute = int(time.time() // 60)
        key = f"miniapp:play-rate:{user_id}:{minute}"
        try:
            count = int(
                self._client.eval(
                    RATE_LIMIT_SCRIPT,
                    1,
                    key,
                    self.RATE_WINDOW_TTL_SECONDS,
                )
            )
        except (RedisError, TypeError, ValueError) as exc:
            raise MiniAppInfrastructureUnavailable(
                "Mini App request guard is unavailable"
            ) from exc
        if count > settings.MINIAPP_RATE_LIMIT_PER_MIN:
            raise MiniAppRateLimitExceeded("play rate limit exceeded")

    def claim(
        self,
        user_id: int,
        idempotency_key: str,
        fingerprint: str,
    ) -> IdempotencyClaim:
        """Claim a request or return its completed cached response."""
        key = self._idempotency_redis_key(user_id, idempotency_key)
        processing = self._processing_payload(fingerprint)
        try:
            acquired = self._client.set(
                key,
                processing,
                ex=self.IDEMPOTENCY_TTL_SECONDS,
                nx=True,
            )
            if acquired:
                return IdempotencyClaim(acquired=True)
            raw_value = self._client.get(key)
            value = json.loads(raw_value) if raw_value else None
        except (RedisError, TypeError, ValueError, json.JSONDecodeError) as exc:
            raise MiniAppInfrastructureUnavailable(
                "Mini App request guard is unavailable"
            ) from exc

        if not isinstance(value, dict) or value.get("fingerprint") != fingerprint:
            raise IdempotencyKeyConflict(
                "idempotency key was reused for another request"
            )
        response = value.get("response") if value.get("state") == "complete" else None
        if response is not None and not isinstance(response, dict):
            raise MiniAppInfrastructureUnavailable(
                "Mini App request guard contains an invalid cached response"
            )
        return IdempotencyClaim(acquired=False, cached_response=response)

    def complete(
        self,
        user_id: int,
        idempotency_key: str,
        fingerprint: str,
        response: dict[str, Any],
    ) -> None:
        """Cache the canonical response for safe replay."""
        key = self._idempotency_redis_key(user_id, idempotency_key)
        payload = json.dumps(
            {
                "state": "complete",
                "fingerprint": fingerprint,
                "response": response,
            },
            separators=(",", ":"),
            sort_keys=True,
        )
        try:
            self._client.set(key, payload, ex=self.IDEMPOTENCY_TTL_SECONDS)
        except RedisError as exc:
            raise MiniAppInfrastructureUnavailable(
                "Mini App request guard is unavailable"
            ) from exc

    def release(
        self,
        user_id: int,
        idempotency_key: str,
        fingerprint: str,
    ) -> None:
        """Release this caller's claim after a non-mutating rejection."""
        key = self._idempotency_redis_key(user_id, idempotency_key)
        processing = self._processing_payload(fingerprint)
        try:
            self._client.eval(RELEASE_CLAIM_SCRIPT, 1, key, processing)
        except RedisError as exc:
            raise MiniAppInfrastructureUnavailable(
                "Mini App request guard is unavailable"
            ) from exc


def get_miniapp_request_guard() -> MiniAppRequestGuard:
    """Create the fail-closed request guard for a Mini App play request."""
    client = get_redis_client()
    if client is None:
        raise MiniAppInfrastructureUnavailable(
            "Mini App request guard is unavailable"
        )
    return MiniAppRequestGuard(client)
