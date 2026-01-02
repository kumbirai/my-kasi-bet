"""
Integration tests for withdrawal flow.

This module tests the complete withdrawal approval and rejection flows.
"""
from decimal import Decimal

import pytest

from app.models.admin import AdminRole, AdminUser
from app.models.withdrawal import WithdrawalMethod, WithdrawalStatus
from app.services.wallet_service import wallet_service
from app.services.withdrawal_service import withdrawal_service
from app.utils.security import get_password_hash


@pytest.fixture
def test_admin(test_db):
    """Create a test admin user."""
    # Use a pre-hashed password to avoid bcrypt initialization issues in tests
    # This is a bcrypt hash of "password123" with rounds=4 for faster testing
    pre_hashed = "$2b$04$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"
    admin = AdminUser(
        email="admin@test.com",
        hashed_password=pre_hashed,
        full_name="Test Admin",
        role=AdminRole.ADMIN,
        is_active=True,
    )
    test_db.add(admin)
    test_db.commit()
    test_db.refresh(admin)
    return admin


@pytest.fixture
def test_user_with_balance(test_db):
    """Create a test user with balance."""
    from app.models.user import User
    from app.models.wallet import Wallet

    user = User(phone_number="27821234567", username="TestUser")
    test_db.add(user)
    test_db.flush()

    wallet = Wallet(user_id=user.id, balance=Decimal("500.00"))
    test_db.add(wallet)
    test_db.commit()
    test_db.refresh(user)

    return user


@pytest.mark.asyncio
async def test_withdrawal_approval_flow(test_db, test_user_with_balance, test_admin):
    """Test complete withdrawal approval flow."""
    initial_balance = wallet_service.get_balance(test_user_with_balance.id, test_db)

    # Create withdrawal request
    withdrawal = withdrawal_service.create_withdrawal_request(
        user_id=test_user_with_balance.id,
        amount=Decimal("100.00"),
        withdrawal_method=WithdrawalMethod.BANK_TRANSFER,
        bank_name="FNB",
        account_number="1234567890",
        account_holder="Test User",
        notes="Test withdrawal",
        db=test_db,
    )
    test_db.commit()

    assert withdrawal.status == WithdrawalStatus.PENDING

    # Balance should be debited immediately
    after_request_balance = wallet_service.get_balance(
        test_user_with_balance.id, test_db
    )
    assert after_request_balance == initial_balance - Decimal("100.00")

    # Approve withdrawal
    approved = await withdrawal_service.approve_withdrawal(
        withdrawal_id=withdrawal.id,
        admin_user_id=test_admin.id,
        payment_reference="PAY123",
        db=test_db,
    )
    test_db.commit()

    assert approved.status == WithdrawalStatus.APPROVED
    assert approved.payment_reference == "PAY123"

    # Balance should remain the same (already debited)
    final_balance = wallet_service.get_balance(test_user_with_balance.id, test_db)
    assert final_balance == after_request_balance


@pytest.mark.asyncio
async def test_withdrawal_rejection_refund(test_db, test_user_with_balance, test_admin):
    """Test withdrawal rejection refunds to wallet."""
    initial_balance = wallet_service.get_balance(test_user_with_balance.id, test_db)

    withdrawal = withdrawal_service.create_withdrawal_request(
        user_id=test_user_with_balance.id,
        amount=Decimal("50.00"),
        withdrawal_method=WithdrawalMethod.EWALLET,
        bank_name=None,
        account_number="0821234567",
        account_holder=None,
        notes="Test",
        db=test_db,
    )
    test_db.commit()

    # Balance should be debited
    after_request_balance = wallet_service.get_balance(
        test_user_with_balance.id, test_db
    )
    assert after_request_balance == initial_balance - Decimal("50.00")

    # Reject withdrawal
    rejected = await withdrawal_service.reject_withdrawal(
        withdrawal_id=withdrawal.id,
        admin_user_id=test_admin.id,
        rejection_reason="Invalid account details",
        db=test_db,
    )
    test_db.commit()

    assert rejected.status == WithdrawalStatus.REJECTED
    assert rejected.refund_transaction_id is not None

    # Balance should be refunded
    final_balance = wallet_service.get_balance(test_user_with_balance.id, test_db)
    assert final_balance == initial_balance


def test_withdrawal_minimum_amount(test_db, test_user):
    """Test minimum withdrawal amount validation."""
    with pytest.raises(ValueError, match="Minimum withdrawal"):
        withdrawal_service.create_withdrawal_request(
            user_id=test_user.id,
            amount=Decimal("20.00"),
            withdrawal_method=WithdrawalMethod.BANK_TRANSFER,
            bank_name="FNB",
            account_number="1234567890",
            account_holder="Test",
            notes="Test",
            db=test_db,
        )


def test_withdrawal_insufficient_balance(test_db, test_user):
    """Test withdrawal with insufficient balance."""
    with pytest.raises(Exception):  # InsufficientBalanceError
        withdrawal_service.create_withdrawal_request(
            user_id=test_user.id,
            amount=Decimal("2000.00"),  # More than test_user's balance
            withdrawal_method=WithdrawalMethod.BANK_TRANSFER,
            bank_name="FNB",
            account_number="1234567890",
            account_holder="Test",
            notes="Test",
            db=test_db,
        )


@pytest.mark.asyncio
async def test_withdrawal_double_approval(test_db, test_user_with_balance, test_admin):
    """Test that withdrawal cannot be approved twice."""
    withdrawal = withdrawal_service.create_withdrawal_request(
        user_id=test_user_with_balance.id,
        amount=Decimal("100.00"),
        withdrawal_method=WithdrawalMethod.BANK_TRANSFER,
        bank_name="FNB",
        account_number="1234567890",
        account_holder="Test",
        notes="Test",
        db=test_db,
    )
    test_db.commit()

    # Approve first time
    await withdrawal_service.approve_withdrawal(
        withdrawal_id=withdrawal.id,
        admin_user_id=test_admin.id,
        payment_reference="PAY123",
        db=test_db,
    )
    test_db.commit()

    # Try to approve again
    with pytest.raises(ValueError, match="not pending"):
        await withdrawal_service.approve_withdrawal(
            withdrawal_id=withdrawal.id,
            admin_user_id=test_admin.id,
            payment_reference="PAY456",
            db=test_db,
        )
