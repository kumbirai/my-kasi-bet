"""
Tests for admin service.

This module tests admin user operations, authentication, and action logging.
"""
import pytest
from decimal import Decimal

from app.models.admin import AdminRole, AdminUser
from app.models.admin_action_log import AdminActionLog
from app.services.admin_service import AdminService


def test_create_admin_user(test_db):
    """Test creating a new admin user."""
    admin = AdminService.create_admin_user(
        email="admin@test.com",
        password="testpassword123",
        full_name="Test Admin",
        role=AdminRole.ADMIN,
        db=test_db,
    )

    assert admin.id is not None
    assert admin.email == "admin@test.com"
    assert admin.full_name == "Test Admin"
    assert admin.role == AdminRole.ADMIN
    assert admin.is_active is True
    assert admin.hashed_password != "testpassword123"  # Should be hashed


def test_create_admin_user_duplicate_email(test_db):
    """Test creating admin user with duplicate email fails."""
    AdminService.create_admin_user(
        email="admin@test.com",
        password="testpassword123",
        full_name="Test Admin",
        db=test_db,
    )

    with pytest.raises(ValueError, match="already exists"):
        AdminService.create_admin_user(
            email="admin@test.com",
            password="anotherpassword",
            full_name="Another Admin",
            db=test_db,
        )


def test_authenticate_admin_success(test_db):
    """Test successful admin authentication."""
    AdminService.create_admin_user(
        email="admin@test.com",
        password="testpassword123",
        full_name="Test Admin",
        db=test_db,
    )

    admin = AdminService.authenticate_admin(
        email="admin@test.com",
        password="testpassword123",
        db=test_db,
    )

    assert admin is not None
    assert admin.email == "admin@test.com"


def test_authenticate_admin_wrong_password(test_db):
    """Test authentication with wrong password."""
    AdminService.create_admin_user(
        email="admin@test.com",
        password="testpassword123",
        full_name="Test Admin",
        db=test_db,
    )

    admin = AdminService.authenticate_admin(
        email="admin@test.com",
        password="wrongpassword",
        db=test_db,
    )

    assert admin is None


def test_authenticate_admin_inactive(test_db):
    """Test authentication with inactive admin account."""
    admin = AdminService.create_admin_user(
        email="admin@test.com",
        password="testpassword123",
        full_name="Test Admin",
        db=test_db,
    )

    admin.is_active = False
    test_db.commit()

    result = AdminService.authenticate_admin(
        email="admin@test.com",
        password="testpassword123",
        db=test_db,
    )

    assert result is None


def test_get_admin_by_id(test_db):
    """Test getting admin by ID."""
    created_admin = AdminService.create_admin_user(
        email="admin@test.com",
        password="testpassword123",
        full_name="Test Admin",
        db=test_db,
    )

    admin = AdminService.get_admin_by_id(created_admin.id, test_db)

    assert admin is not None
    assert admin.id == created_admin.id
    assert admin.email == "admin@test.com"


def test_get_admin_by_id_not_found(test_db):
    """Test getting non-existent admin by ID."""
    admin = AdminService.get_admin_by_id(999, test_db)

    assert admin is None


def test_create_access_token_for_admin(test_db):
    """Test creating JWT access token for admin."""
    admin = AdminService.create_admin_user(
        email="admin@test.com",
        password="testpassword123",
        full_name="Test Admin",
        db=test_db,
    )

    token = AdminService.create_access_token_for_admin(admin)

    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 0


def test_log_admin_action(test_db):
    """Test logging an admin action."""
    admin = AdminService.create_admin_user(
        email="admin@test.com",
        password="testpassword123",
        full_name="Test Admin",
        db=test_db,
    )

    log_entry = AdminService.log_admin_action(
        admin_id=admin.id,
        action_type="approve_deposit",
        entity_type="deposit",
        entity_id=1,
        details={"amount": "100.00", "user_id": 1},
        db=test_db,
    )

    assert log_entry.id is not None
    assert log_entry.admin_id == admin.id
    assert log_entry.action_type == "approve_deposit"
    assert log_entry.entity_type == "deposit"
    assert log_entry.entity_id == 1

    # Verify it was saved to database
    saved_log = test_db.query(AdminActionLog).filter(AdminActionLog.id == log_entry.id).first()
    assert saved_log is not None
    assert saved_log.admin_id == admin.id


def test_check_role_permission_super_admin(test_db):
    """Test role permission check for super admin."""
    admin = AdminService.create_admin_user(
        email="admin@test.com",
        password="testpassword123",
        full_name="Test Admin",
        role=AdminRole.SUPER_ADMIN,
        db=test_db,
    )

    # Super admin should have all permissions
    assert AdminService.check_role_permission(admin, AdminRole.SUPER_ADMIN) is True
    assert AdminService.check_role_permission(admin, AdminRole.ADMIN) is True
    assert AdminService.check_role_permission(admin, AdminRole.SUPPORT) is True


def test_check_role_permission_admin(test_db):
    """Test role permission check for admin."""
    admin = AdminService.create_admin_user(
        email="admin@test.com",
        password="testpassword123",
        full_name="Test Admin",
        role=AdminRole.ADMIN,
        db=test_db,
    )

    assert AdminService.check_role_permission(admin, AdminRole.ADMIN) is True
    assert AdminService.check_role_permission(admin, AdminRole.SUPPORT) is True
    assert AdminService.check_role_permission(admin, AdminRole.SUPER_ADMIN) is False


def test_check_role_permission_support(test_db):
    """Test role permission check for support."""
    admin = AdminService.create_admin_user(
        email="admin@test.com",
        password="testpassword123",
        full_name="Test Admin",
        role=AdminRole.SUPPORT,
        db=test_db,
    )

    assert AdminService.check_role_permission(admin, AdminRole.SUPPORT) is True
    assert AdminService.check_role_permission(admin, AdminRole.ADMIN) is False
    assert AdminService.check_role_permission(admin, AdminRole.SUPER_ADMIN) is False
