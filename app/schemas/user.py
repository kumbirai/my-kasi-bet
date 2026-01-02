"""
User Pydantic schemas.

This module defines Pydantic schemas for user-related operations.
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class UserBase(BaseModel):
    """
    Base user schema with common fields.

    Attributes:
        phone_number: User's phone number (10-20 characters)
        username: Optional username (max 50 characters)
    """

    phone_number: str = Field(..., min_length=10, max_length=20)
    username: Optional[str] = Field(None, max_length=50)


class UserCreate(UserBase):
    """
    Schema for creating a new user.

    Inherits from UserBase with all required fields.
    """

    pass


class UserResponse(UserBase):
    """
    Schema for user response data.

    Attributes:
        id: User ID
        is_active: Whether user is active
        is_blocked: Whether user is blocked
        created_at: Creation timestamp
        last_active: Last activity timestamp
    """

    id: int
    is_active: bool
    is_blocked: bool
    created_at: datetime
    last_active: datetime

    model_config = {"from_attributes": True}


class WalletResponse(BaseModel):
    """
    Schema for wallet response data.

    Attributes:
        id: Wallet ID
        user_id: Associated user ID
        balance: Current balance
        updated_at: Last update timestamp
    """

    id: int
    user_id: int
    balance: Decimal
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserWithWallet(UserResponse):
    """
    Schema for user response with wallet information.

    Attributes:
        wallet: Optional wallet information
    """

    wallet: Optional[WalletResponse] = None
