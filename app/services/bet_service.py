"""
Betting service for handling all betting operations.

This module provides atomic betting operations with complete audit trails
and financial integrity guarantees. All bet placements and settlements
MUST use this service to ensure proper financial handling.
"""
import json
import logging
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from sqlalchemy import and_, desc, func
from sqlalchemy.orm import Session

from app.models.bet import Bet, BetStatus, BetType
from app.services.wallet_service import InsufficientBalanceError, WalletService

logger = logging.getLogger(__name__)


class BettingError(Exception):
    """Base exception for betting errors."""

    pass


class InvalidBetAmountError(BettingError):
    """Raised when bet amount is invalid."""

    pass


class InvalidBetDataError(BettingError):
    """Raised when bet data is invalid."""

    pass


class BetService:
    """
    Service for handling all betting operations.

    All bet placements and settlements MUST use this service
    to ensure proper financial handling and audit trails.
    """

    # Bet limits per game (min, max)
    BET_LIMITS = {
        BetType.LUCKY_WHEEL: (Decimal("5.00"), Decimal("500.00")),
        BetType.COLOR_GAME: (Decimal("5.00"), Decimal("500.00")),
        BetType.PICK_3: (Decimal("2.00"), Decimal("100.00")),
        BetType.FOOTBALL_YESNO: (Decimal("10.00"), Decimal("1000.00")),
    }

    # User-friendly game names for error messages
    GAME_NAMES = {
        BetType.LUCKY_WHEEL: "Lucky Wheel",
        BetType.COLOR_GAME: "Color Game",
        BetType.PICK_3: "Pick 3",
        BetType.FOOTBALL_YESNO: "Football Yes/No",
    }

    @staticmethod
    def get_game_name(bet_type: BetType) -> str:
        """
        Get user-friendly name for a bet type.

        Args:
            bet_type: The bet type enum

        Returns:
            User-friendly game name
        """
        return BetService.GAME_NAMES.get(bet_type, str(bet_type))

    @staticmethod
    def place_bet(
        user_id: int,
        bet_type: BetType,
        stake_amount: Decimal,
        bet_data: Dict[str, Any],
        db: Session,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Bet:
        """
        Place a bet for a user.

        This operation:
        1. Validates bet amount is within limits
        2. Validates user has sufficient balance
        3. Creates bet record
        4. Debits stake from wallet (atomic transaction)

        Args:
            user_id: User ID
            bet_type: Type of bet (lucky_wheel, color_game, etc.)
            stake_amount: Amount to bet
            bet_data: Bet-specific data as dict
            db: Database session
            ip_address: User's IP address (for fraud detection)
            user_agent: User's user agent (for fraud detection)

        Returns:
            Created Bet object

        Raises:
            InvalidBetAmountError: If stake is invalid
            InsufficientBalanceError: If user has insufficient balance
        """
        try:
            # Validate bet amount
            min_bet, max_bet = BetService.BET_LIMITS.get(
                bet_type, (Decimal("1.00"), Decimal("10000.00"))
            )

            if stake_amount < min_bet:
                game_name = BetService.get_game_name(bet_type)
                raise InvalidBetAmountError(
                    f"Minimum bet for {game_name} is R{min_bet}"
                )

            if stake_amount > max_bet:
                game_name = BetService.get_game_name(bet_type)
                raise InvalidBetAmountError(
                    f"Maximum bet for {game_name} is R{max_bet}"
                )

            # Create bet record (status=PENDING)
            bet = Bet(
                user_id=user_id,
                bet_type=bet_type,
                stake_amount=stake_amount,
                bet_data=json.dumps(bet_data),
                status=BetStatus.PENDING,
                ip_address=ip_address,
                user_agent=user_agent,
            )

            db.add(bet)
            db.flush()  # Get bet.id before committing

            # Debit stake from wallet (this will raise InsufficientBalanceError if not enough balance)
            WalletService.debit(
                user_id=user_id,
                amount=stake_amount,
                transaction_type="bet",
                description=f"Bet placed: {bet_type} (Bet #{bet.id})",
                db=db,
                reference_type="bet",
                reference_id=bet.id,
                metadata=bet_data,
            )

            # Commit transaction (bet + wallet debit are atomic)
            db.commit()
            db.refresh(bet)

            logger.info(
                f"Bet placed: user_id={user_id}, bet_id={bet.id}, "
                f"type={bet_type}, stake={stake_amount}"
            )

            return bet

        except InsufficientBalanceError:
            db.rollback()
            raise
        except InvalidBetAmountError:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Error placing bet: {e}", exc_info=True)
            raise BettingError(f"Failed to place bet: {str(e)}")

    @staticmethod
    def settle_bet(
        bet_id: int,
        game_result: Dict[str, Any],
        is_win: bool,
        multiplier: Decimal,
        db: Session,
    ) -> Bet:
        """
        Settle a bet (mark as won or lost).

        This operation:
        1. Updates bet record with game result
        2. If win: credits payout to wallet
        3. Marks bet as settled

        Args:
            bet_id: Bet ID to settle
            game_result: Game result data as dict
            is_win: Whether the bet won
            multiplier: Payout multiplier (e.g., 10.0 for lucky_wheel)
            db: Database session

        Returns:
            Updated Bet object

        Raises:
            BettingError: If bet cannot be settled
        """
        try:
            # Get bet with row lock
            bet = db.query(Bet).filter(Bet.id == bet_id).with_for_update().first()

            if not bet:
                raise BettingError(f"Bet {bet_id} not found")

            if bet.status != BetStatus.PENDING:
                raise BettingError(
                    f"Bet {bet_id} is already settled (status: {bet.status})"
                )

            # Update bet record
            bet.game_result = json.dumps(game_result)
            bet.multiplier = multiplier
            bet.settled_at = datetime.utcnow()

            if is_win:
                # Calculate payout
                payout = bet.stake_amount * multiplier
                bet.payout_amount = payout
                bet.status = BetStatus.WON

                # Credit payout to wallet
                WalletService.credit(
                    user_id=bet.user_id,
                    amount=payout,
                    transaction_type="win",
                    description=f"Bet won: {bet.bet_type} (Bet #{bet.id})",
                    db=db,
                    reference_type="bet",
                    reference_id=bet.id,
                    metadata=game_result,
                )

                logger.info(
                    f"Bet won: bet_id={bet.id}, user_id={bet.user_id}, "
                    f"stake={bet.stake_amount}, payout={payout}, multiplier={multiplier}"
                )
            else:
                # Bet lost - no payout
                bet.payout_amount = Decimal("0.00")
                bet.status = BetStatus.LOST

                logger.info(
                    f"Bet lost: bet_id={bet.id}, user_id={bet.user_id}, "
                    f"stake={bet.stake_amount}"
                )

            # Commit transaction
            db.commit()
            db.refresh(bet)

            return bet

        except BettingError:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Error settling bet: {e}", exc_info=True)
            raise BettingError(f"Failed to settle bet: {str(e)}")

    @staticmethod
    def refund_bet(bet_id: int, reason: str, db: Session) -> Bet:
        """
        Refund a bet (return stake to user).

        This operation:
        1. Marks bet as refunded
        2. Credits stake back to wallet

        Args:
            bet_id: Bet ID to refund
            reason: Reason for refund
            db: Database session

        Returns:
            Updated Bet object
        """
        try:
            # Get bet with row lock
            bet = db.query(Bet).filter(Bet.id == bet_id).with_for_update().first()

            if not bet:
                raise BettingError(f"Bet {bet_id} not found")

            if bet.status != BetStatus.PENDING:
                raise BettingError(
                    f"Can only refund pending bets (current status: {bet.status})"
                )

            # Update bet status
            bet.status = BetStatus.REFUNDED
            bet.settled_at = datetime.utcnow()
            bet.game_result = json.dumps({"refund_reason": reason})

            # Credit stake back to wallet
            WalletService.credit(
                user_id=bet.user_id,
                amount=bet.stake_amount,
                transaction_type="refund",
                description=f"Bet refunded: {reason} (Bet #{bet.id})",
                db=db,
                reference_type="bet",
                reference_id=bet.id,
                metadata={"refund_reason": reason},
            )

            logger.info(
                f"Bet refunded: bet_id={bet.id}, user_id={bet.user_id}, "
                f"stake={bet.stake_amount}, reason={reason}"
            )

            db.commit()
            db.refresh(bet)

            return bet

        except BettingError:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Error refunding bet: {e}", exc_info=True)
            raise BettingError(f"Failed to refund bet: {str(e)}")

    @staticmethod
    def get_bet_history(
        user_id: int,
        db: Session,
        limit: int = 10,
        offset: int = 0,
        bet_type: Optional[BetType] = None,
        status: Optional[BetStatus] = None,
    ) -> List[Bet]:
        """
        Get bet history for a user.

        Args:
            user_id: User ID
            db: Database session
            limit: Maximum number of bets to return
            offset: Number of bets to skip
            bet_type: Filter by bet type (optional)
            status: Filter by status (optional)

        Returns:
            List of Bet objects, ordered by created_at desc
        """
        query = db.query(Bet).filter(Bet.user_id == user_id)

        if bet_type:
            query = query.filter(Bet.bet_type == bet_type)

        if status:
            query = query.filter(Bet.status == status)

        bets = query.order_by(desc(Bet.created_at)).limit(limit).offset(offset).all()

        return bets

    @staticmethod
    def get_bet_statistics(user_id: int, db: Session) -> Dict[str, Any]:
        """
        Get betting statistics for a user.

        Args:
            user_id: User ID
            db: Database session

        Returns:
            Dict with statistics
        """
        # Total bets
        total_bets = (
            db.query(func.count(Bet.id)).filter(Bet.user_id == user_id).scalar()
        )

        # Total wagered
        total_wagered = (
            db.query(func.sum(Bet.stake_amount))
            .filter(Bet.user_id == user_id)
            .scalar()
            or Decimal("0.00")
        )

        # Total won
        total_won = (
            db.query(func.sum(Bet.payout_amount))
            .filter(and_(Bet.user_id == user_id, Bet.status == BetStatus.WON))
            .scalar()
            or Decimal("0.00")
        )

        # Win count
        win_count = (
            db.query(func.count(Bet.id))
            .filter(and_(Bet.user_id == user_id, Bet.status == BetStatus.WON))
            .scalar()
        )

        # Loss count
        loss_count = (
            db.query(func.count(Bet.id))
            .filter(and_(Bet.user_id == user_id, Bet.status == BetStatus.LOST))
            .scalar()
        )

        # Win rate
        win_rate = (win_count / total_bets * 100) if total_bets > 0 else 0

        # Net profit/loss
        net_profit = total_won - total_wagered

        return {
            "total_bets": total_bets,
            "total_wagered": float(total_wagered),
            "total_won": float(total_won),
            "win_count": win_count,
            "loss_count": loss_count,
            "win_rate": round(win_rate, 2),
            "net_profit": float(net_profit),
        }
