"""
Deposit domain model.

This module defines the Deposit model representing deposit requests
with payment method support and admin approval workflow.
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


class DepositStatus(str, enum.Enum):
    """Deposit request status."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


class PaymentMethod(str, enum.Enum):
    """Supported payment methods."""

    VOUCHER_1 = "1voucher"
    SNAPSCAN = "snapscan"
    CAPITEC = "capitec"
    BANK_TRANSFER = "bank_transfer"
    OTHER = "other"


class Deposit(Base):
    """
    Deposit model representing a deposit request.

    This model tracks deposit requests from users, including payment method,
    proof of payment, and admin approval workflow.

    Attributes:
        id: Primary key identifier
        user_id: Foreign key to User
        amount: Deposit amount
        payment_method: Payment method used
        proof_type: Type of proof (reference_number, image_url)
        proof_value: The actual reference or URL
        status: Deposit status (pending, approved, rejected, expired)
        reviewed_by: Admin user ID who reviewed
        reviewed_at: Timestamp when reviewed
        rejection_reason: Reason for rejection (if rejected)
        transaction_id: Link to Transaction when approved
        notes: Additional notes
        created_at: Timestamp when deposit was created
        expires_at: Optional expiry for pending deposits
        user: Relationship to User
        transaction: Relationship to Transaction
    """

    __tablename__ = "deposits"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Deposit details
    amount = Column(Numeric(10, 2), nullable=False)
    payment_method = Column(SQLEnum(PaymentMethod), nullable=False)

    # Proof of payment
    proof_type = Column(String(20), nullable=True)  # reference_number, image_url
    proof_value = Column(String(500), nullable=True)  # The actual reference or URL

    # Status and workflow
    status = Column(
        SQLEnum(DepositStatus),
        default=DepositStatus.PENDING,
        nullable=False,
        index=True,
    )

    # Admin review
    reviewed_by = Column(Integer, ForeignKey("admin_users.id"), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    rejection_reason = Column(String(200), nullable=True)

    # Transaction reference
    transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=True)

    # Metadata
    notes = Column(String(500), nullable=True)

    # Timestamps
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )
    expires_at = Column(
        DateTime(timezone=True), nullable=True
    )  # Optional expiry for pending deposits

    # Relationships
    user = relationship("User", back_populates="deposits")
    transaction = relationship("Transaction", foreign_keys=[transaction_id])

    def __repr__(self) -> str:
        """String representation of Deposit instance."""
        return (
            f"<Deposit(id={self.id}, user_id={self.user_id}, "
            f"amount={self.amount}, status={self.status})>"
        )
