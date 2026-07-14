"""Request and response contracts for the Telegram Mini App API."""
from decimal import Decimal, InvalidOperation
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_validator


class GameLimits(BaseModel):
    """Allowed stake range for one game."""

    minimum: str
    maximum: str


class GameConfig(BaseModel):
    """Public client configuration for one game."""

    id: str
    name: str
    limits: GameLimits
    rules: dict[str, Any]


class MiniAppConfigResponse(BaseModel):
    """Public Mini App game catalogue."""

    currency: str
    games: list[GameConfig]


class MiniAppUserResponse(BaseModel):
    """Authenticated Mini App user and wallet summary."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    telegram_chat_id: str
    username: str | None
    balance: str


class PlayRequest(BaseModel):
    """One idempotent Mini App game attempt."""

    game: str
    stake: Decimal
    data: dict[str, Any]
    idempotency_key: UUID

    @field_validator("stake", mode="before")
    @classmethod
    def validate_stake(cls, value: Any) -> Decimal:
        """Parse stake without binary floating-point balance drift."""
        if isinstance(value, bool):
            raise ValueError("invalid stake")
        try:
            stake = Decimal(str(value))
        except (InvalidOperation, TypeError, ValueError) as exc:
            raise ValueError("invalid stake") from exc
        if not stake.is_finite() or stake <= 0:
            raise ValueError("invalid stake")
        if stake.as_tuple().exponent < -2:
            raise ValueError("stake must have at most two decimal places")
        return stake.quantize(Decimal("0.01"))


class PlayResponse(BaseModel):
    """Authoritative settled result returned to the animation client."""

    result: dict[str, Any]
    balance: str
    bet_id: int
