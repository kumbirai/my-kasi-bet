"""
Tests for wallet service.

This module tests WalletService operations including credit, debit,
transaction history, and balance integrity verification.
"""
import json
from decimal import Decimal

import pytest

from app.models.transaction import Transaction
from app.models.wallet import Wallet
from app.services.wallet_service import (
    InsufficientBalanceError,
    WalletNotFoundError,
    WalletService,
)


def test_get_balance(test_db, test_user):
    """Test getting wallet balance."""
    balance = WalletService.get_balance(test_user.id, test_db)
    assert balance == Decimal("1000.00")


def test_get_balance_wallet_not_found(test_db):
    """Test getting balance for non-existent wallet."""
    with pytest.raises(WalletNotFoundError):
        WalletService.get_balance(999, test_db)


def test_credit_wallet(test_db, test_user):
    """Test crediting wallet."""
    transaction = WalletService.credit(
        user_id=test_user.id,
        amount=Decimal("50.00"),
        transaction_type="deposit",
        description="Test deposit",
        db=test_db,
    )

    test_db.commit()

    # Verify balance
    new_balance = WalletService.get_balance(test_user.id, test_db)
    assert new_balance == Decimal("1050.00")

    # Verify transaction
    assert transaction.amount == Decimal("50.00")
    assert transaction.balance_before == Decimal("1000.00")
    assert transaction.balance_after == Decimal("1050.00")
    assert transaction.type == "deposit"
    assert transaction.description == "Test deposit"


def test_credit_with_reference(test_db, test_user):
    """Test crediting wallet with reference."""
    transaction = WalletService.credit(
        user_id=test_user.id,
        amount=Decimal("25.00"),
        transaction_type="deposit",
        description="Deposit with reference",
        db=test_db,
        reference_type="deposit_id",
        reference_id=123,
    )

    test_db.commit()

    assert transaction.reference_type == "deposit_id"
    assert transaction.reference_id == 123


def test_credit_with_metadata(test_db, test_user):
    """Test crediting wallet with metadata."""
    metadata = {"payment_method": "bank_transfer", "admin_id": 1}
    transaction = WalletService.credit(
        user_id=test_user.id,
        amount=Decimal("30.00"),
        transaction_type="deposit",
        description="Deposit with metadata",
        db=test_db,
        metadata=metadata,
    )

    test_db.commit()

    assert transaction.transaction_metadata is not None
    parsed_metadata = json.loads(transaction.transaction_metadata)
    assert "payment_method" in parsed_metadata
    assert "admin_id" in parsed_metadata


def test_credit_negative_amount(test_db, test_user):
    """Test crediting with negative amount raises error."""
    with pytest.raises(ValueError, match="Credit amount must be positive"):
        WalletService.credit(
            user_id=test_user.id,
            amount=Decimal("-10.00"),
            transaction_type="deposit",
            description="Invalid deposit",
            db=test_db,
        )


def test_credit_zero_amount(test_db, test_user):
    """Test crediting with zero amount raises error."""
    with pytest.raises(ValueError, match="Credit amount must be positive"):
        WalletService.credit(
            user_id=test_user.id,
            amount=Decimal("0.00"),
            transaction_type="deposit",
            description="Invalid deposit",
            db=test_db,
        )


def test_debit_wallet(test_db, test_user):
    """Test debiting wallet."""
    transaction = WalletService.debit(
        user_id=test_user.id,
        amount=Decimal("30.00"),
        transaction_type="bet",
        description="Test bet",
        db=test_db,
    )

    test_db.commit()

    # Verify balance
    new_balance = WalletService.get_balance(test_user.id, test_db)
    assert new_balance == Decimal("970.00")

    # Verify transaction
    assert transaction.amount == Decimal("30.00")
    assert transaction.balance_before == Decimal("1000.00")
    assert transaction.balance_after == Decimal("970.00")
    assert transaction.type == "bet"


def test_debit_insufficient_balance(test_db, test_user):
    """Test debit with insufficient balance."""
    with pytest.raises(InsufficientBalanceError):
        WalletService.debit(
            user_id=test_user.id,
            amount=Decimal("1500.00"),
            transaction_type="bet",
            description="Test bet",
            db=test_db,
        )


def test_debit_allow_negative(test_db, test_user):
    """Test debit with allow_negative flag."""
    transaction = WalletService.debit(
        user_id=test_user.id,
        amount=Decimal("150.00"),
        transaction_type="bet",
        description="Test bet with negative allowed",
        db=test_db,
        allow_negative=True,
    )

    test_db.commit()

    new_balance = WalletService.get_balance(test_user.id, test_db)
    assert new_balance == Decimal("850.00")
    assert transaction.balance_after == Decimal("850.00")


def test_debit_negative_amount(test_db, test_user):
    """Test debiting with negative amount raises error."""
    with pytest.raises(ValueError, match="Debit amount must be positive"):
        WalletService.debit(
            user_id=test_user.id,
            amount=Decimal("-10.00"),
            transaction_type="bet",
            description="Invalid bet",
            db=test_db,
        )


def test_transaction_history(test_db, test_user):
    """Test transaction history."""
    # Create multiple transactions
    WalletService.credit(
        test_user.id, Decimal("50.00"), "deposit", "Deposit 1", test_db
    )
    WalletService.debit(test_user.id, Decimal("20.00"), "bet", "Bet 1", test_db)
    WalletService.credit(test_user.id, Decimal("10.00"), "win", "Win 1", test_db)
    test_db.commit()

    # Get history
    history = WalletService.get_transaction_history(test_user.id, test_db, limit=10)

    assert len(history) == 3
    # Should be ordered by created_at desc
    assert history[0].type == "win"
    assert history[1].type == "bet"
    assert history[2].type == "deposit"


def test_transaction_history_with_filter(test_db, test_user):
    """Test transaction history with type filter."""
    WalletService.credit(
        test_user.id, Decimal("50.00"), "deposit", "Deposit 1", test_db
    )
    WalletService.debit(test_user.id, Decimal("20.00"), "bet", "Bet 1", test_db)
    WalletService.credit(test_user.id, Decimal("10.00"), "deposit", "Deposit 2", test_db)
    test_db.commit()

    # Get only deposits
    deposits = WalletService.get_transaction_history(
        test_user.id, test_db, limit=10, transaction_type="deposit"
    )

    assert len(deposits) == 2
    assert all(t.type == "deposit" for t in deposits)


def test_transaction_history_pagination(test_db, test_user):
    """Test transaction history pagination."""
    # Create multiple transactions
    for i in range(5):
        WalletService.credit(
            test_user.id, Decimal("10.00"), "deposit", f"Deposit {i}", test_db
        )
    test_db.commit()

    # Get first page
    page1 = WalletService.get_transaction_history(
        test_user.id, test_db, limit=2, offset=0
    )
    assert len(page1) == 2

    # Get second page
    page2 = WalletService.get_transaction_history(
        test_user.id, test_db, limit=2, offset=2
    )
    assert len(page2) == 2

    # Verify different transactions
    assert page1[0].id != page2[0].id


def test_balance_integrity(test_db, test_user):
    """Test balance integrity verification."""
    # Create transactions
    WalletService.credit(test_user.id, Decimal("50.00"), "deposit", "Test", test_db)
    WalletService.debit(test_user.id, Decimal("20.00"), "bet", "Test", test_db)
    test_db.commit()

    # Verify integrity
    assert WalletService.verify_balance_integrity(test_user.id, test_db) is True


def test_balance_integrity_no_transactions(test_db, test_user):
    """Test balance integrity with no transactions."""
    # User starts with R100 from fixture
    # But if we reset to 0, integrity should pass
    test_user.wallet.balance = Decimal("0.00")
    test_db.commit()

    assert WalletService.verify_balance_integrity(test_user.id, test_db) is True


def test_concurrent_operations(test_db, test_user):
    """Test sequential wallet operations work correctly."""
    WalletService.credit(test_user.id, Decimal("10.00"), "deposit", "Test 1", test_db)
    WalletService.credit(test_user.id, Decimal("20.00"), "deposit", "Test 2", test_db)
    WalletService.debit(test_user.id, Decimal("15.00"), "bet", "Test 3", test_db)
    test_db.commit()

    final_balance = WalletService.get_balance(test_user.id, test_db)
    # 1000 + 10 + 20 - 15 = 1015
    assert final_balance == Decimal("1015.00")

    # Verify integrity
    assert WalletService.verify_balance_integrity(test_user.id, test_db) is True


def test_multiple_transaction_types(test_db, test_user):
    """Test different transaction types."""
    WalletService.credit(test_user.id, Decimal("50.00"), "deposit", "Deposit", test_db)
    WalletService.credit(test_user.id, Decimal("25.00"), "win", "Win", test_db)
    WalletService.credit(test_user.id, Decimal("10.00"), "refund", "Refund", test_db)
    WalletService.debit(test_user.id, Decimal("30.00"), "bet", "Bet", test_db)
    WalletService.debit(test_user.id, Decimal("20.00"), "withdrawal", "Withdrawal", test_db)
    test_db.commit()

    final_balance = WalletService.get_balance(test_user.id, test_db)
    # 1000 + 50 + 25 + 10 - 30 - 20 = 1035
    assert final_balance == Decimal("1035.00")

    # Verify all transaction types are recorded
    history = WalletService.get_transaction_history(test_user.id, test_db, limit=10)
    types = {t.type for t in history}
    assert "deposit" in types
    assert "win" in types
    assert "refund" in types
    assert "bet" in types
    assert "withdrawal" in types
