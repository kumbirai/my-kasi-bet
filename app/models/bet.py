"""
Bet domain model.

This module defines the Bet model representing user bets on games.
"""
from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, Numeric, String, func
from sqlalchemy.orm import relationship
from sqlalchemy import Enum as SQLEnum

from app.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class BetStatus(str, Enum):
    """Bet status enumeration."""

    PENDING = "pending"
    WON = "won"
    LOST = "lost"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"


class BetType(str, Enum):
    """Bet type enumeration."""

    LUCKY_WHEEL = "lucky_wheel"
    COLOR_GAME = "color_game"
    PICK_3 = "pick_3"
    FOOTBALL_YESNO = "football_yesno"


class Bet(Base):
    """
    Bet model representing a user's bet on a game.

    This model provides a complete audit trail of all betting operations,
    including bet data, game results, and financial outcomes.

    Attributes:
        id: Primary key identifier
        user_id: Foreign key to User
        bet_type: Type of bet (lucky_wheel, color_game, pick_3, football_yesno)
        stake_amount: Amount wagered
        bet_data: JSON string with bet-specific data
        game_result: JSON string with game result data
        status: Bet status (pending, won, lost, refunded, cancelled)
        multiplier: Payout multiplier (e.g., 10.0 for lucky_wheel)
        payout_amount: Actual payout amount (stake * multiplier if won, 0 if lost)
        ip_address: User's IP address (for fraud detection)
        user_agent: User's user agent (for fraud detection)
        created_at: Timestamp when bet was created
        settled_at: Timestamp when bet was settled
        user: Relationship to User
    """

    __tablename__ = "bets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Bet details
    bet_type = Column(SQLEnum(BetType), nullable=False, index=True)
    stake_amount = Column(Numeric(10, 2), nullable=False)

    # Bet data (JSON string with bet-specific data)
    # Example: {"selected_number": 5} for lucky_wheel
    # Example: {"selected_color": "red"} for color_game
    # Example: {"selected_numbers": [5, 12, 28]} for pick_3
    # Example: {"match_id": 1, "choice": "yes"} for football_yesno
    bet_data = Column(String(500), nullable=False)

    # Game result (JSON string with result data)
    # Example: {"drawn_number": 5} for lucky_wheel
    # Example: {"drawn_color": "red"} for color_game
    # Example: {"drawn_numbers": [3, 15, 31], "match_count": 1} for pick_3
    # Example: {"match_result": "yes"} for football_yesno
    game_result = Column(String(500), nullable=True)

    # Outcome
    status = Column(
        SQLEnum(BetStatus), default=BetStatus.PENDING, nullable=False, index=True
    )
    multiplier = Column(Numeric(10, 2), nullable=True)  # Payout multiplier
    payout_amount = Column(
        Numeric(10, 2), default=Decimal("0.00"), nullable=False
    )  # Actual payout

    # Metadata
    ip_address = Column(String(50), nullable=True)  # For fraud detection
    user_agent = Column(String(200), nullable=True)  # For fraud detection

    # Timestamps
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )
    settled_at = Column(DateTime(timezone=True), nullable=True)  # When bet was settled

    # Relationships
    user = relationship("User", back_populates="bets")

    # Composite indexes for efficient queries
    __table_args__ = (
        Index("ix_bets_user_created", "user_id", "created_at"),
        Index("ix_bets_user_type", "user_id", "bet_type"),
        Index("ix_bets_status_created", "status", "created_at"),
    )

    def __repr__(self) -> str:
        """String representation of Bet instance."""
        return (
            f"<Bet(id={self.id}, user_id={self.user_id}, "
            f"type={self.bet_type}, stake={self.stake_amount}, status={self.status})>"
        )
