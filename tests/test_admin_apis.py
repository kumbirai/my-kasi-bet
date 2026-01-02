"""
Tests for admin API endpoints.

This module tests all admin API endpoints including authentication,
user management, deposits, withdrawals, bets, and analytics.
"""
import pytest
from decimal import Decimal
from fastapi.testclient import TestClient

from app.main import app
from app.models.admin import AdminRole, AdminUser
from app.models.bet import Bet, BetStatus, BetType
from app.models.deposit import Deposit, DepositStatus, PaymentMethod
from app.models.user import User
from app.models.wallet import Wallet
from app.models.withdrawal import Withdrawal, WithdrawalMethod, WithdrawalStatus
from app.services.admin_service import AdminService
from app.utils.security import get_password_hash

client = TestClient(app)


@pytest.fixture
def test_admin(test_db):
    """Create a test admin user."""
    admin = AdminUser(
        email="admin@test.com",
        hashed_password=get_password_hash("testpassword123"),
        full_name="Test Admin",
        role=AdminRole.ADMIN,
        is_active=True,
    )
    test_db.add(admin)
    test_db.commit()
    test_db.refresh(admin)
    return admin


@pytest.fixture
def admin_token(test_admin):
    """Get JWT token for test admin."""
    token = AdminService.create_access_token_for_admin(test_admin)
    return token


def test_admin_login_success(test_db, test_admin):
    """Test successful admin login."""
    from app.api.deps import get_db_session
    app.dependency_overrides[get_db_session] = lambda: test_db

    response = client.post(
        "/api/admin/login",
        json={"email": "admin@test.com", "password": "testpassword123"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

    app.dependency_overrides.clear()


def test_admin_login_invalid_credentials(test_db, test_admin):
    """Test admin login with invalid credentials."""
    from app.api.deps import get_db_session
    app.dependency_overrides[get_db_session] = lambda: test_db

    response = client.post(
        "/api/admin/login",
        json={"email": "admin@test.com", "password": "wrongpassword"},
    )

    assert response.status_code == 401

    app.dependency_overrides.clear()


def test_list_users(test_db, test_admin, admin_token, test_user):
    """Test listing users."""
    from app.api.deps import get_db_session, get_current_admin
    app.dependency_overrides[get_db_session] = lambda: test_db
    app.dependency_overrides[get_current_admin] = lambda: test_admin

    response = client.get(
        "/api/admin/users",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "users" in data
    assert "total" in data
    assert len(data["users"]) > 0

    app.dependency_overrides.clear()


def test_get_user_details(test_db, test_admin, admin_token, test_user):
    """Test getting user details."""
    from app.api.deps import get_db_session, get_current_admin
    app.dependency_overrides[get_db_session] = lambda: test_db
    app.dependency_overrides[get_current_admin] = lambda: test_admin

    response = client.get(
        f"/api/admin/users/{test_user.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_user.id
    assert "wallet_balance" in data
    assert "total_bets" in data

    app.dependency_overrides.clear()


def test_block_user(test_db, test_admin, admin_token, test_user):
    """Test blocking a user."""
    from app.api.deps import get_db_session, get_current_admin
    app.dependency_overrides[get_db_session] = lambda: test_db
    app.dependency_overrides[get_current_admin] = lambda: test_admin

    response = client.post(
        f"/api/admin/users/{test_user.id}/block",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"reason": "Test blocking"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "User blocked successfully"

    # Verify user is blocked
    test_db.refresh(test_user)
    assert test_user.is_blocked is True

    app.dependency_overrides.clear()


def test_unblock_user(test_db, test_admin, admin_token, test_user):
    """Test unblocking a user."""
    from app.api.deps import get_db_session, get_current_admin
    app.dependency_overrides[get_db_session] = lambda: test_db
    app.dependency_overrides[get_current_admin] = lambda: test_admin

    # First block the user
    test_user.is_blocked = True
    test_db.commit()

    response = client.post(
        f"/api/admin/users/{test_user.id}/unblock",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "User unblocked successfully"

    # Verify user is unblocked
    test_db.refresh(test_user)
    assert test_user.is_blocked is False

    app.dependency_overrides.clear()


def test_list_deposits(test_db, test_admin, admin_token, test_user):
    """Test listing deposits."""
    from app.api.deps import get_db_session, get_current_admin
    app.dependency_overrides[get_db_session] = lambda: test_db
    app.dependency_overrides[get_current_admin] = lambda: test_admin

    # Create a test deposit
    deposit = Deposit(
        user_id=test_user.id,
        amount=Decimal("100.00"),
        payment_method=PaymentMethod.BANK_TRANSFER,
        status=DepositStatus.PENDING,
    )
    test_db.add(deposit)
    test_db.commit()

    response = client.get(
        "/api/admin/deposits",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "deposits" in data
    assert "total" in data

    app.dependency_overrides.clear()


def test_list_withdrawals(test_db, test_admin, admin_token, test_user):
    """Test listing withdrawals."""
    from app.api.deps import get_db_session, get_current_admin
    app.dependency_overrides[get_db_session] = lambda: test_db
    app.dependency_overrides[get_current_admin] = lambda: test_admin

    # Create a test withdrawal
    withdrawal = Withdrawal(
        user_id=test_user.id,
        amount=Decimal("50.00"),
        withdrawal_method=WithdrawalMethod.BANK_TRANSFER,
        bank_name="Test Bank",
        account_number="123456789",
        account_holder="Test User",
        status=WithdrawalStatus.PENDING,
    )
    test_db.add(withdrawal)
    test_db.commit()

    response = client.get(
        "/api/admin/withdrawals",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "withdrawals" in data
    assert "total" in data

    app.dependency_overrides.clear()


def test_list_bets(test_db, test_admin, admin_token, test_user):
    """Test listing bets."""
    from app.api.deps import get_db_session, get_current_admin
    app.dependency_overrides[get_db_session] = lambda: test_db
    app.dependency_overrides[get_current_admin] = lambda: test_admin

    # Create a test bet
    bet = Bet(
        user_id=test_user.id,
        bet_type=BetType.LUCKY_WHEEL,
        stake_amount=Decimal("10.00"),
        bet_data='{"selected_number": 5}',
        status=BetStatus.PENDING,
        payout_amount=Decimal("0.00"),
    )
    test_db.add(bet)
    test_db.commit()

    response = client.get(
        "/api/admin/bets",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "bets" in data
    assert "total" in data

    app.dependency_overrides.clear()


def test_get_bet_statistics(test_db, test_admin, admin_token, test_user):
    """Test getting bet statistics."""
    from app.api.deps import get_db_session, get_current_admin
    app.dependency_overrides[get_db_session] = lambda: test_db
    app.dependency_overrides[get_current_admin] = lambda: test_admin

    # Create test bets
    bet1 = Bet(
        user_id=test_user.id,
        bet_type=BetType.LUCKY_WHEEL,
        stake_amount=Decimal("10.00"),
        bet_data='{"selected_number": 5}',
        status=BetStatus.WON,
        payout_amount=Decimal("100.00"),
    )
    bet2 = Bet(
        user_id=test_user.id,
        bet_type=BetType.COLOR_GAME,
        stake_amount=Decimal("20.00"),
        bet_data='{"selected_color": "red"}',
        status=BetStatus.LOST,
        payout_amount=Decimal("0.00"),
    )
    test_db.add(bet1)
    test_db.add(bet2)
    test_db.commit()

    response = client.get(
        "/api/admin/bets/statistics",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "total_bets" in data
    assert "total_wagered" in data
    assert "net_revenue" in data
    assert data["total_bets"] >= 2

    app.dependency_overrides.clear()


def test_get_dashboard_stats(test_db, test_admin, admin_token, test_user):
    """Test getting dashboard statistics."""
    from app.api.deps import get_db_session, get_current_admin
    app.dependency_overrides[get_db_session] = lambda: test_db
    app.dependency_overrides[get_current_admin] = lambda: test_admin

    response = client.get(
        "/api/admin/analytics/dashboard",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "total_users" in data
    assert "total_deposits" in data
    assert "total_withdrawals" in data
    assert "net_revenue" in data

    app.dependency_overrides.clear()


def test_get_revenue_breakdown(test_db, test_admin, admin_token, test_user):
    """Test getting revenue breakdown."""
    from app.api.deps import get_db_session, get_current_admin
    app.dependency_overrides[get_db_session] = lambda: test_db
    app.dependency_overrides[get_current_admin] = lambda: test_admin

    response = client.get(
        "/api/admin/analytics/revenue",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

    app.dependency_overrides.clear()


def test_get_user_engagement(test_db, test_admin, admin_token, test_user):
    """Test getting user engagement metrics."""
    from app.api.deps import get_db_session, get_current_admin
    app.dependency_overrides[get_db_session] = lambda: test_db
    app.dependency_overrides[get_current_admin] = lambda: test_admin

    response = client.get(
        "/api/admin/analytics/users",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "total_users" in data
    assert "active_users_24h" in data
    assert "average_bets_per_user" in data

    app.dependency_overrides.clear()


def test_unauthorized_access(test_db):
    """Test that endpoints require authentication."""
    from app.api.deps import get_db_session
    app.dependency_overrides[get_db_session] = lambda: test_db

    response = client.get("/api/admin/users")

    assert response.status_code == 403  # FastAPI returns 403 for missing auth

    app.dependency_overrides.clear()
