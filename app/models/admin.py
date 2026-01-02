"""
Admin user domain model.

This module defines the AdminUser model representing administrative users
with role-based access control.
"""
import enum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, DateTime, Enum as SQLEnum, Integer, String, func

from app.database import Base

if TYPE_CHECKING:
    pass


class AdminRole(str, enum.Enum):
    """Admin user roles."""

    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    SUPPORT = "support"


class AdminUser(Base):
    """
    Admin user model representing an administrative user.

    This model tracks admin users who can approve deposits and withdrawals,
    manage users, and perform other administrative tasks.

    Attributes:
        id: Primary key identifier
        email: Unique email address
        hashed_password: Hashed password (bcrypt)
        full_name: Full name of admin
        role: Admin role (super_admin, admin, support)
        is_active: Whether admin account is active
        created_at: Timestamp when admin was created
        last_login: Timestamp of last login
    """

    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True, index=True)

    # Authentication
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(200), nullable=False)

    # Profile
    full_name = Column(String(100), nullable=False)
    role = Column(
        SQLEnum(AdminRole), default=AdminRole.SUPPORT, nullable=False
    )

    # Status
    is_active = Column(Boolean, default=True, nullable=False)

    # Timestamps
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    last_login = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:
        """String representation of AdminUser instance."""
        return (
            f"<AdminUser(id={self.id}, email={self.email}, role={self.role})>"
        )
