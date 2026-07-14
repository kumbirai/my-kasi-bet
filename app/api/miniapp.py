"""Authenticated HTTP surface for the Telegram Mini App."""
import hashlib
import json
import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.api.deps import current_tg_user, get_db_session
from app.models.bet import Bet, BetStatus, BetType
from app.models.user import User
from app.schemas.miniapp import (
    GameConfig,
    GameLimits,
    MiniAppConfigResponse,
    MiniAppUserResponse,
    PlayRequest,
    PlayResponse,
)
from app.services.bet_service import (
    BetService,
    BettingError,
    DuplicateBetRequestError,
    InvalidBetAmountError,
    InvalidBetDataError,
)
from app.services.games.color_game import ColorGame
from app.services.games.lucky_wheel import LuckyWheelGame
from app.services.games.pick_3 import Pick3Game
from app.services.miniapp_guard import (
    IdempotencyKeyConflict,
    MiniAppInfrastructureUnavailable,
    MiniAppRateLimitExceeded,
    MiniAppRequestGuard,
    get_miniapp_request_guard,
)
from app.services.wallet_service import (
    InsufficientBalanceError,
    WalletNotFoundError,
    WalletService,
)

logger = logging.getLogger(__name__)
router = APIRouter()


def _limits(bet_type: BetType) -> GameLimits:
    minimum, maximum = BetService.BET_LIMITS[bet_type]
    return GameLimits(minimum=str(minimum), maximum=str(maximum))


def _play_guard() -> MiniAppRequestGuard:
    try:
        return get_miniapp_request_guard()
    except MiniAppInfrastructureUnavailable as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="betting temporarily unavailable",
        ) from exc


def _request_fingerprint(body: PlayRequest, selected_color: str) -> str:
    payload = json.dumps(
        {
            "game": body.game,
            "stake": str(body.stake),
            "data": {"selected_color": selected_color},
        },
        separators=(",", ":"),
        sort_keys=True,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _bet_matches_request(
    bet: Bet,
    body: PlayRequest,
    selected_color: str,
) -> bool:
    try:
        bet_data = json.loads(bet.bet_data)
    except (TypeError, json.JSONDecodeError):
        return False
    return (
        bet.bet_type == BetType.COLOR_GAME
        and bet.stake_amount == body.stake
        and bet_data == {"selected_color": selected_color}
    )


def _settled_play_response(bet: Bet, db: Session) -> PlayResponse | None:
    if bet.status not in {BetStatus.WON, BetStatus.LOST}:
        return None
    try:
        bet_data = json.loads(bet.bet_data)
        game_result = json.loads(bet.game_result or "{}")
        balance = WalletService.get_balance(bet.user_id, db)
    except (TypeError, json.JSONDecodeError, WalletNotFoundError):
        logger.error("Cannot reconstruct settled Mini App bet_id=%s", bet.id)
        return None

    is_win = bet.status == BetStatus.WON
    return PlayResponse(
        result={
            "selected_color": bet_data["selected_color"],
            "drawn_color": game_result["drawn_color"],
            "is_win": is_win,
            "stake": float(bet.stake_amount),
            "payout": float(bet.payout_amount) if is_win else 0,
            "multiplier": float(bet.multiplier or 0),
        },
        balance=str(balance),
        bet_id=bet.id,
    )


def _release_claim(
    guard: MiniAppRequestGuard,
    user_id: int,
    idempotency_key: str,
    fingerprint: str,
) -> None:
    try:
        guard.release(user_id, idempotency_key, fingerprint)
    except MiniAppInfrastructureUnavailable:
        logger.warning(
            "Could not release Mini App idempotency claim: user_id=%s key=%s",
            user_id,
            idempotency_key,
        )


@router.get("/config", response_model=MiniAppConfigResponse)
def get_miniapp_config() -> MiniAppConfigResponse:
    """Return the public game catalogue without exposing implementation details."""
    return MiniAppConfigResponse(
        currency="ZAR",
        games=[
            GameConfig(
                id="color",
                name="Color Game",
                limits=_limits(BetType.COLOR_GAME),
                rules={
                    "colors": ColorGame.VALID_COLORS,
                    "multiplier": str(ColorGame.MULTIPLIER),
                },
            ),
            GameConfig(
                id="wheel",
                name="Lucky Wheel",
                limits=_limits(BetType.LUCKY_WHEEL),
                rules={
                    "minimum_number": LuckyWheelGame.MIN_NUMBER,
                    "maximum_number": LuckyWheelGame.MAX_NUMBER,
                    "multiplier": str(LuckyWheelGame.MULTIPLIER),
                },
            ),
            GameConfig(
                id="pick3",
                name="Pick 3",
                limits=_limits(BetType.PICK_3),
                rules={
                    "minimum_number": Pick3Game.MIN_NUMBER,
                    "maximum_number": Pick3Game.MAX_NUMBER,
                    "numbers_to_pick": Pick3Game.NUMBERS_TO_PICK,
                    "multipliers": {
                        "one_match": str(Pick3Game.ONE_MATCH_MULTIPLIER),
                        "two_matches": str(Pick3Game.TWO_MATCH_MULTIPLIER),
                        "three_matches": str(Pick3Game.JACKPOT_MULTIPLIER),
                    },
                },
            ),
            GameConfig(
                id="football",
                name="Football Yes/No",
                limits=_limits(BetType.FOOTBALL_YESNO),
                rules={"outcomes": ["yes", "no"], "odds": "per_match"},
            ),
        ],
    )


@router.get("/me", response_model=MiniAppUserResponse)
def get_current_miniapp_user(
    user: User = Depends(current_tg_user),
    db: Session = Depends(get_db_session),
) -> MiniAppUserResponse:
    """Return the verified user and authoritative wallet balance."""
    try:
        balance = WalletService.get_balance(user.id, db)
    except WalletNotFoundError as exc:
        logger.error("Wallet missing for Telegram Mini App user_id=%s", user.id)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="wallet unavailable",
        ) from exc

    return MiniAppUserResponse(
        id=user.id,
        telegram_chat_id=user.telegram_chat_id,
        username=user.username,
        balance=str(balance),
    )


@router.post("/play", response_model=PlayResponse)
async def play_miniapp_game(
    body: PlayRequest,
    request: Request,
    user: User = Depends(current_tg_user),
    db: Session = Depends(get_db_session),
    guard: MiniAppRequestGuard = Depends(_play_guard),
) -> PlayResponse:
    """Place and settle one idempotent, server-authoritative Color Game bet."""
    if body.game != "color":
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="unknown game",
        )
    try:
        selected_color = ColorGame.validate_bet_data(body.data)
    except (InvalidBetDataError, AttributeError) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc

    idempotency_key = str(body.idempotency_key)
    fingerprint = _request_fingerprint(body, selected_color)
    try:
        claim = guard.claim(user.id, idempotency_key, fingerprint)
    except IdempotencyKeyConflict as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="idempotency key reused for a different request",
        ) from exc
    except MiniAppInfrastructureUnavailable as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="betting temporarily unavailable",
        ) from exc

    if claim.cached_response is not None:
        return PlayResponse.model_validate(claim.cached_response)

    existing = BetService.get_bet_by_idempotency_key(
        user_id=user.id,
        idempotency_key=idempotency_key,
        db=db,
    )
    if existing:
        if not _bet_matches_request(existing, body, selected_color):
            if claim.acquired:
                _release_claim(guard, user.id, idempotency_key, fingerprint)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="idempotency key reused for a different request",
            )
        recovered = _settled_play_response(existing, db)
        if recovered is None:
            if existing.status == BetStatus.REFUNDED:
                _release_claim(guard, user.id, idempotency_key, fingerprint)
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="bet refunded",
                )
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="bet settlement pending",
            )
        try:
            guard.complete(
                user.id,
                idempotency_key,
                fingerprint,
                recovered.model_dump(mode="json"),
            )
        except MiniAppInfrastructureUnavailable:
            logger.warning("Could not cache recovered Mini App bet_id=%s", existing.id)
        return recovered

    if not claim.acquired:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="bet request already in progress",
        )

    try:
        guard.enforce_rate_limit(user.id)
    except MiniAppRateLimitExceeded as exc:
        _release_claim(guard, user.id, idempotency_key, fingerprint)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="play rate limit exceeded",
            headers={"Retry-After": "60"},
        ) from exc
    except MiniAppInfrastructureUnavailable as exc:
        _release_claim(guard, user.id, idempotency_key, fingerprint)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="betting temporarily unavailable",
        ) from exc

    client_address = request.client.host if request.client else None
    try:
        bet, result = await ColorGame.play(
            user_id=user.id,
            stake_amount=body.stake,
            bet_data={"selected_color": selected_color},
            db=db,
            ip_address=client_address,
            user_agent=request.headers.get("user-agent"),
            idempotency_key=idempotency_key,
        )
    except DuplicateBetRequestError as exc:
        duplicate = db.query(Bet).filter(Bet.id == exc.bet_id).first()
        recovered = _settled_play_response(duplicate, db) if duplicate else None
        if recovered is None:
            if duplicate and duplicate.status == BetStatus.REFUNDED:
                _release_claim(guard, user.id, idempotency_key, fingerprint)
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="bet refunded",
                ) from exc
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="bet settlement pending",
            ) from exc
        return recovered
    except InvalidBetAmountError as exc:
        _release_claim(guard, user.id, idempotency_key, fingerprint)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc
    except InsufficientBalanceError as exc:
        _release_claim(guard, user.id, idempotency_key, fingerprint)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="insufficient balance",
        ) from exc
    except (InvalidBetDataError, AttributeError) as exc:
        _release_claim(guard, user.id, idempotency_key, fingerprint)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc
    except BettingError as exc:
        logger.error(
            "Mini App bet failed after claim: user_id=%s key=%s",
            user.id,
            idempotency_key,
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="bet settlement unavailable",
        ) from exc

    response = PlayResponse(
        result=result,
        balance=str(WalletService.get_balance(user.id, db)),
        bet_id=bet.id,
    )
    try:
        guard.complete(
            user.id,
            idempotency_key,
            fingerprint,
            response.model_dump(mode="json"),
        )
    except MiniAppInfrastructureUnavailable:
        logger.warning("Could not cache settled Mini App bet_id=%s", bet.id)
    return response
