"""
Match domain model.

This module defines the Match model representing football matches
for the Football Yes/No betting game.
"""
from datetime import datetime
from decimal import Decimal
from enum import Enum

from sqlalchemy import Column, DateTime, Integer, Numeric, String, func
from sqlalchemy import Enum as SQLEnum

from app.database import Base


class MatchStatus(str, Enum):
    """Match status enumeration."""

    ACTIVE = "active"
    SETTLED = "settled"
    CANCELLED = "cancelled"


class MatchResult(str, Enum):
    """Match result enumeration."""

    YES = "yes"
    NO = "no"


class Match(Base):
    """
    Match model representing a football match for Yes/No betting.

    This model stores match information, odds, and settlement results
    for the Football Yes/No game.

    Attributes:
        id: Primary key identifier
        home_team: Home team name
        away_team: Away team name
        event_description: Question/event description (e.g., "Will Chiefs score first?")
        yes_odds: Odds for YES bet (e.g., 1.80)
        no_odds: Odds for NO bet (e.g., 2.10)
        status: Match status (active, settled, cancelled)
        result: Match result (yes, no) - set by admin when settling
        created_at: Timestamp when match was created
        match_time: Scheduled match time (optional)
        settled_at: Timestamp when match was settled
    """

    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)

    # Match details
    home_team = Column(String(100), nullable=False)
    away_team = Column(String(100), nullable=False)
    event_description = Column(String(200), nullable=False)  # "Will Chiefs score first?"

    # Odds
    yes_odds = Column(Numeric(5, 2), nullable=False)  # e.g., 1.80
    no_odds = Column(Numeric(5, 2), nullable=False)  # e.g., 2.10

    # Status and result
    status = Column(
        SQLEnum(MatchStatus), default=MatchStatus.ACTIVE, nullable=False, index=True
    )
    result = Column(SQLEnum(MatchResult), nullable=True)  # Set by admin when settling

    # Timestamps
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    match_time = Column(DateTime(timezone=True), nullable=True)  # Scheduled match time
    settled_at = Column(DateTime(timezone=True), nullable=True)  # When admin settled

    def __repr__(self) -> str:
        """String representation of Match instance."""
        return (
            f"<Match(id={self.id}, {self.home_team} vs {self.away_team}, "
            f"status={self.status})>"
        )
