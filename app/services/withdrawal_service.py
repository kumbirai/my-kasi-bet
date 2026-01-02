"""
Withdrawal service for handling withdrawal requests and approvals.

This module provides business logic for withdrawal operations including
creation (with immediate wallet debit), approval, and rejection (with refund).
"""
import logging
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.withdrawal import Withdrawal, WithdrawalMethod, WithdrawalStatus
from app.services.wallet_service import InsufficientBalanceError, wallet_service
from app.services.whatsapp import whatsapp_service

logger = logging.getLogger(__name__)


class WithdrawalService:
    """Service for handling withdrawal requests and approvals."""

    # Withdrawal limits
    MIN_WITHDRAWAL = Decimal("50.00")
    MAX_WITHDRAWAL = Decimal("10000.00")
    DAILY_WITHDRAWAL_LIMIT = Decimal("20000.00")

    @staticmethod
    def create_withdrawal_request(
        user_id: int,
        amount: Decimal,
        withdrawal_method: WithdrawalMethod,
        bank_name: Optional[str],
        account_number: Optional[str],
        account_holder: Optional[str],
        notes: Optional[str],
        db: Session,
    ) -> Withdrawal:
        """
        Create a withdrawal request and immediately debit wallet.

        The wallet is debited when request is created (not when approved).
        If rejected, amount is refunded to wallet.

        Args:
            user_id: User ID
            amount: Withdrawal amount
            withdrawal_method: Withdrawal method
            bank_name: Bank name (for bank transfer)
            account_number: Account number
            account_holder: Account holder name
            notes: Additional notes
            db: Database session

        Returns:
            Created Withdrawal object

        Raises:
            ValueError: If amount is invalid or exceeds limits
            InsufficientBalanceError: If insufficient balance
        """
        # Validate amount
        if amount <= 0:
            raise ValueError(f"Withdrawal amount must be positive, got {amount}")

        if amount < WithdrawalService.MIN_WITHDRAWAL:
            raise ValueError(
                f"Minimum withdrawal is R{WithdrawalService.MIN_WITHDRAWAL}"
            )

        if amount > WithdrawalService.MAX_WITHDRAWAL:
            raise ValueError(
                f"Maximum withdrawal is R{WithdrawalService.MAX_WITHDRAWAL}"
            )

        # Check daily withdrawal limit
        daily_total = WithdrawalService._get_daily_withdrawal_total(user_id, db)
        if daily_total + amount > WithdrawalService.DAILY_WITHDRAWAL_LIMIT:
            remaining = WithdrawalService.DAILY_WITHDRAWAL_LIMIT - daily_total
            raise ValueError(
                f"Daily withdrawal limit exceeded. Remaining: R{remaining}"
            )

        # Debit wallet immediately
        transaction = wallet_service.debit(
            user_id=user_id,
            amount=amount,
            transaction_type="withdrawal",
            description=f"Withdrawal request #{user_id}-pending",
            db=db,
            reference_type="withdrawal",
            reference_id=None,  # Will update after withdrawal created
            metadata={"withdrawal_method": withdrawal_method.value},
        )

        # Create withdrawal request
        withdrawal = Withdrawal(
            user_id=user_id,
            amount=amount,
            withdrawal_method=withdrawal_method,
            bank_name=bank_name,
            account_number=account_number,
            account_holder=account_holder,
            notes=notes,
            status=WithdrawalStatus.PENDING,
            debit_transaction_id=transaction.id,
        )

        db.add(withdrawal)
        db.flush()

        # Update transaction reference
        transaction.reference_id = withdrawal.id
        transaction.description = f"Withdrawal request #{withdrawal.id}"

        logger.info(
            f"Withdrawal request created: withdrawal_id={withdrawal.id}, "
            f"user_id={user_id}, amount={amount}, "
            f"transaction_id={transaction.id}"
        )

        return withdrawal

    @staticmethod
    async def approve_withdrawal(
        withdrawal_id: int,
        admin_user_id: int,
        payment_reference: Optional[str],
        db: Session,
    ) -> Withdrawal:
        """
        Approve a withdrawal request.

        Wallet was already debited when request was created.
        This just marks it as approved and ready for payment.

        Args:
            withdrawal_id: Withdrawal ID to approve
            admin_user_id: Admin user ID approving
            payment_reference: External payment reference
            db: Database session

        Returns:
            Updated Withdrawal object
        """
        # Get withdrawal with lock
        withdrawal = (
            db.query(Withdrawal)
            .filter(Withdrawal.id == withdrawal_id)
            .with_for_update()
            .first()
        )

        if not withdrawal:
            raise ValueError(f"Withdrawal {withdrawal_id} not found")

        if withdrawal.status != WithdrawalStatus.PENDING:
            raise ValueError(
                f"Withdrawal {withdrawal_id} is not pending (status: {withdrawal.status})"
            )

        # Update withdrawal status
        withdrawal.status = WithdrawalStatus.APPROVED
        withdrawal.reviewed_by = admin_user_id
        withdrawal.reviewed_at = datetime.utcnow()
        withdrawal.payment_reference = payment_reference
        withdrawal.paid_at = datetime.utcnow()

        db.flush()

        logger.info(
            f"Withdrawal approved: withdrawal_id={withdrawal_id}, "
            f"user_id={withdrawal.user_id}, amount={withdrawal.amount}"
        )

        # Notify user via WhatsApp
        try:
            user = db.query(User).filter(User.id == withdrawal.user_id).first()
            if user:
                message = f"""✅ WITHDRAWAL APPROVED

Amount: R{float(withdrawal.amount):.2f}
Method: {withdrawal.withdrawal_method.value.replace('_', ' ').title()}
Reference: {payment_reference or 'Processing'}

Your withdrawal is being processed.
Funds will arrive within 24-48 hours.

Reply 'menu' for main menu."""

                await whatsapp_service.send_message(user.phone_number, message)
        except Exception as e:
            logger.error(f"Error sending withdrawal approval notification: {e}")

        return withdrawal

    @staticmethod
    async def reject_withdrawal(
        withdrawal_id: int,
        admin_user_id: int,
        rejection_reason: str,
        db: Session,
    ) -> Withdrawal:
        """
        Reject a withdrawal request and refund to wallet.

        Args:
            withdrawal_id: Withdrawal ID to reject
            admin_user_id: Admin user ID rejecting
            rejection_reason: Reason for rejection
            db: Database session

        Returns:
            Updated Withdrawal object
        """
        # Get withdrawal with lock
        withdrawal = (
            db.query(Withdrawal)
            .filter(Withdrawal.id == withdrawal_id)
            .with_for_update()
            .first()
        )

        if not withdrawal:
            raise ValueError(f"Withdrawal {withdrawal_id} not found")

        if withdrawal.status != WithdrawalStatus.PENDING:
            raise ValueError(
                f"Withdrawal {withdrawal_id} is not pending (status: {withdrawal.status})"
            )

        # Refund amount to wallet
        refund_transaction = wallet_service.credit(
            user_id=withdrawal.user_id,
            amount=withdrawal.amount,
            transaction_type="refund",
            description=f"Withdrawal #{withdrawal.id} rejected - refund",
            db=db,
            reference_type="withdrawal",
            reference_id=withdrawal.id,
            metadata={"reason": rejection_reason},
        )

        # Update withdrawal status
        withdrawal.status = WithdrawalStatus.REJECTED
        withdrawal.reviewed_by = admin_user_id
        withdrawal.reviewed_at = datetime.utcnow()
        withdrawal.rejection_reason = rejection_reason
        withdrawal.refund_transaction_id = refund_transaction.id

        db.flush()

        logger.info(
            f"Withdrawal rejected: withdrawal_id={withdrawal_id}, "
            f"user_id={withdrawal.user_id}, refunded={withdrawal.amount}"
        )

        # Notify user via WhatsApp
        try:
            user = db.query(User).filter(User.id == withdrawal.user_id).first()
            if user:
                message = f"""❌ WITHDRAWAL REJECTED

Amount: R{float(withdrawal.amount):.2f}
Reason: {rejection_reason}

Your funds have been refunded to your wallet.
New Balance: R{float(refund_transaction.balance_after):.2f}

Reply 'menu' for main menu."""

                await whatsapp_service.send_message(user.phone_number, message)
        except Exception as e:
            logger.error(f"Error sending withdrawal rejection notification: {e}")

        return withdrawal

    @staticmethod
    def _get_daily_withdrawal_total(user_id: int, db: Session) -> Decimal:
        """
        Get total withdrawal amount for user today.

        Args:
            user_id: User ID
            db: Database session

        Returns:
            Total withdrawal amount for today
        """
        today_start = datetime.combine(date.today(), datetime.min.time())

        total = (
            db.query(func.sum(Withdrawal.amount))
            .filter(
                Withdrawal.user_id == user_id,
                Withdrawal.created_at >= today_start,
                Withdrawal.status.in_(
                    [WithdrawalStatus.PENDING, WithdrawalStatus.APPROVED]
                ),
            )
            .scalar()
        )

        return total or Decimal("0.00")

    @staticmethod
    def get_pending_withdrawals(db: Session, limit: int = 50) -> List[Withdrawal]:
        """
        Get all pending withdrawal requests.

        Args:
            db: Database session
            limit: Maximum number of withdrawals to return

        Returns:
            List of pending Withdrawal objects
        """
        withdrawals = (
            db.query(Withdrawal)
            .filter(Withdrawal.status == WithdrawalStatus.PENDING)
            .order_by(desc(Withdrawal.created_at))
            .limit(limit)
            .all()
        )

        return withdrawals

    @staticmethod
    def get_user_withdrawals(
        user_id: int,
        db: Session,
        limit: int = 10,
        status: Optional[WithdrawalStatus] = None,
    ) -> List[Withdrawal]:
        """
        Get withdrawal history for a user.

        Args:
            user_id: User ID
            db: Database session
            limit: Maximum number of withdrawals to return
            status: Filter by status (optional)

        Returns:
            List of Withdrawal objects
        """
        query = db.query(Withdrawal).filter(Withdrawal.user_id == user_id)

        if status:
            query = query.filter(Withdrawal.status == status)

        withdrawals = query.order_by(desc(Withdrawal.created_at)).limit(limit).all()

        return withdrawals


# Export singleton instance
withdrawal_service = WithdrawalService()
