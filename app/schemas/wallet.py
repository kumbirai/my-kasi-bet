"""
Wallet Pydantic schemas.

This module defines Pydantic schemas for wallet and transaction operations.
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class TransactionBase(BaseModel):
    """
    Base transaction schema with common fields.

    Attributes:
        type: Transaction type (deposit, withdrawal, bet, win, refund)
        amount: Transaction amount
        description: Optional description
    """

    type: str = Field(..., max_length=20)
    amount: Decimal = Field(..., gt=0)
    description: Optional[str] = Field(None, max_length=200)


class TransactionCreate(TransactionBase):
    """
    Schema for creating a new transaction.

    Attributes:
        user_id: User ID for the transaction
        reference_type: Optional reference type (deposit_id, withdrawal_id, bet_id)
        reference_id: Optional reference ID
    """

    user_id: int
    reference_type: Optional[str] = Field(None, max_length=20)
    reference_id: Optional[int] = None


class TransactionResponse(BaseModel):
    """
    Schema for transaction response data.

    Attributes:
        id: Transaction ID
        user_id: User ID
        type: Transaction type
        amount: Transaction amount
        balance_before: Balance before transaction
        balance_after: Balance after transaction
        description: Transaction description
        created_at: Creation timestamp
    """

    id: int
    user_id: int
    type: str
    amount: Decimal
    balance_before: Decimal
    balance_after: Decimal
    description: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class WalletBalanceResponse(BaseModel):
    """
    Schema for wallet balance response.

    Attributes:
        user_id: User ID
        balance: Current balance
        updated_at: Last update timestamp
    """

    user_id: int
    balance: Decimal
    updated_at: datetime

    model_config = {"from_attributes": True}


class TransactionHistoryResponse(BaseModel):
    """
    Schema for transaction history response.

    Attributes:
        transactions: List of transactions
        total: Total number of transactions
        limit: Limit used in query
        offset: Offset used in query
    """

    transactions: list[TransactionResponse]
    total: int
    limit: int
    offset: int
