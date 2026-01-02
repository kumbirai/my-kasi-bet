"""
Tests for database models.

This module tests User and Wallet model functionality.
"""
from decimal import Decimal

import pytest

from app.models.user import User
from app.models.wallet import Wallet


def test_create_user(test_db):
    """Test creating a user."""
    user = User(phone_number="27821234567", username="TestUser")
    test_db.add(user)
    test_db.commit()

    assert user.id is not None
    assert user.phone_number == "27821234567"
    assert user.username == "TestUser"
    assert user.is_active is True
    assert user.is_blocked is False


def test_create_wallet(test_db):
    """Test creating a wallet for a user."""
    from app.models.user import User
    
    # Create a new user without wallet for this test
    user = User(phone_number="27829999999", username="TestUser2")
    test_db.add(user)
    test_db.flush()
    
    wallet = Wallet(user_id=user.id, balance=Decimal("100.00"))
    test_db.add(wallet)
    test_db.commit()

    assert wallet.id is not None
    assert wallet.user_id == user.id
    assert wallet.balance == Decimal("100.00")


def test_user_wallet_relationship(test_db, test_user):
    """Test user-wallet relationship."""
    test_db.refresh(test_user)
    assert test_user.wallet is not None
    assert test_user.wallet.user_id == test_user.id


def test_user_repr(test_user):
    """Test user string representation."""
    repr_str = repr(test_user)
    assert "User" in repr_str
    assert str(test_user.id) in repr_str
    assert test_user.phone_number in repr_str


def test_wallet_repr(test_db, test_user):
    """Test wallet string representation."""
    test_db.refresh(test_user)
    wallet = test_user.wallet
    repr_str = repr(wallet)
    assert "Wallet" in repr_str
    assert str(wallet.user_id) in repr_str
