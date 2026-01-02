"""
Football Yes/No game engine.

This module implements the Football Yes/No game where admins create matches
with Yes/No questions and odds. Users bet on outcomes, and admins settle
matches after real-world events conclude.
"""
import asyncio
import json
import logging
from decimal import Decimal
from typing import Dict, Any, Tuple, List, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import SessionLocal
from app.models.bet import Bet, BetType, BetStatus
from app.models.match import Match, MatchStatus, MatchResult
from app.models.user import User
from app.models.wallet import Wallet
from app.services.bet_service import BetService, InvalidBetDataError
from app.services.whatsapp import whatsapp_service

logger = logging.getLogger(__name__)


class FootballYesNoGame:
    """Football Yes/No game - bet on match outcomes with variable odds"""

    @staticmethod
    def create_match(
        home_team: str,
        away_team: str,
        event_description: str,
        yes_odds: Decimal,
        no_odds: Decimal,
        match_time: Optional[datetime],
        db: Session,
    ) -> Match:
        """
        Create a new match (admin only).

        Args:
            home_team: Home team name
            away_team: Away team name
            event_description: Question/event (e.g., "Will Chiefs score first?")
            yes_odds: Odds for YES bet (e.g., 1.80)
            no_odds: Odds for NO bet (e.g., 2.10)
            match_time: Scheduled match time
            db: Database session

        Returns:
            Created Match object
        """
        if yes_odds <= 0 or no_odds <= 0:
            raise ValueError("Odds must be positive")

        match = Match(
            home_team=home_team,
            away_team=away_team,
            event_description=event_description,
            yes_odds=yes_odds,
            no_odds=no_odds,
            match_time=match_time,
            status=MatchStatus.ACTIVE,
        )

        db.add(match)
        db.commit()
        db.refresh(match)

        logger.info(
            f"Match created: {home_team} vs {away_team}, "
            f"event='{event_description}', yes_odds={yes_odds}, no_odds={no_odds}"
        )

        return match

    @staticmethod
    def get_active_matches(db: Session, limit: int = 10) -> List[Match]:
        """
        Get all active matches.

        Args:
            db: Database session
            limit: Maximum number of matches to return

        Returns:
            List of active Match objects
        """
        return (
            db.query(Match)
            .filter(Match.status == MatchStatus.ACTIVE)
            .order_by(Match.created_at.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def validate_bet_data(bet_data: Dict[str, Any], db: Session) -> Tuple[int, str, Decimal]:
        """
        Validate bet data for Football Yes/No.

        Args:
            bet_data: {"match_id": 1, "choice": "yes"}
            db: Database session

        Returns:
            Tuple of (match_id, choice, odds)

        Raises:
            InvalidBetDataError: If data is invalid
        """
        if "match_id" not in bet_data:
            raise InvalidBetDataError("Missing 'match_id' in bet data")

        if "choice" not in bet_data:
            raise InvalidBetDataError("Missing 'choice' in bet data")

        match_id = bet_data["match_id"]
        choice = bet_data["choice"].lower()

        if choice not in ["yes", "no"]:
            raise InvalidBetDataError("Choice must be 'yes' or 'no'")

        # Get match
        match = db.query(Match).filter(Match.id == match_id).first()

        if not match:
            raise InvalidBetDataError(f"Match {match_id} not found")

        if match.status != MatchStatus.ACTIVE:
            raise InvalidBetDataError(f"Match is {match.status}, betting closed")

        # Get odds
        odds = match.yes_odds if choice == "yes" else match.no_odds

        return match_id, choice, odds

    @staticmethod
    async def place_bet(
        user_id: int,
        stake_amount: Decimal,
        bet_data: Dict[str, Any],
        db: Session,
    ) -> Tuple[Bet, Dict[str, Any]]:
        """
        Place a Football Yes/No bet.

        Note: This does NOT settle the bet immediately.
        Bets remain PENDING until admin settles the match.

        Args:
            user_id: User ID
            stake_amount: Bet amount
            bet_data: {"match_id": 1, "choice": "yes"}
            db: Database session

        Returns:
            Tuple of (Bet object, result dict)
        """
        # Validate bet data
        match_id, choice, odds = FootballYesNoGame.validate_bet_data(bet_data, db)

        # Get match details
        match = db.query(Match).filter(Match.id == match_id).first()

        # Place bet (status will be PENDING)
        bet = BetService.place_bet(
            user_id=user_id,
            bet_type=BetType.FOOTBALL_YESNO,
            stake_amount=stake_amount,
            bet_data={
                "match_id": match_id,
                "choice": choice,
                "odds": float(odds),
            },
            db=db,
        )

        # Prepare result (bet is pending, not settled yet)
        result = {
            "match_id": match_id,
            "home_team": match.home_team,
            "away_team": match.away_team,
            "event_description": match.event_description,
            "choice": choice,
            "odds": float(odds),
            "stake": float(stake_amount),
            "potential_payout": float(stake_amount * odds),
            "status": "pending",
        }

        logger.info(
            f"Football bet placed: user_id={user_id}, bet_id={bet.id}, "
            f"match_id={match_id}, choice={choice}, odds={odds}"
        )

        return bet, result

    @staticmethod
    async def _notify_users_match_settled(
        match_id: int,
        match_home_team: str,
        match_away_team: str,
        result: MatchResult,
        user_bets: Dict[int, Dict[str, Any]],
    ) -> None:
        """
        Notify all users with active bets that the match has been settled.

        Args:
            match_id: Match ID
            match_home_team: Home team name
            match_away_team: Away team name
            result: Match result
            user_bets: Dictionary mapping user_id to bet info dict with:
                - bet_data: JSON string
                - status: BetStatus
                - stake_amount: Decimal
                - payout_amount: Decimal
        """
        # Create new database session for this thread
        db = SessionLocal()
        try:
            for user_id, bet_info in user_bets.items():
                try:
                    # Get user
                    user = db.query(User).filter(User.id == user_id).first()
                    if not user or user.is_blocked:
                        continue

                    # Get wallet balance
                    wallet = db.query(Wallet).filter(Wallet.user_id == user_id).first()
                    balance = wallet.balance if wallet else Decimal("0.00")

                    # Parse bet data
                    bet_data = json.loads(bet_info["bet_data"])
                    user_choice = bet_data.get("choice", "").upper()
                    stake = bet_info["stake_amount"]
                    bet_status = bet_info["status"]

                    # Build notification message
                    result_emoji = "✅" if bet_status == BetStatus.WON else "❌"
                    result_text = result.value.upper()

                    if bet_status == BetStatus.WON:
                        payout = bet_info["payout_amount"]
                        message = (
                            f"⚽ MATCH SETTLED\n\n"
                            f"{match_home_team} vs {match_away_team}\n"
                            f"Result: {result_text} {result_emoji}\n\n"
                            f"Your bet: {user_choice} - R{float(stake):.2f}\n"
                            f"🎉 You won R{float(payout):.2f}!\n"
                            f"💰 Balance: R{float(balance):.2f}"
                        )
                    else:
                        message = (
                            f"⚽ MATCH SETTLED\n\n"
                            f"{match_home_team} vs {match_away_team}\n"
                            f"Result: {result_text} {result_emoji}\n\n"
                            f"Your bet: {user_choice} - R{float(stake):.2f}\n"
                            f"❌ You lost\n"
                            f"💰 Balance: R{float(balance):.2f}"
                        )

                    # Send notification
                    await whatsapp_service.send_message(
                        to=user.phone_number,
                        message=message,
                    )

                    logger.info(
                        f"Notification sent to user {user_id} for match {match_id}"
                    )

                except Exception as e:
                    logger.error(
                        f"Error sending notification to user {user_id} for match {match_id}: {e}",
                        exc_info=True,
                    )
                    # Continue with other users even if one fails
        finally:
            db.close()

    @staticmethod
    def settle_match(
        match_id: int,
        result: MatchResult,
        db: Session,
    ) -> List[Bet]:
        """
        Settle a match and all associated bets (admin only).

        All users with active bets on this match will be notified via WhatsApp.

        Args:
            match_id: Match ID to settle
            result: Match result (YES or NO)
            db: Database session

        Returns:
            List of settled Bet objects
        """
        # Get match
        match = db.query(Match).filter(Match.id == match_id).first()

        if not match:
            raise ValueError(f"Match {match_id} not found")

        if match.status != MatchStatus.ACTIVE:
            raise ValueError(f"Match is already {match.status}")

        # Update match
        match.result = result
        match.status = MatchStatus.SETTLED
        match.settled_at = datetime.utcnow()

        # Get all pending bets for this match
        pending_bets = (
            db.query(Bet)
            .filter(
                Bet.bet_type == BetType.FOOTBALL_YESNO,
                Bet.status == BetStatus.PENDING,
            )
            .all()
        )

        settled_bets = []
        user_bets: Dict[int, Dict[str, Any]] = {}  # Track bet info per user for notification

        for bet in pending_bets:
            bet_data = json.loads(bet.bet_data)

            # Check if this bet is for this match
            if bet_data.get("match_id") != match_id:
                continue

            # Check if bet won
            user_choice = bet_data.get("choice")
            is_win = user_choice == result.value

            # Get odds
            odds = Decimal(str(bet_data.get("odds", 0)))
            multiplier = odds if is_win else Decimal("0.0")

            # Settle bet
            game_result = {
                "match_result": result.value,
                "match_id": match_id,
            }

            settled_bet = BetService.settle_bet(
                bet_id=bet.id,
                game_result=game_result,
                is_win=is_win,
                multiplier=multiplier,
                db=db,
            )

            settled_bets.append(settled_bet)

            # Track user for notification (one bet per user)
            # Store bet info needed for notification
            if bet.user_id not in user_bets:
                user_bets[bet.user_id] = {
                    "bet_data": bet.bet_data,
                    "status": settled_bet.status,
                    "stake_amount": settled_bet.stake_amount,
                    "payout_amount": settled_bet.payout_amount,
                }

        db.commit()

        logger.info(
            f"Match settled: match_id={match_id}, result={result.value}, "
            f"settled_bets={len(settled_bets)}, users_to_notify={len(user_bets)}"
        )

        # Notify all users with active bets (fire-and-forget)
        if user_bets:
            try:
                # Run notifications in a background thread to avoid blocking
                # and to handle async operations from sync context
                def run_notifications():
                    try:
                        # Create new event loop for this thread
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        loop.run_until_complete(
                            FootballYesNoGame._notify_users_match_settled(
                                match_id=match_id,
                                match_home_team=match.home_team,
                                match_away_team=match.away_team,
                                result=result,
                                user_bets=user_bets,
                            )
                        )
                    except Exception as e:
                        logger.error(
                            f"Error in notification thread for match {match_id}: {e}",
                            exc_info=True,
                        )
                    finally:
                        loop.close()

                import threading

                thread = threading.Thread(target=run_notifications, daemon=True)
                thread.start()

            except Exception as e:
                logger.error(
                    f"Error starting notification thread for match {match_id}: {e}",
                    exc_info=True,
                )

        return settled_bets
