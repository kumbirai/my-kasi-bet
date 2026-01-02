"""
Lucky Wheel game engine.

This module implements the Lucky Wheel game where users bet on
a number from 1-12. If their number matches the drawn number,
they win 10x their stake.
"""
import secrets
import logging
from decimal import Decimal
from typing import Dict, Any, Tuple
from sqlalchemy.orm import Session

from app.models.bet import Bet, BetType
from app.services.bet_service import BetService, InvalidBetDataError

logger = logging.getLogger(__name__)


class LuckyWheelGame:
    """Lucky Wheel game engine - pick a number 1-12, win 10x"""

    MULTIPLIER = Decimal("10.0")
    MIN_NUMBER = 1
    MAX_NUMBER = 12

    @staticmethod
    def validate_bet_data(bet_data: Dict[str, Any]) -> int:
        """
        Validate bet data for Lucky Wheel.

        Args:
            bet_data: Dict with 'selected_number' key

        Returns:
            Selected number (1-12)

        Raises:
            InvalidBetDataError: If data is invalid
        """
        if "selected_number" not in bet_data:
            raise InvalidBetDataError("Missing 'selected_number' in bet data")

        selected_number = bet_data["selected_number"]

        if not isinstance(selected_number, int):
            raise InvalidBetDataError(
                f"Selected number must be an integer, got {type(selected_number)}"
            )

        if (
            selected_number < LuckyWheelGame.MIN_NUMBER
            or selected_number > LuckyWheelGame.MAX_NUMBER
        ):
            raise InvalidBetDataError(
                f"Number must be between {LuckyWheelGame.MIN_NUMBER} and {LuckyWheelGame.MAX_NUMBER}"
            )

        return selected_number

    @staticmethod
    def generate_result() -> int:
        """
        Generate random number (1-12) using cryptographically secure RNG.

        Returns:
            Random number between 1 and 12 (inclusive)
        """
        return secrets.randbelow(12) + 1  # 0-11 -> 1-12

    @staticmethod
    def check_win(selected_number: int, drawn_number: int) -> bool:
        """
        Check if user won.

        Args:
            selected_number: User's selected number
            drawn_number: Drawn number

        Returns:
            True if win, False otherwise
        """
        return selected_number == drawn_number

    @staticmethod
    async def play(
        user_id: int,
        stake_amount: Decimal,
        bet_data: Dict[str, Any],
        db: Session,
    ) -> Tuple[Bet, Dict[str, Any]]:
        """
        Play Lucky Wheel game.

        This method:
        1. Validates bet data
        2. Places bet (debits wallet)
        3. Generates random result
        4. Determines win/loss
        5. Settles bet (credits winnings if won)

        Args:
            user_id: User ID
            stake_amount: Bet amount
            bet_data: {"selected_number": 5}
            db: Database session

        Returns:
            Tuple of (Bet object, result dict for WhatsApp message)
        """
        # Validate bet data
        selected_number = LuckyWheelGame.validate_bet_data(bet_data)

        # Place bet (debit stake from wallet)
        bet = BetService.place_bet(
            user_id=user_id,
            bet_type=BetType.LUCKY_WHEEL,
            stake_amount=stake_amount,
            bet_data=bet_data,
            db=db,
        )

        # Generate result
        drawn_number = LuckyWheelGame.generate_result()

        # Check if win
        is_win = LuckyWheelGame.check_win(selected_number, drawn_number)

        # Settle bet
        game_result = {"drawn_number": drawn_number}
        multiplier = LuckyWheelGame.MULTIPLIER if is_win else Decimal("0.0")

        bet = BetService.settle_bet(
            bet_id=bet.id,
            game_result=game_result,
            is_win=is_win,
            multiplier=multiplier,
            db=db,
        )

        # Prepare result for WhatsApp
        result = {
            "selected_number": selected_number,
            "drawn_number": drawn_number,
            "is_win": is_win,
            "stake": float(stake_amount),
            "payout": float(bet.payout_amount) if is_win else 0,
            "multiplier": float(multiplier),
        }

        logger.info(
            f"Lucky Wheel played: user_id={user_id}, bet_id={bet.id}, "
            f"selected={selected_number}, drawn={drawn_number}, win={is_win}"
        )

        return bet, result
