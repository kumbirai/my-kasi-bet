"""
Admin service for handling admin user operations and action logging.

This module provides business logic for admin user management including
authentication, password hashing, and audit trail logging.
"""
import json
import logging
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.models.admin import AdminRole, AdminUser
from app.models.admin_action_log import AdminActionLog
from app.utils.security import (
    create_access_token,
    get_password_hash,
    verify_password,
)

logger = logging.getLogger(__name__)


class AdminService:
    """Service for handling admin user operations and action logging."""

    @staticmethod
    def create_admin_user(
        email: str,
        password: str,
        full_name: str,
        role: AdminRole = AdminRole.SUPPORT,
        db: Session = None,
    ) -> AdminUser:
        """
        Create a new admin user.

        Args:
            email: Admin email address
            password: Plain text password (will be hashed)
            full_name: Admin full name
            role: Admin role (default: SUPPORT)
            db: Database session

        Returns:
            Created AdminUser object

        Raises:
            ValueError: If email already exists
        """
        if db is None:
            raise ValueError("Database session is required")

        # Check if email already exists
        existing_admin = db.query(AdminUser).filter(AdminUser.email == email).first()
        if existing_admin:
            raise ValueError(f"Admin user with email {email} already exists")

        # Hash password
        hashed_password = get_password_hash(password)

        # Create admin user
        admin_user = AdminUser(
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            role=role,
            is_active=True,
        )

        db.add(admin_user)
        db.flush()

        logger.info(f"Admin user created: admin_id={admin_user.id}, email={email}, role={role}")

        return admin_user

    @staticmethod
    def authenticate_admin(
        email: str,
        password: str,
        db: Session,
    ) -> Optional[AdminUser]:
        """
        Authenticate an admin user.

        Args:
            email: Admin email address
            password: Plain text password
            db: Database session

        Returns:
            AdminUser if authentication successful, None otherwise
        """
        admin_user = db.query(AdminUser).filter(AdminUser.email == email).first()

        if not admin_user:
            logger.warning(f"Admin authentication failed: email {email} not found")
            return None

        if not verify_password(password, admin_user.hashed_password):
            logger.warning(f"Admin authentication failed: invalid password for {email}")
            return None

        if not admin_user.is_active:
            logger.warning(f"Admin authentication failed: account inactive for {email}")
            return None

        # Update last login
        admin_user.last_login = datetime.utcnow()
        db.flush()

        logger.info(f"Admin authenticated successfully: admin_id={admin_user.id}, email={email}")

        return admin_user

    @staticmethod
    def get_admin_by_id(admin_id: int, db: Session) -> Optional[AdminUser]:
        """
        Get admin user by ID.

        Args:
            admin_id: Admin user ID
            db: Database session

        Returns:
            AdminUser if found, None otherwise
        """
        return db.query(AdminUser).filter(AdminUser.id == admin_id).first()

    @staticmethod
    def create_access_token_for_admin(admin_user: AdminUser) -> str:
        """
        Create JWT access token for admin user.

        Args:
            admin_user: AdminUser instance

        Returns:
            JWT token string
        """
        from datetime import timedelta

        from app.config import settings

        data = {
            "sub": str(admin_user.id),
            "email": admin_user.email,
            "role": admin_user.role.value,
        }

        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

        return create_access_token(data=data, expires_delta=expires_delta)

    @staticmethod
    def log_admin_action(
        admin_id: int,
        action_type: str,
        entity_type: str,
        entity_id: int,
        details: Optional[dict] = None,
        db: Session = None,
    ) -> AdminActionLog:
        """
        Log an admin action for audit trail.

        Args:
            admin_id: Admin user ID who performed the action
            action_type: Type of action (e.g., "approve_deposit", "block_user")
            entity_type: Type of entity affected (e.g., "deposit", "user", "bet")
            entity_id: ID of the affected entity
            details: Additional context/details about the action (dict, will be JSON encoded)
            db: Database session

        Returns:
            Created AdminActionLog object

        Raises:
            ValueError: If database session is not provided
        """
        if db is None:
            raise ValueError("Database session is required")

        # Convert details dict to JSON string if provided
        details_json = None
        if details:
            try:
                details_json = json.dumps(details)
            except (TypeError, ValueError) as e:
                logger.warning(f"Failed to serialize details to JSON: {e}")
                details_json = str(details)

        log_entry = AdminActionLog(
            admin_id=admin_id,
            action_type=action_type,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details_json,
        )

        db.add(log_entry)
        db.flush()

        logger.info(
            f"Admin action logged: admin_id={admin_id}, action={action_type}, "
            f"entity={entity_type}:{entity_id}"
        )

        return log_entry

    @staticmethod
    def check_role_permission(
        admin_user: AdminUser,
        required_role: AdminRole,
    ) -> bool:
        """
        Check if admin user has required role permission.

        Super admins have all permissions.

        Args:
            admin_user: AdminUser instance
            required_role: Required role level

        Returns:
            True if admin has permission, False otherwise
        """
        if admin_user.role == AdminRole.SUPER_ADMIN:
            return True

        role_hierarchy = {
            AdminRole.SUPER_ADMIN: 3,
            AdminRole.ADMIN: 2,
            AdminRole.SUPPORT: 1,
        }

        admin_level = role_hierarchy.get(admin_user.role, 0)
        required_level = role_hierarchy.get(required_role, 0)

        return admin_level >= required_level
