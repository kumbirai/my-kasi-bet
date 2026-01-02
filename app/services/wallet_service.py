"""
Wallet service for handling all wallet operations.

This module provides atomic wallet operations with complete transaction logging
and balance integrity guarantees. All operations that modify wallet balance
MUST use this service to ensure proper audit trails and prevent race conditions.
"""
import json
import logging
from decimal import Decimal
from typing import Any, Dict, List, Optional

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.models.transaction import Transaction
from app.models.wallet import Wallet

logger = logging.getLogger(__name__)


class InsufficientBalanceError(Exception):
    """Raised when wallet has insufficient balance for a debit operation."""

    pass


class WalletNotFoundError(Exception):
    """Raised when wallet doesn't exist for a user."""

    pass


class WalletService:
    """
    Service for handling all wallet operations with ACID guarantees.

    All operations that modify wallet balance MUST use this service
    to ensure proper transaction logging and balance integrity.
    """

    @staticmethod
    def get_balance(user_id: int, db: Session) -> Decimal:
        """
        Get current wallet balance for a user.

        Args:
            user_id: User ID
            db: Database session

        Returns:
            Current balance as Decimal

        Raises:
            WalletNotFoundError: If wallet doesn't exist
        """
        wallet = db.query(Wallet).filter(Wallet.user_id == user_id).first()

        if not wallet:
            raise WalletNotFoundError(f"Wallet not found for user {user_id}")

        return wallet.balance

    @staticmethod
    def credit(
        user_id: int,
        amount: Decimal,
        transaction_type: str,
        description: str,
        db: Session,
        reference_type: Optional[str] = None,
        reference_id: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Transaction:
        """
        Credit (add money to) a user's wallet.

        This operation is atomic - either both wallet update and transaction log
        succeed, or both are rolled back.

        Args:
            user_id: User ID
            amount: Amount to credit (must be positive)
            transaction_type: Type of transaction (deposit, win, refund)
            description: Human-readable description
            db: Database session
            reference_type: Optional reference type (deposit_id, bet_id)
            reference_id: Optional reference ID
            metadata: Optional additional data as dict

        Returns:
            Created Transaction object

        Raises:
            ValueError: If amount is not positive
            WalletNotFoundError: If wallet doesn't exist
        """
        if amount <= 0:
            raise ValueError(f"Credit amount must be positive, got {amount}")

        # Get wallet with row-level lock to prevent race conditions
        wallet = db.query(Wallet).filter(Wallet.user_id == user_id).with_for_update().first()

        if not wallet:
            raise WalletNotFoundError(f"Wallet not found for user {user_id}")

        # Capture balance before
        balance_before = wallet.balance

        # Update balance
        wallet.balance += amount
        balance_after = wallet.balance

        # Create transaction log
        transaction = Transaction(
            user_id=user_id,
            type=transaction_type,
            amount=amount,
            balance_before=balance_before,
            balance_after=balance_after,
            reference_type=reference_type,
            reference_id=reference_id,
            description=description,
            transaction_metadata=json.dumps(metadata) if metadata else None,
        )

        db.add(transaction)
        db.flush()  # Get transaction ID before commit

        logger.info(
            f"Credited wallet: user_id={user_id}, amount={amount}, "
            f"balance: {balance_before} -> {balance_after}, "
            f"transaction_id={transaction.id}"
        )

        return transaction

    @staticmethod
    def debit(
        user_id: int,
        amount: Decimal,
        transaction_type: str,
        description: str,
        db: Session,
        reference_type: Optional[str] = None,
        reference_id: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
        allow_negative: bool = False,
    ) -> Transaction:
        """
        Debit (subtract money from) a user's wallet.

        This operation is atomic - either both wallet update and transaction log
        succeed, or both are rolled back.

        Args:
            user_id: User ID
            amount: Amount to debit (must be positive)
            transaction_type: Type of transaction (withdrawal, bet)
            description: Human-readable description
            db: Database session
            reference_type: Optional reference type (withdrawal_id, bet_id)
            reference_id: Optional reference ID
            metadata: Optional additional data as dict
            allow_negative: Allow balance to go negative (default: False)

        Returns:
            Created Transaction object

        Raises:
            ValueError: If amount is not positive
            WalletNotFoundError: If wallet doesn't exist
            InsufficientBalanceError: If insufficient balance and allow_negative=False
        """
        if amount <= 0:
            raise ValueError(f"Debit amount must be positive, got {amount}")

        # Get wallet with row-level lock to prevent race conditions
        wallet = db.query(Wallet).filter(Wallet.user_id == user_id).with_for_update().first()

        if not wallet:
            raise WalletNotFoundError(f"Wallet not found for user {user_id}")

        # Check sufficient balance
        if not allow_negative and wallet.balance < amount:
            raise InsufficientBalanceError(
                f"Insufficient balance: has {wallet.balance}, needs {amount}"
            )

        # Capture balance before
        balance_before = wallet.balance

        # Update balance
        wallet.balance -= amount
        balance_after = wallet.balance

        # Create transaction log
        transaction = Transaction(
            user_id=user_id,
            type=transaction_type,
            amount=amount,
            balance_before=balance_before,
            balance_after=balance_after,
            reference_type=reference_type,
            reference_id=reference_id,
            description=description,
            transaction_metadata=json.dumps(metadata) if metadata else None,
        )

        db.add(transaction)
        db.flush()  # Get transaction ID before commit

        logger.info(
            f"Debited wallet: user_id={user_id}, amount={amount}, "
            f"balance: {balance_before} -> {balance_after}, "
            f"transaction_id={transaction.id}"
        )

        return transaction

    @staticmethod
    def get_transaction_history(
        user_id: int,
        db: Session,
        limit: int = 10,
        offset: int = 0,
        transaction_type: Optional[str] = None,
    ) -> List[Transaction]:
        """
        Get transaction history for a user.

        Args:
            user_id: User ID
            db: Database session
            limit: Maximum number of transactions to return
            offset: Number of transactions to skip
            transaction_type: Filter by transaction type (optional)

        Returns:
            List of Transaction objects, ordered by created_at desc
        """
        query = db.query(Transaction).filter(Transaction.user_id == user_id)

        if transaction_type:
            query = query.filter(Transaction.type == transaction_type)

        transactions = query.order_by(desc(Transaction.created_at)).limit(limit).offset(offset).all()

        return transactions

    @staticmethod
    def verify_balance_integrity(user_id: int, db: Session) -> bool:
        """
        Verify wallet balance matches transaction history.

        This is useful for debugging and audit purposes. It checks that
        the wallet balance matches the balance_after of the most recent
        transaction.

        Args:
            user_id: User ID
            db: Database session

        Returns:
            True if balance is correct, False otherwise
        """
        wallet = db.query(Wallet).filter(Wallet.user_id == user_id).first()

        if not wallet:
            logger.error(f"Wallet not found for user {user_id}")
            return False

        # Get all transactions
        transactions = (
            db.query(Transaction)
            .filter(Transaction.user_id == user_id)
            .order_by(Transaction.created_at)
            .all()
        )

        if not transactions:
            # No transactions, balance should be 0
            return wallet.balance == Decimal("0.00")

        # Last transaction's balance_after should match wallet balance
        last_transaction = transactions[-1]

        if wallet.balance != last_transaction.balance_after:
            logger.error(
                f"Balance mismatch for user {user_id}: "
                f"wallet={wallet.balance}, "
                f"last_transaction={last_transaction.balance_after}"
            )
            return False

        return True


# Export singleton instance
wallet_service = WalletService()
