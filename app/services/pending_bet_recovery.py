"""Recovery of stale, debited Mini App bets that never settled."""
import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models.bet import Bet, BetStatus, BetType
from app.services.admin_service import AdminService
from app.services.bet_service import BetService, BettingError

logger = logging.getLogger(__name__)


class PendingBetRecoveryService:
    """Refund bounded batches of orphaned immediate-result Mini App bets."""

    IMMEDIATE_RESULT_GAMES = (
        BetType.COLOR_GAME,
        BetType.LUCKY_WHEEL,
        BetType.PICK_3,
    )
    MAX_BATCH_SIZE = 100

    @staticmethod
    def refund_stale_bets(
        older_than_seconds: int,
        db: Session,
        admin_id: int | None = None,
    ) -> list[int]:
        """Refund eligible pending bets and return the successfully handled ids."""
        if older_than_seconds <= 0:
            raise ValueError("older_than_seconds must be positive")

        cutoff = datetime.now(timezone.utc) - timedelta(seconds=older_than_seconds)
        candidate_ids = [
            bet_id
            for (bet_id,) in (
                db.query(Bet.id)
                .filter(
                    Bet.status == BetStatus.PENDING,
                    Bet.idempotency_key.isnot(None),
                    Bet.bet_type.in_(
                        PendingBetRecoveryService.IMMEDIATE_RESULT_GAMES
                    ),
                    Bet.created_at < cutoff,
                )
                .order_by(Bet.created_at.asc())
                .limit(PendingBetRecoveryService.MAX_BATCH_SIZE)
                .all()
            )
        ]

        refunded_ids: list[int] = []
        for bet_id in candidate_ids:
            try:
                if admin_id is not None:
                    AdminService.log_admin_action(
                        admin_id=admin_id,
                        action_type="refund_stale_miniapp_bet",
                        entity_type="bet",
                        entity_id=bet_id,
                        details={
                            "maximum_pending_age_seconds": older_than_seconds
                        },
                        db=db,
                    )
                BetService.refund_bet(
                    bet_id=bet_id,
                    reason="Automatic refund: Mini App settlement did not complete",
                    db=db,
                )
                refunded_ids.append(bet_id)
            except BettingError:
                logger.info(
                    "Skipped stale pending bet after concurrent state change: bet_id=%s",
                    bet_id,
                )

        if refunded_ids:
            logger.warning(
                "Refunded stale Mini App bets: count=%s bet_ids=%s",
                len(refunded_ids),
                refunded_ids,
            )
        return refunded_ids
