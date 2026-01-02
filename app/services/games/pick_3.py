"""
Pick 3 Numbers game engine.

This module implements the Pick 3 game where users select 3 unique numbers
from 1-36. If all 3 numbers match the drawn numbers (any order), they win
800x their stake. Partial matches also pay out (2 matches = 10x, 1 match = 2x).
"""
import secrets
import logging
from decimal import Decimal
from typing import Dict, Any, Tuple, List, Set
from sqlalchemy.orm import Session

from app.models.bet import Bet, BetType
from app.services.bet_service import BetService, InvalidBetDataError

logger = logging.getLogger(__name__)


class Pick3Game:
    """Pick 3 Numbers game - pick 3 unique numbers (1-36), win 800x for exact match"""

    JACKPOT_MULTIPLIER = Decimal("800.0")  # All 3 match
    TWO_MATCH_MULTIPLIER = Decimal("10.0")  # 2 numbers match (optional)
    ONE_MATCH_MULTIPLIER = Decimal("2.0")  # 1 number matches (optional)

    MIN_NUMBER = 1
    MAX_NUMBER = 36
    NUMBERS_TO_PICK = 3

    @staticmethod
    def validate_bet_data(bet_data: Dict[str, Any]) -> List[int]:
        """
        Validate bet data for Pick 3.

        Args:
            bet_data: Dict with 'selected_numbers' key (list of 3 integers)

        Returns:
            Sorted list of selected numbers

        Raises:
            InvalidBetDataError: If data is invalid
        """
        if "selected_numbers" not in bet_data:
            raise InvalidBetDataError("Missing 'selected_numbers' in bet data")

        selected_numbers = bet_data["selected_numbers"]

        if not isinstance(selected_numbers, list):
            raise InvalidBetDataError("'selected_numbers' must be a list")

        if len(selected_numbers) != Pick3Game.NUMBERS_TO_PICK:
            raise InvalidBetDataError(
                f"Must select exactly {Pick3Game.NUMBERS_TO_PICK} numbers"
            )

        # Check all are integers
        if not all(isinstance(n, int) for n in selected_numbers):
            raise InvalidBetDataError("All numbers must be integers")

        # Check range
        for num in selected_numbers:
            if num < Pick3Game.MIN_NUMBER or num > Pick3Game.MAX_NUMBER:
                raise InvalidBetDataError(
                    f"Numbers must be between {Pick3Game.MIN_NUMBER} and {Pick3Game.MAX_NUMBER}"
                )

        # Check uniqueness
        if len(selected_numbers) != len(set(selected_numbers)):
            raise InvalidBetDataError("Numbers must be unique (no duplicates)")

        return sorted(selected_numbers)

    @staticmethod
    def generate_result() -> List[int]:
        """
        Generate 3 unique random numbers (1-36) using cryptographically secure RNG.

        Returns:
            List of 3 unique random numbers, sorted
        """
        numbers: Set[int] = set()

        while len(numbers) < Pick3Game.NUMBERS_TO_PICK:
            num = secrets.randbelow(Pick3Game.MAX_NUMBER) + 1  # 1-36
            numbers.add(num)

        return sorted(list(numbers))

    @staticmethod
    def check_matches(selected_numbers: List[int], drawn_numbers: List[int]) -> int:
        """
        Check how many numbers match.

        Args:
            selected_numbers: User's selected numbers (sorted)
            drawn_numbers: Drawn numbers (sorted)

        Returns:
            Number of matches (0-3)
        """
        selected_set = set(selected_numbers)
        drawn_set = set(drawn_numbers)

        return len(selected_set.intersection(drawn_set))

    @staticmethod
    def get_multiplier(match_count: int, enable_partial_matches: bool = True) -> Decimal:
        """
        Get payout multiplier based on match count.

        Args:
            match_count: Number of matching numbers (0-3)
            enable_partial_matches: Whether to pay for partial matches

        Returns:
            Multiplier (Decimal)
        """
        if match_count == 3:
            return Pick3Game.JACKPOT_MULTIPLIER
        elif match_count == 2 and enable_partial_matches:
            return Pick3Game.TWO_MATCH_MULTIPLIER
        elif match_count == 1 and enable_partial_matches:
            return Pick3Game.ONE_MATCH_MULTIPLIER
        else:
            return Decimal("0.0")

    @staticmethod
    async def play(
        user_id: int,
        stake_amount: Decimal,
        bet_data: Dict[str, Any],
        db: Session,
        enable_partial_matches: bool = True,
    ) -> Tuple[Bet, Dict[str, Any]]:
        """
        Play Pick 3 game.

        This method:
        1. Validates bet data
        2. Places bet (debits wallet)
        3. Generates random result
        4. Checks matches
        5. Determines win/loss
        6. Settles bet (credits winnings if won)

        Args:
            user_id: User ID
            stake_amount: Bet amount
            bet_data: {"selected_numbers": [5, 12, 28]}
            db: Database session
            enable_partial_matches: Whether to pay for partial matches

        Returns:
            Tuple of (Bet object, result dict for WhatsApp message)
        """
        # Validate bet data
        selected_numbers = Pick3Game.validate_bet_data(bet_data)

        # Place bet
        bet = BetService.place_bet(
            user_id=user_id,
            bet_type=BetType.PICK_3,
            stake_amount=stake_amount,
            bet_data={"selected_numbers": selected_numbers},
            db=db,
        )

        # Generate result
        drawn_numbers = Pick3Game.generate_result()

        # Check matches
        match_count = Pick3Game.check_matches(selected_numbers, drawn_numbers)
        is_win = match_count > 0 if enable_partial_matches else match_count == 3

        # Get multiplier
        multiplier = Pick3Game.get_multiplier(match_count, enable_partial_matches)

        # Settle bet
        game_result = {
            "drawn_numbers": drawn_numbers,
            "match_count": match_count,
        }

        bet = BetService.settle_bet(
            bet_id=bet.id,
            game_result=game_result,
            is_win=is_win,
            multiplier=multiplier,
            db=db,
        )

        # Prepare result
        result = {
            "selected_numbers": selected_numbers,
            "drawn_numbers": drawn_numbers,
            "match_count": match_count,
            "is_win": is_win,
            "stake": float(stake_amount),
            "payout": float(bet.payout_amount) if is_win else 0,
            "multiplier": float(multiplier),
        }

        logger.info(
            f"Pick 3 played: user_id={user_id}, bet_id={bet.id}, "
            f"selected={selected_numbers}, drawn={drawn_numbers}, matches={match_count}"
        )

        return bet, result
