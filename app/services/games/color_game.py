"""
Color Game engine.

This module implements the Color Game where users bet on
one of 4 colors (Red, Green, Blue, Yellow). If their color
matches the drawn color, they win 3x their stake.
"""
import secrets
import logging
from decimal import Decimal
from typing import Dict, Any, Tuple
from enum import Enum
from sqlalchemy.orm import Session

from app.models.bet import Bet, BetType
from app.services.bet_service import BetService, InvalidBetDataError

logger = logging.getLogger(__name__)


class Color(str, Enum):
    """Color enumeration."""

    RED = "red"
    GREEN = "green"
    BLUE = "blue"
    YELLOW = "yellow"


class ColorGame:
    """Color Game engine - pick a color, win 3x"""

    MULTIPLIER = Decimal("3.0")
    VALID_COLORS = ["red", "green", "blue", "yellow"]

    COLOR_EMOJIS = {
        "red": "🔴",
        "green": "🟢",
        "blue": "🔵",
        "yellow": "🟡",
    }

    @staticmethod
    def validate_bet_data(bet_data: Dict[str, Any]) -> str:
        """
        Validate bet data for Color Game.

        Args:
            bet_data: Dict with 'selected_color' key

        Returns:
            Selected color (normalized to lowercase)

        Raises:
            InvalidBetDataError: If data is invalid
        """
        if "selected_color" not in bet_data:
            raise InvalidBetDataError("Missing 'selected_color' in bet data")

        selected_color = bet_data["selected_color"].lower()

        if selected_color not in ColorGame.VALID_COLORS:
            raise InvalidBetDataError(
                f"Invalid color. Must be one of: {', '.join(ColorGame.VALID_COLORS)}"
            )

        return selected_color

    @staticmethod
    def generate_result() -> str:
        """
        Generate random color using cryptographically secure RNG.

        Returns:
            Random color string
        """
        index = secrets.randbelow(4)  # 0-3
        return ColorGame.VALID_COLORS[index]

    @staticmethod
    def check_win(selected_color: str, drawn_color: str) -> bool:
        """
        Check if user won.

        Args:
            selected_color: User's selected color
            drawn_color: Drawn color

        Returns:
            True if win, False otherwise
        """
        return selected_color.lower() == drawn_color.lower()

    @staticmethod
    async def play(
        user_id: int,
        stake_amount: Decimal,
        bet_data: Dict[str, Any],
        db: Session,
    ) -> Tuple[Bet, Dict[str, Any]]:
        """
        Play Color Game.

        This method:
        1. Validates bet data
        2. Places bet (debits wallet)
        3. Generates random result
        4. Determines win/loss
        5. Settles bet (credits winnings if won)

        Args:
            user_id: User ID
            stake_amount: Bet amount
            bet_data: {"selected_color": "red"}
            db: Database session

        Returns:
            Tuple of (Bet object, result dict for WhatsApp message)
        """
        # Validate bet data
        selected_color = ColorGame.validate_bet_data(bet_data)

        # Place bet
        bet = BetService.place_bet(
            user_id=user_id,
            bet_type=BetType.COLOR_GAME,
            stake_amount=stake_amount,
            bet_data={"selected_color": selected_color},
            db=db,
        )

        # Generate result
        drawn_color = ColorGame.generate_result()

        # Check if win
        is_win = ColorGame.check_win(selected_color, drawn_color)

        # Settle bet
        game_result = {"drawn_color": drawn_color}
        multiplier = ColorGame.MULTIPLIER if is_win else Decimal("0.0")

        bet = BetService.settle_bet(
            bet_id=bet.id,
            game_result=game_result,
            is_win=is_win,
            multiplier=multiplier,
            db=db,
        )

        # Prepare result
        result = {
            "selected_color": selected_color,
            "drawn_color": drawn_color,
            "is_win": is_win,
            "stake": float(stake_amount),
            "payout": float(bet.payout_amount) if is_win else 0,
            "multiplier": float(multiplier),
        }

        logger.info(
            f"Color Game played: user_id={user_id}, bet_id={bet.id}, "
            f"selected={selected_color}, drawn={drawn_color}, win={is_win}"
        )

        return bet, result
