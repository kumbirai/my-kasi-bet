"""
Withdrawal Pydantic schemas.

This module defines Pydantic schemas for withdrawal operations.
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field

from app.models.withdrawal import WithdrawalMethod, WithdrawalStatus


class WithdrawalCreate(BaseModel):
    """
    Schema for creating a withdrawal request.

    Attributes:
        amount: Withdrawal amount (must be positive)
        withdrawal_method: Withdrawal method
        bank_name: Bank name (for bank transfer)
        account_number: Account number
        account_holder: Account holder name
        notes: Additional notes
    """

    amount: Decimal = Field(..., gt=0)
    withdrawal_method: WithdrawalMethod
    bank_name: Optional[str] = Field(None, max_length=100)
    account_number: Optional[str] = Field(None, max_length=50)
    account_holder: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = Field(None, max_length=500)


class WithdrawalResponse(BaseModel):
    """
    Schema for withdrawal response data.

    Attributes:
        id: Withdrawal ID
        user_id: User ID
        amount: Withdrawal amount
        withdrawal_method: Withdrawal method
        status: Withdrawal status
        bank_name: Bank name
        account_number: Account number
        account_holder: Account holder name
        created_at: Creation timestamp
        reviewed_at: Review timestamp (if reviewed)
        rejection_reason: Rejection reason (if rejected)
        payment_reference: Payment reference (if approved)
    """

    id: int
    user_id: int
    amount: Decimal
    withdrawal_method: WithdrawalMethod
    status: WithdrawalStatus
    bank_name: Optional[str]
    account_number: Optional[str]
    account_holder: Optional[str]
    created_at: datetime
    reviewed_at: Optional[datetime]
    rejection_reason: Optional[str]
    payment_reference: Optional[str]

    model_config = {"from_attributes": True}


class WithdrawalApproval(BaseModel):
    """
    Schema for withdrawal approval request.

    Attributes:
        withdrawal_id: Withdrawal ID to approve
        admin_user_id: Admin user ID approving (set by auth)
        payment_reference: Optional payment reference
    """

    withdrawal_id: int
    payment_reference: Optional[str] = None


class WithdrawalRejection(BaseModel):
    """
    Schema for withdrawal rejection request.

    Attributes:
        withdrawal_id: Withdrawal ID to reject
        admin_user_id: Admin user ID rejecting (set by auth)
        rejection_reason: Reason for rejection (10-200 characters)
    """

    withdrawal_id: int
    rejection_reason: str = Field(..., min_length=10, max_length=200)
