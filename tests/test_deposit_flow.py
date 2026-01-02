"""
Integration tests for deposit flow.

This module tests the complete deposit approval and rejection flows.
"""
from decimal import Decimal

import pytest

from app.models.admin import AdminRole, AdminUser
from app.models.deposit import DepositStatus, PaymentMethod
from app.services.deposit_service import deposit_service
from app.services.wallet_service import wallet_service
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


@pytest.mark.asyncio
async def test_deposit_approval_flow(test_db, test_user, test_admin):
    """Test complete deposit approval flow."""
    # Create deposit request
    deposit = deposit_service.create_deposit_request(
        user_id=test_user.id,
        amount=Decimal("100.00"),
        payment_method=PaymentMethod.BANK_TRANSFER,
        proof_type="reference",
        proof_value="REF123",
        notes="Test deposit",
        db=test_db,
    )
    test_db.commit()

    assert deposit.status == DepositStatus.PENDING

    # Get initial balance
    initial_balance = wallet_service.get_balance(test_user.id, test_db)

    # Approve deposit
    approved = await deposit_service.approve_deposit(
        deposit_id=deposit.id,
        admin_user_id=test_admin.id,
        db=test_db,
    )
    test_db.commit()

    assert approved.status == DepositStatus.APPROVED
    assert approved.transaction_id is not None
    assert approved.reviewed_by == test_admin.id

    # Check balance increased
    new_balance = wallet_service.get_balance(test_user.id, test_db)
    assert new_balance == initial_balance + Decimal("100.00")


@pytest.mark.asyncio
async def test_deposit_rejection_flow(test_db, test_user, test_admin):
    """Test deposit rejection flow."""
    deposit = deposit_service.create_deposit_request(
        user_id=test_user.id,
        amount=Decimal("50.00"),
        payment_method=PaymentMethod.SNAPSCAN,
        proof_type="reference",
        proof_value="SNAP456",
        notes="Test",
        db=test_db,
    )
    test_db.commit()

    initial_balance = wallet_service.get_balance(test_user.id, test_db)

    # Reject deposit
    rejected = await deposit_service.reject_deposit(
        deposit_id=deposit.id,
        admin_user_id=test_admin.id,
        rejection_reason="Invalid proof of payment",
        db=test_db,
    )
    test_db.commit()

    assert rejected.status == DepositStatus.REJECTED
    assert rejected.rejection_reason == "Invalid proof of payment"

    # Balance should not change
    final_balance = wallet_service.get_balance(test_user.id, test_db)
    assert final_balance == initial_balance


def test_deposit_minimum_amount(test_db, test_user):
    """Test minimum deposit amount validation."""
    with pytest.raises(ValueError, match="Minimum deposit"):
        deposit_service.create_deposit_request(
            user_id=test_user.id,
            amount=Decimal("5.00"),
            payment_method=PaymentMethod.BANK_TRANSFER,
            proof_type="reference",
            proof_value="REF123",
            notes="Test",
            db=test_db,
        )


@pytest.mark.asyncio
async def test_deposit_double_approval(test_db, test_user, test_admin):
    """Test that deposit cannot be approved twice."""
    deposit = deposit_service.create_deposit_request(
        user_id=test_user.id,
        amount=Decimal("100.00"),
        payment_method=PaymentMethod.BANK_TRANSFER,
        proof_type="reference",
        proof_value="REF123",
        notes="Test",
        db=test_db,
    )
    test_db.commit()

    # Approve first time
    await deposit_service.approve_deposit(
        deposit_id=deposit.id,
        admin_user_id=test_admin.id,
        db=test_db,
    )
    test_db.commit()

    # Try to approve again
    with pytest.raises(ValueError, match="not pending"):
        await deposit_service.approve_deposit(
            deposit_id=deposit.id,
            admin_user_id=test_admin.id,
            db=test_db,
        )
