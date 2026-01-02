"""
Integration tests for game flows.

Tests complete game flows, concurrent betting, and balance integrity.
"""
import pytest
from decimal import Decimal

from app.models.bet import BetType, BetStatus
from app.models.user import User
from app.models.wallet import Wallet
from app.services.bet_service import BetService
from app.services.games.color_game import ColorGame
from app.services.games.lucky_wheel import LuckyWheelGame
from app.services.games.pick_3 import Pick3Game
from app.services.wallet_service import WalletService


@pytest.mark.asyncio
async def test_lucky_wheel_full_flow(test_user, test_db):
    """Test complete Lucky Wheel game flow."""
    initial_balance = Decimal("1000.00")

    bet, result = await LuckyWheelGame.play(
        user_id=test_user.id,
        stake_amount=Decimal("50.00"),
        bet_data={"selected_number": 7},
        db=test_db,
    )

    # Verify bet created
    assert bet.id is not None
    assert bet.bet_type == BetType.LUCKY_WHEEL
    assert bet.status in [BetStatus.WON, BetStatus.LOST]

    # Verify wallet balance updated correctly
    wallet = test_db.query(Wallet).filter(Wallet.user_id == test_user.id).first()
    if result["is_win"]:
        # Won: stake debited, payout credited
        expected = initial_balance - Decimal("50.00") + Decimal("500.00")
        assert wallet.balance == expected
    else:
        # Lost: only stake debited
        assert wallet.balance == initial_balance - Decimal("50.00")


@pytest.mark.asyncio
async def test_color_game_full_flow(test_user, test_db):
    """Test complete Color Game flow."""
    bet, result = await ColorGame.play(
        user_id=test_user.id,
        stake_amount=Decimal("30.00"),
        bet_data={"selected_color": "red"},
        db=test_db,
    )

    assert bet.id is not None
    assert bet.bet_type == BetType.COLOR_GAME
    assert bet.status in [BetStatus.WON, BetStatus.LOST]


@pytest.mark.asyncio
async def test_pick3_full_flow(test_user, test_db):
    """Test complete Pick 3 game flow."""
    bet, result = await Pick3Game.play(
        user_id=test_user.id,
        stake_amount=Decimal("10.00"),
        bet_data={"selected_numbers": [5, 12, 28]},
        db=test_db,
        enable_partial_matches=True,
    )

    assert bet.id is not None
    assert bet.bet_type == BetType.PICK_3
    assert bet.status in [BetStatus.WON, BetStatus.LOST]
    assert 0 <= result["match_count"] <= 3


def test_balance_integrity_after_multiple_bets(test_user, test_db):
    """Test balance integrity after multiple bets."""
    initial_balance = Decimal("1000.00")

    # Place multiple bets
    for i in range(5):
        BetService.place_bet(
            user_id=test_user.id,
            bet_type=BetType.LUCKY_WHEEL,
            stake_amount=Decimal("10.00"),
            bet_data={"selected_number": i + 1},
            db=test_db,
        )

    # Verify balance integrity
    is_valid = WalletService.verify_balance_integrity(test_user.id, test_db)
    assert is_valid is True

    # Verify balance matches expected
    wallet = test_db.query(Wallet).filter(Wallet.user_id == test_user.id).first()
    expected_balance = initial_balance - (Decimal("10.00") * 5)
    assert wallet.balance == expected_balance
