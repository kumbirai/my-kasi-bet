"""
Withdrawal domain model.

This module defines the Withdrawal model representing withdrawal requests
with banking details and admin approval workflow.
"""
import enum
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    Column,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    func,
)
from sqlalchemy.orm import relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.admin import AdminUser
    from app.models.transaction import Transaction
    from app.models.user import User


class WithdrawalStatus(str, enum.Enum):
    """Withdrawal request status."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class WithdrawalMethod(str, enum.Enum):
    """Withdrawal methods."""

    BANK_TRANSFER = "bank_transfer"
    CASH_PICKUP = "cash_pickup"
    EWALLET = "ewallet"


class Withdrawal(Base):
    """
    Withdrawal model representing a withdrawal request.

    This model tracks withdrawal requests from users, including banking details,
    withdrawal method, and admin approval workflow. The wallet is debited
    immediately when the request is created.

    Attributes:
        id: Primary key identifier
        user_id: Foreign key to User
        amount: Withdrawal amount
        withdrawal_method: Withdrawal method
        bank_name: Bank name (for bank transfer)
        account_number: Account number
        account_holder: Account holder name
        status: Withdrawal status (pending, approved, rejected, cancelled)
        reviewed_by: Admin user ID who reviewed
        reviewed_at: Timestamp when reviewed
        rejection_reason: Reason for rejection (if rejected)
        debit_transaction_id: Link to Transaction when wallet debited
        refund_transaction_id: Link to Transaction if rejected and refunded
        payment_reference: External payment reference
        paid_at: Timestamp when payment was made
        notes: Additional notes
        created_at: Timestamp when withdrawal was created
        user: Relationship to User
        debit_transaction: Relationship to debit Transaction
        refund_transaction: Relationship to refund Transaction
    """

    __tablename__ = "withdrawals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Withdrawal details
    amount = Column(Numeric(10, 2), nullable=False)
    withdrawal_method = Column(SQLEnum(WithdrawalMethod), nullable=False)

    # Banking details (encrypted in production)
    bank_name = Column(String(100), nullable=True)
    account_number = Column(String(50), nullable=True)
    account_holder = Column(String(100), nullable=True)

    # Status and workflow
    status = Column(
        SQLEnum(WithdrawalStatus),
        default=WithdrawalStatus.PENDING,
        nullable=False,
        index=True,
    )

    # Admin review
    reviewed_by = Column(Integer, ForeignKey("admin_users.id"), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    rejection_reason = Column(String(200), nullable=True)

    # Transaction references
    debit_transaction_id = Column(
        Integer, ForeignKey("transactions.id"), nullable=True
    )  # Wallet debit
    refund_transaction_id = Column(
        Integer, ForeignKey("transactions.id"), nullable=True
    )  # If rejected

    # Payment tracking
    payment_reference = Column(String(100), nullable=True)  # External payment reference
    paid_at = Column(DateTime(timezone=True), nullable=True)

    # Metadata
    notes = Column(String(500), nullable=True)

    # Timestamps
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )

    # Relationships
    user = relationship("User", back_populates="withdrawals")
    debit_transaction = relationship("Transaction", foreign_keys=[debit_transaction_id])
    refund_transaction = relationship(
        "Transaction", foreign_keys=[refund_transaction_id]
    )

    def __repr__(self) -> str:
        """String representation of Withdrawal instance."""
        return (
            f"<Withdrawal(id={self.id}, user_id={self.user_id}, "
            f"amount={self.amount}, status={self.status})>"
        )
