"""
Unit tests for BetService.

Tests bet placement, settlement, refund, history, and statistics.
"""
import pytest
from decimal import Decimal

from app.models.bet import Bet, BetStatus, BetType
from app.models.user import User
from app.models.wallet import Wallet
from app.services.bet_service import (
    BetService,
    BettingError,
    InvalidBetAmountError,
    InvalidBetDataError,
)
from app.services.wallet_service import InsufficientBalanceError


def test_place_bet_success(test_user, test_db):
    """Test successful bet placement."""
    bet = BetService.place_bet(
        user_id=test_user.id,
        bet_type=BetType.LUCKY_WHEEL,
        stake_amount=Decimal("50.00"),
        bet_data={"selected_number": 7},
        db=test_db,
    )

    assert bet.id is not None
    assert bet.user_id == test_user.id
    assert bet.bet_type == BetType.LUCKY_WHEEL
    assert bet.stake_amount == Decimal("50.00")
    assert bet.status == BetStatus.PENDING

    # Verify wallet debited
    wallet = test_db.query(Wallet).filter(Wallet.user_id == test_user.id).first()
    assert wallet.balance == Decimal("950.00")


def test_place_bet_insufficient_balance(test_user, test_db):
    """Test bet placement with insufficient balance."""
    # Set balance to low amount
    wallet = test_db.query(Wallet).filter(Wallet.user_id == test_user.id).first()
    wallet.balance = Decimal("10.00")
    test_db.commit()

    with pytest.raises(InsufficientBalanceError):
        BetService.place_bet(
            user_id=test_user.id,
            bet_type=BetType.LUCKY_WHEEL,
            stake_amount=Decimal("50.00"),
            bet_data={"selected_number": 7},
            db=test_db,
        )


def test_place_bet_below_minimum(test_user, test_db):
    """Test bet placement below minimum."""
    with pytest.raises(InvalidBetAmountError):
        BetService.place_bet(
            user_id=test_user.id,
            bet_type=BetType.LUCKY_WHEEL,
            stake_amount=Decimal("1.00"),  # Below minimum of R5
            bet_data={"selected_number": 7},
            db=test_db,
        )


def test_place_bet_above_maximum(test_user, test_db):
    """Test bet placement above maximum."""
    with pytest.raises(InvalidBetAmountError):
        BetService.place_bet(
            user_id=test_user.id,
            bet_type=BetType.LUCKY_WHEEL,
            stake_amount=Decimal("1000.00"),  # Above maximum of R500
            bet_data={"selected_number": 7},
            db=test_db,
        )


def test_settle_bet_win(test_user, test_db):
    """Test settling a winning bet."""
    # Place bet
    bet = BetService.place_bet(
        user_id=test_user.id,
        bet_type=BetType.LUCKY_WHEEL,
        stake_amount=Decimal("50.00"),
        bet_data={"selected_number": 7},
        db=test_db,
    )

    initial_balance = Decimal("950.00")  # After bet placement

    # Settle as win
    bet = BetService.settle_bet(
        bet_id=bet.id,
        game_result={"drawn_number": 7},
        is_win=True,
        multiplier=Decimal("10.0"),
        db=test_db,
    )

    assert bet.status == BetStatus.WON
    assert bet.payout_amount == Decimal("500.00")  # 50 * 10

    # Verify wallet credited
    wallet = test_db.query(Wallet).filter(Wallet.user_id == test_user.id).first()
    assert wallet.balance == initial_balance + Decimal("500.00")


def test_settle_bet_loss(test_user, test_db):
    """Test settling a losing bet."""
    # Place bet
    bet = BetService.place_bet(
        user_id=test_user.id,
        bet_type=BetType.LUCKY_WHEEL,
        stake_amount=Decimal("50.00"),
        bet_data={"selected_number": 7},
        db=test_db,
    )

    initial_balance = Decimal("950.00")  # After bet placement

    # Settle as loss
    bet = BetService.settle_bet(
        bet_id=bet.id,
        game_result={"drawn_number": 8},
        is_win=False,
        multiplier=Decimal("0.0"),
        db=test_db,
    )

    assert bet.status == BetStatus.LOST
    assert bet.payout_amount == Decimal("0.00")

    # Verify wallet not credited
    wallet = test_db.query(Wallet).filter(Wallet.user_id == test_user.id).first()
    assert wallet.balance == initial_balance


def test_refund_bet(test_user, test_db):
    """Test refunding a bet."""
    # Place bet
    bet = BetService.place_bet(
        user_id=test_user.id,
        bet_type=BetType.LUCKY_WHEEL,
        stake_amount=Decimal("50.00"),
        bet_data={"selected_number": 7},
        db=test_db,
    )

    initial_balance = Decimal("950.00")  # After bet placement

    # Refund bet
    bet = BetService.refund_bet(
        bet_id=bet.id,
        reason="Technical issue",
        db=test_db,
    )

    assert bet.status == BetStatus.REFUNDED

    # Verify wallet credited back
    wallet = test_db.query(Wallet).filter(Wallet.user_id == test_user.id).first()
    assert wallet.balance == initial_balance + Decimal("50.00")


def test_get_bet_history(test_user, test_db):
    """Test getting bet history."""
    # Place multiple bets
    for i in range(5):
        BetService.place_bet(
            user_id=test_user.id,
            bet_type=BetType.LUCKY_WHEEL,
            stake_amount=Decimal("10.00"),
            bet_data={"selected_number": i + 1},
            db=test_db,
        )

    # Get history
    bets = BetService.get_bet_history(
        user_id=test_user.id,
        db=test_db,
        limit=10,
    )

    assert len(bets) == 5
    assert all(bet.user_id == test_user.id for bet in bets)


def test_get_bet_statistics(test_user, test_db):
    """Test getting bet statistics."""
    # Place and settle some bets
    bet1 = BetService.place_bet(
        user_id=test_user.id,
        bet_type=BetType.LUCKY_WHEEL,
        stake_amount=Decimal("50.00"),
        bet_data={"selected_number": 7},
        db=test_db,
    )
    BetService.settle_bet(
        bet_id=bet1.id,
        game_result={"drawn_number": 7},
        is_win=True,
        multiplier=Decimal("10.0"),
        db=test_db,
    )

    bet2 = BetService.place_bet(
        user_id=test_user.id,
        bet_type=BetType.LUCKY_WHEEL,
        stake_amount=Decimal("50.00"),
        bet_data={"selected_number": 7},
        db=test_db,
    )
    BetService.settle_bet(
        bet_id=bet2.id,
        game_result={"drawn_number": 8},
        is_win=False,
        multiplier=Decimal("0.0"),
        db=test_db,
    )

    # Get statistics
    stats = BetService.get_bet_statistics(user_id=test_user.id, db=test_db)

    assert stats["total_bets"] == 2
    assert stats["total_wagered"] == 100.0
    assert stats["total_won"] == 500.0
    assert stats["win_count"] == 1
    assert stats["loss_count"] == 1
    assert stats["win_rate"] == 50.0
