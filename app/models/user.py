"""
User domain model.

This module defines the User model representing a betting platform user.
"""
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, DateTime, Integer, String, func
from sqlalchemy.orm import relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.wallet import Wallet


class User(Base):
    """
    User model representing a betting platform user.

    Attributes:
        id: Primary key identifier
        phone_number: Unique phone number (WhatsApp number)
        username: Optional username
        is_active: Whether the user account is active
        is_blocked: Whether the user account is blocked
        created_at: Timestamp when user was created
        last_active: Timestamp of last activity
        wallet: Relationship to user's wallet
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(20), unique=True, nullable=False, index=True)
    username = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_blocked = Column(Boolean, default=False, nullable=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    last_active = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    wallet = relationship(
        "Wallet",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    transactions = relationship(
        "Transaction",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    deposits = relationship(
        "Deposit",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    withdrawals = relationship(
        "Withdrawal",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    bets = relationship(
        "Bet",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        """String representation of User instance."""
        return (
            f"<User(id={self.id}, phone={self.phone_number}, "
            f"active={self.is_active}, blocked={self.is_blocked})>"
        )
