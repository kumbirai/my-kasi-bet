"""
Admin User Management API endpoints.

This module provides REST API endpoints for managing users including
listing, viewing details, and blocking/unblocking users.
"""
import logging
from decimal import Decimal
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin, get_db_session
from app.models.admin import AdminUser
from app.models.bet import Bet, BetStatus, BetType
from app.models.deposit import Deposit, DepositStatus
from app.models.user import User
from app.models.wallet import Wallet
from app.models.withdrawal import Withdrawal, WithdrawalStatus
from app.schemas.admin import PaginatedResponse
from app.services.admin_service import AdminService
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin/users", tags=["admin-users"])


class UserListItem(BaseModel):
    """Schema for user list item."""

    id: int
    phone_number: str
    is_active: bool
    is_blocked: bool
    created_at: str
    wallet_balance: float


class UserListResponse(BaseModel):
    """Schema for paginated user list response."""

    users: List[UserListItem]
    total: int
    page: int
    page_size: int
    total_pages: int


class UserDetailResponse(BaseModel):
    """Schema for user detail response."""

    id: int
    phone_number: str
    is_active: bool
    is_blocked: bool
    created_at: str
    wallet_balance: float
    total_deposits: float
    total_withdrawals: float
    total_bets: int
    total_wagered: float
    total_winnings: float


class BlockUserRequest(BaseModel):
    """Schema for block user request."""

    reason: str = ""


@router.get("")
def list_users(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search by phone number"),
    is_blocked: Optional[bool] = Query(None, description="Filter by blocked status"),
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db_session),
):
    """
    List all users with pagination and filtering.

    Args:
        page: Page number (starting from 1)
        page_size: Number of items per page (1-100)
        search: Search term for phone number
        is_blocked: Filter by blocked status
        current_admin: Current authenticated admin
        db: Database session

    Returns:
        Paginated list of users
    """
    # Build query
    query = db.query(User).join(Wallet, User.id == Wallet.user_id)

    # Apply filters
    if search:
        query = query.filter(User.phone_number.contains(search))

    if is_blocked is not None:
        query = query.filter(User.is_blocked == is_blocked)

    # Get total count
    total = query.count()

    # Apply pagination
    offset = (page - 1) * page_size
    users = (
        query.order_by(User.created_at.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )

    # Build response
    user_list = []
    for user in users:
        wallet = db.query(Wallet).filter(Wallet.user_id == user.id).first()
        user_list.append(
            {
                "id": user.id,
                "phone_number": user.phone_number,
                "is_active": user.is_active,
                "is_blocked": user.is_blocked,
                "created_at": user.created_at.isoformat(),
                "wallet_balance": float(wallet.balance) if wallet else 0.0,
            }
        )

    total_pages = PaginatedResponse.calculate_total_pages(total, page_size)

    return UserListResponse(
        users=[UserListItem(**user) for user in user_list],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/{user_id}", response_model=UserDetailResponse)
def get_user_details(
    user_id: int,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db_session),
):
    """
    Get detailed information about a specific user.

    Args:
        user_id: User ID
        current_admin: Current authenticated admin
        db: Database session

    Returns:
        User details with statistics

    Raises:
        HTTPException: If user not found
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Get wallet
    wallet = db.query(Wallet).filter(Wallet.user_id == user_id).first()
    wallet_balance = wallet.balance if wallet else Decimal("0.00")

    # Get deposit total
    total_deposits = (
        db.query(func.sum(Deposit.amount))
        .filter(
            Deposit.user_id == user_id,
            Deposit.status == DepositStatus.APPROVED,
        )
        .scalar()
        or Decimal("0.00")
    )

    # Get withdrawal total
    total_withdrawals = (
        db.query(func.sum(Withdrawal.amount))
        .filter(
            Withdrawal.user_id == user_id,
            Withdrawal.status == WithdrawalStatus.APPROVED,
        )
        .scalar()
        or Decimal("0.00")
    )

    # Get bet statistics
    total_bets = db.query(func.count(Bet.id)).filter(Bet.user_id == user_id).scalar()

    total_wagered = (
        db.query(func.sum(Bet.stake_amount))
        .filter(Bet.user_id == user_id)
        .scalar()
        or Decimal("0.00")
    )

    total_winnings = (
        db.query(func.sum(Bet.payout_amount))
        .filter(
            Bet.user_id == user_id,
            Bet.status == BetStatus.WON,
        )
        .scalar()
        or Decimal("0.00")
    )

    return UserDetailResponse(
        id=user.id,
        phone_number=user.phone_number,
        is_active=user.is_active,
        is_blocked=user.is_blocked,
        created_at=user.created_at.isoformat(),
        wallet_balance=float(wallet_balance),
        total_deposits=float(total_deposits),
        total_withdrawals=float(total_withdrawals),
        total_bets=total_bets,
        total_wagered=float(total_wagered),
        total_winnings=float(total_winnings),
    )


@router.post("/{user_id}/block")
def block_user(
    user_id: int,
    request: BlockUserRequest,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db_session),
):
    """
    Block a user from placing bets.

    Args:
        user_id: User ID to block
        request: Request body with reason
        current_admin: Current authenticated admin
        db: Database session

    Returns:
        Success message

    Raises:
        HTTPException: If user not found or already blocked
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if user.is_blocked:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User is already blocked"
        )

    reason = request.reason or "No reason provided"

    user.is_blocked = True
    db.commit()

    # Log admin action
    AdminService.log_admin_action(
        admin_id=current_admin.id,
        action_type="block_user",
        entity_type="user",
        entity_id=user_id,
        details={"reason": reason, "phone_number": user.phone_number},
        db=db,
    )

    logger.info(
        f"User blocked: user_id={user_id}, admin_id={current_admin.id}, reason={reason}"
    )

    return {"message": "User blocked successfully", "user_id": user_id}


@router.post("/{user_id}/unblock")
def unblock_user(
    user_id: int,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db_session),
):
    """
    Unblock a user.

    Args:
        user_id: User ID to unblock
        current_admin: Current authenticated admin
        db: Database session

    Returns:
        Success message

    Raises:
        HTTPException: If user not found or not blocked
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if not user.is_blocked:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User is not blocked"
        )

    user.is_blocked = False
    db.commit()

    # Log admin action
    AdminService.log_admin_action(
        admin_id=current_admin.id,
        action_type="unblock_user",
        entity_type="user",
        entity_id=user_id,
        details={"phone_number": user.phone_number},
        db=db,
    )

    logger.info(f"User unblocked: user_id={user_id}, admin_id={current_admin.id}")

    return {"message": "User unblocked successfully", "user_id": user_id}
