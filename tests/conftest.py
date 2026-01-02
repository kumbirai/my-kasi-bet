"""
Pytest configuration and fixtures.

This module provides shared fixtures for all tests.
"""
from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.models import (
    AdminActionLog,
    AdminUser,
    Bet,
    Deposit,
    Transaction,
    User,
    Wallet,
    Withdrawal,
)


@pytest.fixture(scope="function")
def test_db():
    """
    Create a test database session with in-memory SQLite.

    This fixture creates a fresh database for each test function
    and automatically cleans up after the test completes.

    Yields:
        Session: Test database session
    """
    # Create in-memory SQLite database for testing
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Create session factory
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=engine
    )

    # Create session
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user(test_db: Session) -> User:
    """
    Create a test user with wallet.

    Args:
        test_db: Test database session

    Returns:
        User: Test user instance
    """
    user = User(phone_number="27821234567", username="TestUser")
    test_db.add(user)
    test_db.flush()

    wallet = Wallet(user_id=user.id, balance=Decimal("1000.00"))
    test_db.add(wallet)
    test_db.commit()
    test_db.refresh(user)

    return user
