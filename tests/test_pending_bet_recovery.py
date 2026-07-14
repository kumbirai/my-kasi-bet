"""Tests for stale Mini App bet recovery."""
from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from app.models.bet import BetStatus, BetType
from app.models.wallet import Wallet
from app.services.bet_service import BetService
from app.services.pending_bet_recovery import PendingBetRecoveryService


def place_pending_bet(test_user, test_db, bet_type=BetType.COLOR_GAME):
    bet_data = (
        {"match_id": 1, "choice": "yes"}
        if bet_type == BetType.FOOTBALL_YESNO
        else {"selected_color": "red"}
    )
    bet = BetService.place_bet(
        user_id=test_user.id,
        bet_type=bet_type,
        stake_amount=Decimal("10.00"),
        bet_data=bet_data,
        db=test_db,
        idempotency_key="d9f36ab8-9b2a-40a4-b3de-393677347f36",
    )
    bet.created_at = datetime.now(timezone.utc) - timedelta(minutes=5)
    test_db.commit()
    return bet


def test_recovery_refunds_stale_immediate_result_bet(test_user, test_db):
    bet = place_pending_bet(test_user, test_db)

    refunded_ids = PendingBetRecoveryService.refund_stale_bets(
        older_than_seconds=120,
        db=test_db,
    )

    test_db.refresh(bet)
    assert refunded_ids == [bet.id]
    assert bet.status == BetStatus.REFUNDED
    assert test_db.query(Wallet).one().balance == Decimal("1000.00")


def test_recovery_ignores_recent_bet(test_user, test_db):
    bet = place_pending_bet(test_user, test_db)
    bet.created_at = datetime.now(timezone.utc)
    test_db.commit()

    refunded_ids = PendingBetRecoveryService.refund_stale_bets(120, test_db)

    test_db.refresh(bet)
    assert refunded_ids == []
    assert bet.status == BetStatus.PENDING
    assert test_db.query(Wallet).one().balance == Decimal("990.00")


def test_recovery_never_refunds_deferred_football_bet(test_user, test_db):
    bet = place_pending_bet(test_user, test_db, BetType.FOOTBALL_YESNO)

    refunded_ids = PendingBetRecoveryService.refund_stale_bets(120, test_db)

    test_db.refresh(bet)
    assert refunded_ids == []
    assert bet.status == BetStatus.PENDING


def test_recovery_rejects_non_positive_age(test_db):
    with pytest.raises(ValueError, match="must be positive"):
        PendingBetRecoveryService.refund_stale_bets(0, test_db)
