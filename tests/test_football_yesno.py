"""
Unit tests for Football Yes/No game engine.

Tests match creation, bet placement, and match settlement.
"""
import pytest
from decimal import Decimal
from datetime import datetime

from app.models.bet import BetType, BetStatus
from app.models.match import Match, MatchStatus, MatchResult
from app.models.user import User
from app.models.wallet import Wallet
from app.services.bet_service import InvalidBetDataError
from app.services.games.football_yesno import FootballYesNoGame


def test_create_match(test_db):
    """Test creating a match."""
    match = FootballYesNoGame.create_match(
        home_team="Chiefs",
        away_team="Pirates",
        event_description="Will Chiefs score first?",
        yes_odds=Decimal("1.80"),
        no_odds=Decimal("2.10"),
        match_time=None,
        db=test_db,
    )

    assert match.id is not None
    assert match.status == MatchStatus.ACTIVE
    assert match.home_team == "Chiefs"
    assert match.away_team == "Pirates"


def test_get_active_matches(test_db):
    """Test getting active matches."""
    # Create matches
    match1 = FootballYesNoGame.create_match(
        home_team="Team A",
        away_team="Team B",
        event_description="Test event",
        yes_odds=Decimal("1.50"),
        no_odds=Decimal("2.50"),
        match_time=None,
        db=test_db,
    )

    matches = FootballYesNoGame.get_active_matches(test_db)
    assert len(matches) >= 1
    assert any(m.id == match1.id for m in matches)


def test_validate_bet_data_valid(test_user, test_db):
    """Test valid bet data passes validation."""
    # Create match
    match = FootballYesNoGame.create_match(
        home_team="Chiefs",
        away_team="Pirates",
        event_description="Will Chiefs score first?",
        yes_odds=Decimal("1.80"),
        no_odds=Decimal("2.10"),
        match_time=None,
        db=test_db,
    )

    bet_data = {"match_id": match.id, "choice": "yes"}
    match_id, choice, odds = FootballYesNoGame.validate_bet_data(bet_data, test_db)

    assert match_id == match.id
    assert choice == "yes"
    assert odds == Decimal("1.80")


def test_validate_bet_data_invalid_match(test_user, test_db):
    """Test invalid match ID fails validation."""
    bet_data = {"match_id": 99999, "choice": "yes"}
    with pytest.raises(InvalidBetDataError):
        FootballYesNoGame.validate_bet_data(bet_data, test_db)


@pytest.mark.asyncio
async def test_place_bet(test_user, test_db):
    """Test placing a bet."""
    # Create match
    match = FootballYesNoGame.create_match(
        home_team="Chiefs",
        away_team="Pirates",
        event_description="Will Chiefs score first?",
        yes_odds=Decimal("1.80"),
        no_odds=Decimal("2.10"),
        match_time=None,
        db=test_db,
    )

    bet, result = await FootballYesNoGame.place_bet(
        user_id=test_user.id,
        stake_amount=Decimal("100.00"),
        bet_data={"match_id": match.id, "choice": "yes"},
        db=test_db,
    )

    assert bet.id is not None
    assert bet.bet_type == BetType.FOOTBALL_YESNO
    assert bet.status == BetStatus.PENDING
    assert result["status"] == "pending"
    assert result["potential_payout"] == 180.0  # 100 * 1.80


def test_settle_match(test_user, test_db):
    """Test settling a match."""
    # Create match
    match = FootballYesNoGame.create_match(
        home_team="Chiefs",
        away_team="Pirates",
        event_description="Will Chiefs score first?",
        yes_odds=Decimal("1.80"),
        no_odds=Decimal("2.10"),
        match_time=None,
        db=test_db,
    )

    # Place bets
    import asyncio

    bet1 = asyncio.run(
        FootballYesNoGame.place_bet(
            user_id=test_user.id,
            stake_amount=Decimal("100.00"),
            bet_data={"match_id": match.id, "choice": "yes"},
            db=test_db,
        )
    )[0]

    # Settle match
    settled_bets = FootballYesNoGame.settle_match(
        match_id=match.id,
        result=MatchResult.YES,
        db=test_db,
    )

    assert len(settled_bets) == 1
    assert settled_bets[0].status == BetStatus.WON

    # Verify match is settled
    test_db.refresh(match)
    assert match.status == MatchStatus.SETTLED
    assert match.result == MatchResult.YES
