"""
Deposit service for handling deposit requests and approvals.

This module provides business logic for deposit operations including
creation, approval, and rejection workflows with automatic wallet crediting.
"""
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.models.deposit import Deposit, DepositStatus, PaymentMethod
from app.models.user import User
from app.services.wallet_service import wallet_service
from app.services.whatsapp import whatsapp_service

logger = logging.getLogger(__name__)


class DepositService:
    """Service for handling deposit requests and approvals."""

    # Minimum deposit amount
    MIN_DEPOSIT = Decimal("10.00")

    @staticmethod
    def create_deposit_request(
        user_id: int,
        amount: Decimal,
        payment_method: PaymentMethod,
        proof_type: Optional[str],
        proof_value: Optional[str],
        notes: Optional[str],
        db: Session,
    ) -> Deposit:
        """
        Create a new deposit request.

        Args:
            user_id: User ID
            amount: Deposit amount
            payment_method: Payment method used
            proof_type: Type of proof (reference_number, image_url)
            proof_value: Actual proof value
            notes: Additional notes from user
            db: Database session

        Returns:
            Created Deposit object

        Raises:
            ValueError: If amount is invalid
        """
        if amount <= 0:
            raise ValueError(f"Deposit amount must be positive, got {amount}")

        if amount < DepositService.MIN_DEPOSIT:
            raise ValueError(f"Minimum deposit is R{DepositService.MIN_DEPOSIT}")

        # Create deposit request
        deposit = Deposit(
            user_id=user_id,
            amount=amount,
            payment_method=payment_method,
            proof_type=proof_type,
            proof_value=proof_value,
            notes=notes,
            status=DepositStatus.PENDING,
            expires_at=datetime.utcnow() + timedelta(hours=24),  # 24 hour expiry
        )

        db.add(deposit)
        db.flush()

        logger.info(
            f"Deposit request created: deposit_id={deposit.id}, "
            f"user_id={user_id}, amount={amount}, method={payment_method}"
        )

        return deposit

    @staticmethod
    async def approve_deposit(
        deposit_id: int,
        admin_user_id: int,
        db: Session,
    ) -> Deposit:
        """
        Approve a deposit request and credit user's wallet.

        This operation is atomic - either deposit is approved AND wallet is credited,
        or both operations are rolled back.

        Args:
            deposit_id: Deposit ID to approve
            admin_user_id: Admin user ID approving the deposit
            db: Database session

        Returns:
            Updated Deposit object

        Raises:
            ValueError: If deposit is not in pending status
        """
        # Get deposit with lock
        deposit = (
            db.query(Deposit)
            .filter(Deposit.id == deposit_id)
            .with_for_update()
            .first()
        )

        if not deposit:
            raise ValueError(f"Deposit {deposit_id} not found")

        if deposit.status != DepositStatus.PENDING:
            raise ValueError(
                f"Deposit {deposit_id} is not pending (status: {deposit.status})"
            )

        # Credit wallet using wallet service
        transaction = wallet_service.credit(
            user_id=deposit.user_id,
            amount=deposit.amount,
            transaction_type="deposit",
            description=f"Deposit via {deposit.payment_method.value}",
            db=db,
            reference_type="deposit_id",
            reference_id=deposit.id,
            metadata={
                "payment_method": deposit.payment_method.value,
                "approved_by": admin_user_id,
            },
        )

        # Update deposit status
        deposit.status = DepositStatus.APPROVED
        deposit.reviewed_by = admin_user_id
        deposit.reviewed_at = datetime.utcnow()
        deposit.transaction_id = transaction.id

        db.flush()

        logger.info(
            f"Deposit approved: deposit_id={deposit_id}, "
            f"user_id={deposit.user_id}, amount={deposit.amount}, "
            f"transaction_id={transaction.id}"
        )

        # Notify user via WhatsApp
        try:
            user = db.query(User).filter(User.id == deposit.user_id).first()
            if user:
                message = f"""✅ DEPOSIT APPROVED

Amount: R{float(deposit.amount):.2f}
Method: {deposit.payment_method.value.replace('_', ' ').title()}
New Balance: R{float(transaction.balance_after):.2f}

Your account has been credited!
Reply 'balance' to check your balance."""

                await whatsapp_service.send_message(user.phone_number, message)
        except Exception as e:
            logger.error(f"Error sending deposit approval notification: {e}")

        return deposit

    @staticmethod
    async def reject_deposit(
        deposit_id: int,
        admin_user_id: int,
        rejection_reason: str,
        db: Session,
    ) -> Deposit:
        """
        Reject a deposit request.

        Args:
            deposit_id: Deposit ID to reject
            admin_user_id: Admin user ID rejecting the deposit
            rejection_reason: Reason for rejection
            db: Database session

        Returns:
            Updated Deposit object

        Raises:
            ValueError: If deposit is not in pending status
        """
        # Get deposit with lock
        deposit = (
            db.query(Deposit)
            .filter(Deposit.id == deposit_id)
            .with_for_update()
            .first()
        )

        if not deposit:
            raise ValueError(f"Deposit {deposit_id} not found")

        if deposit.status != DepositStatus.PENDING:
            raise ValueError(
                f"Deposit {deposit_id} is not pending (status: {deposit.status})"
            )

        # Update deposit status
        deposit.status = DepositStatus.REJECTED
        deposit.reviewed_by = admin_user_id
        deposit.reviewed_at = datetime.utcnow()
        deposit.rejection_reason = rejection_reason

        db.flush()

        logger.info(
            f"Deposit rejected: deposit_id={deposit_id}, "
            f"user_id={deposit.user_id}, reason={rejection_reason}"
        )

        # Notify user via WhatsApp
        try:
            user = db.query(User).filter(User.id == deposit.user_id).first()
            if user:
                message = f"""❌ DEPOSIT REJECTED

Amount: R{float(deposit.amount):.2f}
Method: {deposit.payment_method.value.replace('_', ' ').title()}

Reason: {rejection_reason}

Please contact support if you have questions."""

                await whatsapp_service.send_message(user.phone_number, message)
        except Exception as e:
            logger.error(f"Error sending deposit rejection notification: {e}")

        return deposit

    @staticmethod
    def get_pending_deposits(db: Session, limit: int = 50) -> List[Deposit]:
        """
        Get all pending deposit requests.

        Args:
            db: Database session
            limit: Maximum number of deposits to return

        Returns:
            List of pending Deposit objects
        """
        deposits = (
            db.query(Deposit)
            .filter(Deposit.status == DepositStatus.PENDING)
            .order_by(desc(Deposit.created_at))
            .limit(limit)
            .all()
        )

        return deposits

    @staticmethod
    def get_user_deposits(
        user_id: int,
        db: Session,
        limit: int = 10,
        status: Optional[DepositStatus] = None,
    ) -> List[Deposit]:
        """
        Get deposit history for a user.

        Args:
            user_id: User ID
            db: Database session
            limit: Maximum number of deposits to return
            status: Filter by status (optional)

        Returns:
            List of Deposit objects
        """
        query = db.query(Deposit).filter(Deposit.user_id == user_id)

        if status:
            query = query.filter(Deposit.status == status)

        deposits = query.order_by(desc(Deposit.created_at)).limit(limit).all()

        return deposits


# Export singleton instance
deposit_service = DepositService()
