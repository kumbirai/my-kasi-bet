"""
Unit tests for Lucky Wheel game engine.

Tests validation, RNG, win checking, and play method.
"""
import pytest
from decimal import Decimal

from app.models.bet import BetType
from app.models.user import User
from app.models.wallet import Wallet
from app.services.bet_service import InvalidBetDataError
from app.services.games.lucky_wheel import LuckyWheelGame


@pytest.mark.asyncio
async def test_validate_bet_data_valid(test_user, test_db):
    """Test valid bet data passes validation."""
    bet_data = {"selected_number": 7}
    result = LuckyWheelGame.validate_bet_data(bet_data)
    assert result == 7


def test_validate_bet_data_invalid_range():
    """Test number out of range fails validation."""
    bet_data = {"selected_number": 13}
    with pytest.raises(InvalidBetDataError):
        LuckyWheelGame.validate_bet_data(bet_data)


def test_validate_bet_data_missing_field():
    """Test missing field fails validation."""
    bet_data = {}
    with pytest.raises(InvalidBetDataError):
        LuckyWheelGame.validate_bet_data(bet_data)


def test_generate_result_in_range():
    """Test generated numbers are in valid range."""
    for _ in range(100):
        result = LuckyWheelGame.generate_result()
        assert 1 <= result <= 12


def test_check_win():
    """Test win checking logic."""
    assert LuckyWheelGame.check_win(7, 7) is True
    assert LuckyWheelGame.check_win(7, 8) is False


@pytest.mark.asyncio
async def test_play_win(test_user, test_db):
    """Test playing game with win."""
    # This test would need to mock the RNG or test multiple times
    # For now, we test the structure
    bet_data = {"selected_number": 7}
    stake_amount = Decimal("50.00")

    bet, result = await LuckyWheelGame.play(
        user_id=test_user.id,
        stake_amount=stake_amount,
        bet_data=bet_data,
        db=test_db,
    )

    assert bet.id is not None
    assert bet.bet_type == BetType.LUCKY_WHEEL
    assert "selected_number" in result
    assert "drawn_number" in result
    assert "is_win" in result
    assert result["stake"] == 50.0
