"""
Transaction domain model.

This module defines the Transaction model representing all financial transactions
for audit and balance integrity verification.
"""
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, Numeric, String, func
from sqlalchemy.orm import relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class Transaction(Base):
    """
    Transaction model representing a financial transaction.

    This model provides a complete audit trail of all wallet operations,
    including balance snapshots before and after each transaction for
    integrity verification.

    Attributes:
        id: Primary key identifier
        user_id: Foreign key to User
        type: Transaction type (deposit, withdrawal, bet, win, refund)
        amount: Transaction amount (always positive)
        balance_before: Wallet balance before transaction
        balance_after: Wallet balance after transaction
        reference_type: Type of related entity (deposit_id, withdrawal_id, bet_id)
        reference_id: ID of related entity
        description: Human-readable description
        transaction_metadata: Additional data as JSON string
        created_at: Timestamp when transaction was created
        user: Relationship to User
    """

    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Transaction details
    type = Column(String(20), nullable=False, index=True)  # deposit, withdrawal, bet, win, refund
    amount = Column(Numeric(10, 2), nullable=False)

    # Balance snapshots for audit
    balance_before = Column(Numeric(10, 2), nullable=False)
    balance_after = Column(Numeric(10, 2), nullable=False)

    # Reference to related entity
    reference_type = Column(String(20), nullable=True)  # deposit_id, withdrawal_id, bet_id
    reference_id = Column(Integer, nullable=True)

    # Metadata
    description = Column(String(200), nullable=True)
    transaction_metadata = Column("metadata", String(500), nullable=True)  # JSON string for additional data

    # Timestamps
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )

    # Relationships
    user = relationship("User", back_populates="transactions")

    # Composite indexes for efficient queries
    __table_args__ = (
        Index("ix_user_created", "user_id", "created_at"),
        Index("ix_user_type", "user_id", "type"),
    )

    def __repr__(self) -> str:
        """String representation of Transaction instance."""
        return (
            f"<Transaction(id={self.id}, user_id={self.user_id}, "
            f"type={self.type}, amount={self.amount})>"
        )
