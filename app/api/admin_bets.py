"""
Admin Bet Monitoring API endpoints.

This module provides REST API endpoints for monitoring bets including
listing, filtering, and statistics.
"""
import json
import logging
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin, get_db_session
from app.models.admin import AdminUser
from app.models.bet import Bet, BetStatus, BetType
from app.models.user import User
from app.schemas.admin import PaginatedResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin/bets", tags=["admin-bets"])


class BetResponse(BaseModel):
    """Schema for bet response."""

    id: int
    user_id: int
    user_phone: str
    bet_type: BetType
    stake_amount: float
    bet_data: dict
    status: BetStatus
    game_result: Optional[dict]
    multiplier: Optional[float]
    payout_amount: float
    created_at: str
    settled_at: Optional[str]

    class Config:
        """Pydantic config."""

        from_attributes = True


class BetListResponse(BaseModel):
    """Schema for paginated bet list response."""

    bets: List[BetResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class BetStatistics(BaseModel):
    """Schema for bet statistics."""

    total_bets: int
    active_bets: int
    settled_bets: int
    won_bets: int
    lost_bets: int
    total_wagered: float
    total_payouts: float
    net_revenue: float


@router.get("")
def list_bets(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    bet_type: Optional[BetType] = Query(None, description="Filter by bet type"),
    status: Optional[BetStatus] = Query(None, description="Filter by status"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    date_from: Optional[date] = Query(None, description="Filter from date"),
    date_to: Optional[date] = Query(None, description="Filter to date"),
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db_session),
):
    """
    List all bets with pagination and filtering.

    Args:
        page: Page number (starting from 1)
        page_size: Number of items per page (1-100)
        bet_type: Filter by bet type
        status: Filter by bet status
        user_id: Filter by user ID
        date_from: Filter from date
        date_to: Filter to date
        current_admin: Current authenticated admin
        db: Database session

    Returns:
        Paginated list of bets
    """
    # Build query
    query = db.query(Bet).join(User, Bet.user_id == User.id)

    # Apply filters
    if bet_type:
        query = query.filter(Bet.bet_type == bet_type)

    if status:
        query = query.filter(Bet.status == status)

    if user_id:
        query = query.filter(Bet.user_id == user_id)

    if date_from:
        query = query.filter(Bet.created_at >= datetime.combine(date_from, datetime.min.time()))

    if date_to:
        end_date = datetime.combine(date_to, datetime.max.time()) + timedelta(days=1)
        query = query.filter(Bet.created_at < end_date)

    # Get total count
    total = query.count()

    # Apply pagination
    offset = (page - 1) * page_size
    bets = (
        query.order_by(Bet.created_at.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )

    # Build response
    bet_list = []
    for bet in bets:
        user = db.query(User).filter(User.id == bet.user_id).first()

        # Parse JSON strings
        bet_data = {}
        game_result = None

        if bet.bet_data:
            try:
                bet_data = json.loads(bet.bet_data)
            except (json.JSONDecodeError, TypeError):
                bet_data = {}

        if bet.game_result:
            try:
                game_result = json.loads(bet.game_result)
            except (json.JSONDecodeError, TypeError):
                game_result = None

        bet_list.append(
            BetResponse(
                id=bet.id,
                user_id=bet.user_id,
                user_phone=user.phone_number if user else "Unknown",
                bet_type=bet.bet_type,
                stake_amount=float(bet.stake_amount),
                bet_data=bet_data,
                status=bet.status,
                game_result=game_result,
                multiplier=float(bet.multiplier) if bet.multiplier else None,
                payout_amount=float(bet.payout_amount),
                created_at=bet.created_at.isoformat(),
                settled_at=bet.settled_at.isoformat() if bet.settled_at else None,
            )
        )

    total_pages = PaginatedResponse.calculate_total_pages(total, page_size)

    return BetListResponse(
        bets=bet_list,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/active")
def list_active_bets(
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db_session),
):
    """
    Get all active (unsettled) bets.

    Args:
        current_admin: Current authenticated admin
        db: Database session

    Returns:
        List of active bets
    """
    bets = (
        db.query(Bet)
        .filter(Bet.status == BetStatus.PENDING)
        .order_by(Bet.created_at.desc())
        .all()
    )

    bet_list = []
    for bet in bets:
        user = db.query(User).filter(User.id == bet.user_id).first()

        bet_data = {}
        if bet.bet_data:
            try:
                bet_data = json.loads(bet.bet_data)
            except (json.JSONDecodeError, TypeError):
                bet_data = {}

        bet_list.append(
            BetResponse(
                id=bet.id,
                user_id=bet.user_id,
                user_phone=user.phone_number if user else "Unknown",
                bet_type=bet.bet_type,
                stake_amount=float(bet.stake_amount),
                bet_data=bet_data,
                status=bet.status,
                game_result=None,
                multiplier=None,
                payout_amount=0.0,
                created_at=bet.created_at.isoformat(),
                settled_at=None,
            )
        )

    return bet_list


@router.get("/statistics", response_model=BetStatistics)
def get_bet_statistics(
    bet_type: Optional[BetType] = Query(None, description="Filter by bet type"),
    date_from: Optional[date] = Query(None, description="Filter from date"),
    date_to: Optional[date] = Query(None, description="Filter to date"),
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db_session),
):
    """
    Get betting statistics.

    Args:
        bet_type: Filter by bet type
        date_from: Filter from date
        date_to: Filter to date
        current_admin: Current authenticated admin
        db: Database session

    Returns:
        Bet statistics
    """
    # Build base query
    query = db.query(Bet)

    # Apply filters
    if bet_type:
        query = query.filter(Bet.bet_type == bet_type)

    if date_from:
        query = query.filter(Bet.created_at >= datetime.combine(date_from, datetime.min.time()))

    if date_to:
        end_date = datetime.combine(date_to, datetime.max.time()) + timedelta(days=1)
        query = query.filter(Bet.created_at < end_date)

    # Total bets
    total_bets = query.count()

    # Active bets
    active_bets = query.filter(Bet.status == BetStatus.PENDING).count()

    # Settled bets
    settled_bets = total_bets - active_bets

    # Won bets
    won_bets = query.filter(Bet.status == BetStatus.WON).count()

    # Lost bets
    lost_bets = query.filter(Bet.status == BetStatus.LOST).count()

    # Total wagered
    total_wagered = (
        query.with_entities(func.sum(Bet.stake_amount)).scalar() or Decimal("0.00")
    )

    # Total payouts (only for won bets)
    total_payouts = (
        db.query(func.sum(Bet.payout_amount))
        .filter(Bet.status == BetStatus.WON)
        .scalar()
        or Decimal("0.00")
    )

    # Apply date filters to payout query if needed
    if date_from or date_to:
        payout_query = db.query(func.sum(Bet.payout_amount)).filter(
            Bet.status == BetStatus.WON
        )
        if date_from:
            payout_query = payout_query.filter(
                Bet.created_at >= datetime.combine(date_from, datetime.min.time())
            )
        if date_to:
            end_date = datetime.combine(date_to, datetime.max.time()) + timedelta(days=1)
            payout_query = payout_query.filter(Bet.created_at < end_date)
        total_payouts = payout_query.scalar() or Decimal("0.00")

    # Net revenue (stakes - payouts)
    net_revenue = total_wagered - total_payouts

    return BetStatistics(
        total_bets=total_bets,
        active_bets=active_bets,
        settled_bets=settled_bets,
        won_bets=won_bets,
        lost_bets=lost_bets,
        total_wagered=float(total_wagered),
        total_payouts=float(total_payouts),
        net_revenue=float(net_revenue),
    )
