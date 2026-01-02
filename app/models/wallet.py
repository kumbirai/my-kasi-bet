"""
Wallet domain model.

This module defines the Wallet model representing a user's wallet balance.
"""
from decimal import Decimal

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, func
from sqlalchemy.orm import relationship

from app.database import Base


class Wallet(Base):
    """
    Wallet model representing a user's wallet balance.

    Attributes:
        id: Primary key identifier
        user_id: Foreign key to User
        balance: Current wallet balance (Decimal for precision)
        updated_at: Timestamp when wallet was last updated
        user: Relationship to User
    """

    __tablename__ = "wallets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    balance = Column(
        Numeric(10, 2), default=Decimal("0.00"), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    user = relationship("User", back_populates="wallet")

    def __repr__(self) -> str:
        """String representation of Wallet instance."""
        return f"<Wallet(user_id={self.user_id}, balance={self.balance})>"
