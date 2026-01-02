"""
Unit tests for Color Game engine.

Tests validation, RNG, win checking, and play method.
"""
import pytest
from decimal import Decimal

from app.models.bet import BetType
from app.models.user import User
from app.models.wallet import Wallet
from app.services.bet_service import InvalidBetDataError
from app.services.games.color_game import ColorGame


def test_validate_bet_data_valid():
    """Test valid bet data passes validation."""
    bet_data = {"selected_color": "red"}
    result = ColorGame.validate_bet_data(bet_data)
    assert result == "red"


def test_validate_bet_data_invalid_color():
    """Test invalid color fails validation."""
    bet_data = {"selected_color": "purple"}
    with pytest.raises(InvalidBetDataError):
        ColorGame.validate_bet_data(bet_data)


def test_generate_result_valid():
    """Test generated colors are valid."""
    valid_colors = ColorGame.VALID_COLORS
    for _ in range(100):
        result = ColorGame.generate_result()
        assert result in valid_colors


def test_check_win():
    """Test win checking logic."""
    assert ColorGame.check_win("red", "red") is True
    assert ColorGame.check_win("red", "green") is False
    assert ColorGame.check_win("RED", "red") is True  # Case insensitive


@pytest.mark.asyncio
async def test_play(test_user, test_db):
    """Test playing game."""
    bet_data = {"selected_color": "red"}
    stake_amount = Decimal("30.00")

    bet, result = await ColorGame.play(
        user_id=test_user.id,
        stake_amount=stake_amount,
        bet_data=bet_data,
        db=test_db,
    )

    assert bet.id is not None
    assert bet.bet_type == BetType.COLOR_GAME
    assert "selected_color" in result
    assert "drawn_color" in result
    assert result["stake"] == 30.0
