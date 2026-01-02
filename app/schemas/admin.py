"""
Admin Pydantic schemas.

This module defines Pydantic schemas for admin operations including
authentication, user management, and action logging.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from app.models.admin import AdminRole


class AdminUserCreate(BaseModel):
    """
    Schema for creating a new admin user.

    Attributes:
        email: Admin email address
        password: Plain text password (min 8 characters)
        full_name: Admin full name
        role: Admin role (default: SUPPORT)
    """

    email: EmailStr
    password: str = Field(..., min_length=8, description="Password (min 8 characters)")
    full_name: str = Field(..., min_length=2, max_length=100)
    role: AdminRole = AdminRole.SUPPORT


class AdminUserLogin(BaseModel):
    """
    Schema for admin login request.

    Attributes:
        email: Admin email address
        password: Plain text password
    """

    email: EmailStr
    password: str


class AdminUserResponse(BaseModel):
    """
    Schema for admin user response data.

    Attributes:
        id: Admin user ID
        email: Admin email address
        full_name: Admin full name
        role: Admin role
        is_active: Whether admin account is active
        last_login: Last login timestamp
        created_at: Creation timestamp
    """

    id: int
    email: str
    full_name: str
    role: AdminRole
    is_active: bool
    last_login: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    """
    Schema for JWT token response.

    Attributes:
        access_token: JWT access token
        token_type: Token type (always "bearer")
    """

    access_token: str
    token_type: str = "bearer"


class AdminActionLogResponse(BaseModel):
    """
    Schema for admin action log response data.

    Attributes:
        id: Log entry ID
        admin_id: Admin user ID who performed the action
        admin_email: Admin email (for display)
        action_type: Type of action
        entity_type: Type of entity affected
        entity_id: ID of the affected entity
        details: Additional context (JSON string)
        created_at: Timestamp when action was logged
    """

    id: int
    admin_id: int
    admin_email: Optional[str] = None
    action_type: str
    entity_type: str
    entity_id: int
    details: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class PaginatedResponse(BaseModel):
    """
    Base schema for paginated responses.

    Attributes:
        total: Total number of items
        page: Current page number
        page_size: Number of items per page
        total_pages: Total number of pages
    """

    total: int
    page: int
    page_size: int
    total_pages: int

    @classmethod
    def calculate_total_pages(cls, total: int, page_size: int) -> int:
        """
        Calculate total pages.

        Args:
            total: Total number of items
            page_size: Number of items per page

        Returns:
            Total number of pages
        """
        if page_size <= 0:
            return 0
        return (total + page_size - 1) // page_size
