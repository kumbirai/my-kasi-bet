"""
Unit tests for Pick 3 game engine.

Tests validation, match counting, partial match rewards, and play method.
"""
import pytest
from decimal import Decimal

from app.models.bet import BetType
from app.models.user import User
from app.models.wallet import Wallet
from app.services.bet_service import InvalidBetDataError
from app.services.games.pick_3 import Pick3Game


def test_validate_bet_data_valid():
    """Test valid bet data passes validation."""
    bet_data = {"selected_numbers": [5, 12, 28]}
    result = Pick3Game.validate_bet_data(bet_data)
    assert result == [5, 12, 28]


def test_validate_bet_data_duplicates():
    """Test duplicate numbers fail validation."""
    bet_data = {"selected_numbers": [5, 5, 28]}
    with pytest.raises(InvalidBetDataError):
        Pick3Game.validate_bet_data(bet_data)


def test_validate_bet_data_wrong_count():
    """Test wrong number count fails validation."""
    bet_data = {"selected_numbers": [5, 12]}
    with pytest.raises(InvalidBetDataError):
        Pick3Game.validate_bet_data(bet_data)


def test_validate_bet_data_out_of_range():
    """Test numbers out of range fail validation."""
    bet_data = {"selected_numbers": [5, 12, 40]}
    with pytest.raises(InvalidBetDataError):
        Pick3Game.validate_bet_data(bet_data)


def test_generate_result_valid():
    """Test generated numbers are valid."""
    for _ in range(100):
        result = Pick3Game.generate_result()
        assert len(result) == 3
        assert len(set(result)) == 3  # All unique
        assert all(1 <= n <= 36 for n in result)


def test_check_matches():
    """Test match counting logic."""
    assert Pick3Game.check_matches([5, 12, 28], [5, 12, 28]) == 3
    assert Pick3Game.check_matches([5, 12, 28], [5, 12, 31]) == 2
    assert Pick3Game.check_matches([5, 12, 28], [5, 15, 31]) == 1
    assert Pick3Game.check_matches([5, 12, 28], [3, 15, 31]) == 0


def test_get_multiplier():
    """Test multiplier calculation."""
    assert Pick3Game.get_multiplier(3) == Decimal("800.0")
    assert Pick3Game.get_multiplier(2) == Decimal("10.0")
    assert Pick3Game.get_multiplier(1) == Decimal("2.0")
    assert Pick3Game.get_multiplier(0) == Decimal("0.0")


@pytest.mark.asyncio
async def test_play(test_user, test_db):
    """Test playing game."""
    bet_data = {"selected_numbers": [5, 12, 28]}
    stake_amount = Decimal("10.00")

    bet, result = await Pick3Game.play(
        user_id=test_user.id,
        stake_amount=stake_amount,
        bet_data=bet_data,
        db=test_db,
    )

    assert bet.id is not None
    assert bet.bet_type == BetType.PICK_3
    assert "selected_numbers" in result
    assert "drawn_numbers" in result
    assert "match_count" in result
    assert result["stake"] == 10.0
