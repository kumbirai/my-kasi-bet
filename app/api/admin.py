"""
Admin API endpoints.

This module provides REST API endpoints for admin operations including
authentication, deposit approval/rejection, and withdrawal approval/rejection.
"""
import logging
from datetime import datetime, timedelta
from typing import List

from decimal import Decimal
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin, get_db_session
from app.models.admin import AdminUser
from app.models.deposit import Deposit, DepositStatus, PaymentMethod
from app.models.match import Match, MatchResult, MatchStatus
from app.models.user import User
from app.models.withdrawal import Withdrawal, WithdrawalStatus
from app.schemas.admin import PaginatedResponse
from app.schemas.deposit import (
    AdminDepositCreate,
    DepositApproval,
    DepositRejection,
    DepositResponse,
)
from app.schemas.withdrawal import (
    WithdrawalApproval,
    WithdrawalRejection,
    WithdrawalResponse,
)
from app.services.admin_service import AdminService
from app.services.deposit_service import deposit_service
from app.services.games.football_yesno import FootballYesNoGame
from app.services.withdrawal_service import withdrawal_service
from app.utils.security import create_access_token, verify_password

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])


class AdminLogin(BaseModel):
    """Schema for admin login request."""

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Schema for token response."""

    access_token: str
    token_type: str = "bearer"


@router.post("/login", response_model=TokenResponse)
def admin_login(login: AdminLogin, db: Session = Depends(get_db_session)):
    """
    Admin login endpoint.

    Authenticates admin user and returns JWT token.

    Args:
        login: Login credentials
        db: Database session

    Returns:
        TokenResponse with access token

    Raises:
        HTTPException: If authentication fails
    """
    admin = db.query(AdminUser).filter(AdminUser.email == login.email).first()

    if not admin or not verify_password(login.password, admin.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    if not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin account is inactive",
        )

    # Create access token
    access_token = create_access_token(
        data={"sub": str(admin.id), "role": admin.role.value},
        expires_delta=timedelta(hours=24),
    )

    # Update last login
    admin.last_login = datetime.utcnow()
    db.commit()

    return {"access_token": access_token}


@router.get("/deposits/pending", response_model=List[DepositResponse])
def get_pending_deposits(
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db_session),
):
    """
    Get all pending deposit requests.

    Args:
        current_admin: Current authenticated admin
        db: Database session

    Returns:
        List of pending deposits
    """
    deposits = deposit_service.get_pending_deposits(db, limit=100)
    return deposits


@router.get("/deposits")
def list_deposits(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    status: Optional[DepositStatus] = Query(None, description="Filter by status"),
    payment_method: Optional[PaymentMethod] = Query(
        None, description="Filter by payment method"
    ),
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db_session),
):
    """
    List all deposits with pagination and filtering.

    Args:
        page: Page number (starting from 1)
        page_size: Number of items per page (1-100)
        status: Filter by deposit status
        payment_method: Filter by payment method
        current_admin: Current authenticated admin
        db: Database session

    Returns:
        Paginated list of deposits
    """
    # Build query
    query = db.query(Deposit).join(User, Deposit.user_id == User.id)

    # Apply filters
    if status:
        query = query.filter(Deposit.status == status)

    if payment_method:
        query = query.filter(Deposit.payment_method == payment_method)

    # Get total count
    total = query.count()

    # Apply pagination
    offset = (page - 1) * page_size
    deposits = (
        query.order_by(Deposit.created_at.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )

    # Build response
    deposit_list = [
        DepositResponse(
            id=d.id,
            user_id=d.user_id,
            amount=d.amount,
            payment_method=d.payment_method,
            status=d.status,
            proof_type=d.proof_type,
            proof_value=d.proof_value,
            created_at=d.created_at,
            reviewed_at=d.reviewed_at,
            rejection_reason=d.rejection_reason,
        )
        for d in deposits
    ]

    total_pages = PaginatedResponse.calculate_total_pages(total, page_size)

    return {
        "deposits": deposit_list,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


@router.post("/deposits", response_model=DepositResponse, status_code=status.HTTP_201_CREATED)
async def create_deposit(
    deposit_data: AdminDepositCreate,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db_session),
):
    """
    Create a new deposit request (admin-initiated).

    This endpoint allows admins to create deposits on behalf of users,
    typically when a bank transfer with reference number is received.

    Args:
        deposit_data: Deposit creation data
        current_admin: Current authenticated admin
        db: Database session

    Returns:
        Created Deposit object

    Raises:
        HTTPException: If user not found or validation fails
    """
    # Verify user exists
    user = db.query(User).filter(User.id == deposit_data.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {deposit_data.user_id} not found",
        )

    try:
        # Create deposit request
        deposit = deposit_service.create_deposit_request(
            user_id=deposit_data.user_id,
            amount=deposit_data.amount,
            payment_method=deposit_data.payment_method,
            proof_type=deposit_data.proof_type,
            proof_value=deposit_data.proof_value,
            notes=deposit_data.notes,
            db=db,
        )
        db.flush()

        # Auto-approve if requested
        if deposit_data.auto_approve:
            deposit = await deposit_service.approve_deposit(
                deposit_id=deposit.id,
                admin_user_id=current_admin.id,
                db=db,
            )

        db.commit()

        # Log admin action
        action_type = "create_deposit_approved" if deposit_data.auto_approve else "create_deposit"
        AdminService.log_admin_action(
            admin_id=current_admin.id,
            action_type=action_type,
            entity_type="deposit",
            entity_id=deposit.id,
            details={
                "user_id": deposit_data.user_id,
                "amount": str(deposit_data.amount),
                "payment_method": deposit_data.payment_method.value,
                "proof_type": deposit_data.proof_type,
                "proof_value": deposit_data.proof_value,
                "auto_approved": deposit_data.auto_approve,
            },
            db=db,
        )
        db.commit()

        # Return deposit response
        return DepositResponse(
            id=deposit.id,
            user_id=deposit.user_id,
            amount=deposit.amount,
            payment_method=deposit.payment_method,
            status=deposit.status,
            proof_type=deposit.proof_type,
            proof_value=deposit.proof_value,
            created_at=deposit.created_at,
            reviewed_at=deposit.reviewed_at,
            rejection_reason=deposit.rejection_reason,
        )

    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating deposit: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create deposit",
        )


@router.post("/deposits/approve")
async def approve_deposit(
    approval: DepositApproval,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db_session),
):
    """
    Approve a deposit request.

    Args:
        approval: Deposit approval request
        current_admin: Current authenticated admin
        db: Database session

    Returns:
        Success message with deposit ID

    Raises:
        HTTPException: If deposit not found or not pending
    """
    try:
        deposit = await deposit_service.approve_deposit(
            deposit_id=approval.deposit_id,
            admin_user_id=current_admin.id,
            db=db,
        )
        db.commit()

        # Log admin action
        AdminService.log_admin_action(
            admin_id=current_admin.id,
            action_type="approve_deposit",
            entity_type="deposit",
            entity_id=deposit.id,
            details={"amount": str(deposit.amount), "user_id": deposit.user_id},
            db=db,
        )

        return {
            "message": "Deposit approved successfully",
            "deposit_id": deposit.id,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/deposits/reject")
async def reject_deposit(
    rejection: DepositRejection,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db_session),
):
    """
    Reject a deposit request.

    Args:
        rejection: Deposit rejection request
        current_admin: Current authenticated admin
        db: Database session

    Returns:
        Success message with deposit ID

    Raises:
        HTTPException: If deposit not found or not pending
    """
    try:
        deposit = await deposit_service.reject_deposit(
            deposit_id=rejection.deposit_id,
            admin_user_id=current_admin.id,
            rejection_reason=rejection.rejection_reason,
            db=db,
        )
        db.commit()

        # Log admin action
        AdminService.log_admin_action(
            admin_id=current_admin.id,
            action_type="reject_deposit",
            entity_type="deposit",
            entity_id=deposit.id,
            details={
                "amount": str(deposit.amount),
                "user_id": deposit.user_id,
                "reason": rejection.rejection_reason,
            },
            db=db,
        )

        return {
            "message": "Deposit rejected successfully",
            "deposit_id": deposit.id,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/withdrawals/pending", response_model=List[WithdrawalResponse])
def get_pending_withdrawals(
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db_session),
):
    """
    Get all pending withdrawal requests.

    Args:
        current_admin: Current authenticated admin
        db: Database session

    Returns:
        List of pending withdrawals
    """
    withdrawals = withdrawal_service.get_pending_withdrawals(db, limit=100)
    return withdrawals


@router.get("/withdrawals")
def list_withdrawals(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    status: Optional[WithdrawalStatus] = Query(None, description="Filter by status"),
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db_session),
):
    """
    List all withdrawals with pagination and filtering.

    Args:
        page: Page number (starting from 1)
        page_size: Number of items per page (1-100)
        status: Filter by withdrawal status
        current_admin: Current authenticated admin
        db: Database session

    Returns:
        Paginated list of withdrawals
    """
    # Build query
    query = db.query(Withdrawal).join(User, Withdrawal.user_id == User.id)

    # Apply filters
    if status:
        query = query.filter(Withdrawal.status == status)

    # Get total count
    total = query.count()

    # Apply pagination
    offset = (page - 1) * page_size
    withdrawals = (
        query.order_by(Withdrawal.created_at.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )

    # Build response
    withdrawal_list = [
        WithdrawalResponse(
            id=w.id,
            user_id=w.user_id,
            amount=w.amount,
            withdrawal_method=w.withdrawal_method,
            bank_name=w.bank_name,
            account_number=w.account_number,
            account_holder=w.account_holder,
            status=w.status,
            created_at=w.created_at,
            reviewed_at=w.reviewed_at,
            rejection_reason=w.rejection_reason,
            payment_reference=w.payment_reference,
        )
        for w in withdrawals
    ]

    total_pages = PaginatedResponse.calculate_total_pages(total, page_size)

    return {
        "withdrawals": withdrawal_list,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


@router.post("/withdrawals/approve")
async def approve_withdrawal(
    approval: WithdrawalApproval,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db_session),
):
    """
    Approve a withdrawal request.

    Args:
        approval: Withdrawal approval request
        current_admin: Current authenticated admin
        db: Database session

    Returns:
        Success message with withdrawal ID

    Raises:
        HTTPException: If withdrawal not found or not pending
    """
    try:
        withdrawal = await withdrawal_service.approve_withdrawal(
            withdrawal_id=approval.withdrawal_id,
            admin_user_id=current_admin.id,
            payment_reference=approval.payment_reference,
            db=db,
        )
        db.commit()

        # Log admin action
        AdminService.log_admin_action(
            admin_id=current_admin.id,
            action_type="approve_withdrawal",
            entity_type="withdrawal",
            entity_id=withdrawal.id,
            details={
                "amount": str(withdrawal.amount),
                "user_id": withdrawal.user_id,
                "payment_reference": approval.payment_reference,
            },
            db=db,
        )

        return {
            "message": "Withdrawal approved successfully",
            "withdrawal_id": withdrawal.id,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/withdrawals/reject")
async def reject_withdrawal(
    rejection: WithdrawalRejection,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db_session),
):
    """
    Reject a withdrawal request.

    Args:
        rejection: Withdrawal rejection request
        current_admin: Current authenticated admin
        db: Database session

    Returns:
        Success message with withdrawal ID

    Raises:
        HTTPException: If withdrawal not found or not pending
    """
    try:
        withdrawal = await withdrawal_service.reject_withdrawal(
            withdrawal_id=rejection.withdrawal_id,
            admin_user_id=current_admin.id,
            rejection_reason=rejection.rejection_reason,
            db=db,
        )
        db.commit()

        # Log admin action
        AdminService.log_admin_action(
            admin_id=current_admin.id,
            action_type="reject_withdrawal",
            entity_type="withdrawal",
            entity_id=withdrawal.id,
            details={
                "amount": str(withdrawal.amount),
                "user_id": withdrawal.user_id,
                "reason": rejection.rejection_reason,
            },
            db=db,
        )

        return {
            "message": "Withdrawal rejected successfully",
            "withdrawal_id": withdrawal.id,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# Match management endpoints


class CreateMatchRequest(BaseModel):
    """Schema for creating a match."""

    home_team: str
    away_team: str
    event_description: str
    yes_odds: Decimal
    no_odds: Decimal
    match_time: datetime | None = None


class SettleMatchRequest(BaseModel):
    """Schema for settling a match."""

    result: str  # "yes" or "no"


class MatchResponse(BaseModel):
    """Schema for match response."""

    id: int
    home_team: str
    away_team: str
    event_description: str
    yes_odds: float
    no_odds: float
    status: str
    result: str | None
    created_at: str
    settled_at: str | None

    class Config:
        """Pydantic config."""

        from_attributes = True


@router.post("/matches", response_model=dict)
def create_match(
    request: CreateMatchRequest,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db_session),
):
    """
    Create a new football match (admin only).

    Args:
        request: Match creation request
        current_admin: Current authenticated admin
        db: Database session

    Returns:
        Success message with match ID
    """
    try:
        match = FootballYesNoGame.create_match(
            home_team=request.home_team,
            away_team=request.away_team,
            event_description=request.event_description,
            yes_odds=request.yes_odds,
            no_odds=request.no_odds,
            match_time=request.match_time,
            db=db,
        )

        return {
            "success": True,
            "match_id": match.id,
            "message": "Match created successfully",
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/matches", response_model=List[MatchResponse])
def get_matches(
    status: str | None = None,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db_session),
):
    """
    Get all matches.

    Args:
        status: Optional status filter (active, settled, cancelled)
        current_admin: Current authenticated admin
        db: Database session

    Returns:
        List of matches
    """
    query = db.query(Match)

    if status:
        try:
            match_status = MatchStatus(status)
            query = query.filter(Match.status == match_status)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status}")

    matches = query.order_by(Match.created_at.desc()).limit(50).all()

    return [
        MatchResponse(
            id=m.id,
            home_team=m.home_team,
            away_team=m.away_team,
            event_description=m.event_description,
            yes_odds=float(m.yes_odds),
            no_odds=float(m.no_odds),
            status=m.status.value,
            result=m.result.value if m.result else None,
            created_at=m.created_at.isoformat(),
            settled_at=m.settled_at.isoformat() if m.settled_at else None,
        )
        for m in matches
    ]


@router.post("/matches/{match_id}/settle", response_model=dict)
def settle_match(
    match_id: int,
    request: SettleMatchRequest,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db_session),
):
    """
    Settle a match (admin only).

    Args:
        match_id: Match ID to settle
        request: Settlement request with result
        current_admin: Current authenticated admin
        db: Database session

    Returns:
        Success message with settled bets count
    """
    try:
        result = (
            MatchResult.YES if request.result.lower() == "yes" else MatchResult.NO
        )

        settled_bets = FootballYesNoGame.settle_match(
            match_id=match_id,
            result=result,
            db=db,
        )

        return {
            "success": True,
            "match_id": match_id,
            "result": result.value,
            "settled_bets": len(settled_bets),
            "message": f"Match settled as {result.value.upper()}",
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
