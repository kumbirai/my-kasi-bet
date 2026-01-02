"""
Deposit Pydantic schemas.

This module defines Pydantic schemas for deposit operations.
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field

from app.models.deposit import DepositStatus, PaymentMethod


class DepositCreate(BaseModel):
    """
    Schema for creating a deposit request.

    Attributes:
        amount: Deposit amount (must be positive)
        payment_method: Payment method used
        proof_type: Type of proof (reference_number, image_url)
        proof_value: Actual proof value
        notes: Additional notes
    """

    amount: Decimal = Field(..., gt=0, description="Deposit amount")
    payment_method: PaymentMethod
    proof_type: Optional[str] = Field(None, max_length=20)
    proof_value: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = Field(None, max_length=500)


class DepositResponse(BaseModel):
    """
    Schema for deposit response data.

    Attributes:
        id: Deposit ID
        user_id: User ID
        amount: Deposit amount
        payment_method: Payment method used
        status: Deposit status
        proof_type: Type of proof
        proof_value: Proof value
        created_at: Creation timestamp
        reviewed_at: Review timestamp (if reviewed)
        rejection_reason: Rejection reason (if rejected)
    """

    id: int
    user_id: int
    amount: Decimal
    payment_method: PaymentMethod
    status: DepositStatus
    proof_type: Optional[str]
    proof_value: Optional[str]
    created_at: datetime
    reviewed_at: Optional[datetime]
    rejection_reason: Optional[str]

    model_config = {"from_attributes": True}


class DepositApproval(BaseModel):
    """
    Schema for deposit approval request.

    Attributes:
        deposit_id: Deposit ID to approve
        admin_user_id: Admin user ID approving (set by auth)
    """

    deposit_id: int


class DepositRejection(BaseModel):
    """
    Schema for deposit rejection request.

    Attributes:
        deposit_id: Deposit ID to reject
        admin_user_id: Admin user ID rejecting (set by auth)
        rejection_reason: Reason for rejection (10-200 characters)
    """

    deposit_id: int
    rejection_reason: str = Field(..., min_length=10, max_length=200)


class AdminDepositCreate(BaseModel):
    """
    Schema for admin-created deposit request.

    Attributes:
        user_id: User ID to create deposit for
        amount: Deposit amount (must be positive)
        payment_method: Payment method used
        proof_type: Type of proof (reference_number, image_url)
        proof_value: Actual proof value (e.g., bank reference number)
        notes: Additional notes
        auto_approve: Whether to automatically approve the deposit (default: False)
    """

    user_id: int = Field(..., description="User ID to create deposit for")
    amount: Decimal = Field(..., gt=0, description="Deposit amount")
    payment_method: PaymentMethod
    proof_type: Optional[str] = Field(
        None, max_length=20, description="Type of proof (e.g., 'reference_number')"
    )
    proof_value: Optional[str] = Field(
        None, max_length=500, description="Proof value (e.g., bank reference number)"
    )
    notes: Optional[str] = Field(None, max_length=500, description="Additional notes")
    auto_approve: bool = Field(
        False, description="Whether to automatically approve the deposit"
    )
