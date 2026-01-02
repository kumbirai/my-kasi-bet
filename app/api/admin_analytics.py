"""
Admin Analytics & Reporting API endpoints.

This module provides REST API endpoints for analytics and reporting including
dashboard statistics, revenue breakdown, and user engagement metrics.
"""
import logging
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin, get_db_session
from app.models.admin import AdminUser
from app.models.bet import Bet, BetStatus, BetType
from app.models.deposit import Deposit, DepositStatus
from app.models.user import User
from app.models.withdrawal import Withdrawal, WithdrawalStatus

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin/analytics", tags=["admin-analytics"])


class DashboardStats(BaseModel):
    """Schema for dashboard statistics."""

    total_users: int
    active_users: int
    blocked_users: int
    total_deposits: float
    total_withdrawals: float
    pending_deposits: int
    pending_withdrawals: int
    total_bets: int
    active_bets: int
    total_wagered: float
    total_payouts: float
    net_revenue: float
    platform_balance: float


class RevenueBreakdown(BaseModel):
    """Schema for revenue breakdown by game type."""

    game_type: str
    total_wagered: float
    total_payouts: float
    net_revenue: float
    bet_count: int


class UserEngagementMetrics(BaseModel):
    """Schema for user engagement metrics."""

    total_users: int
    active_users_24h: int
    active_users_7d: int
    active_users_30d: int
    new_users_today: int
    new_users_7d: int
    new_users_30d: int
    average_bets_per_user: float
    average_deposit_per_user: float


@router.get("/dashboard", response_model=DashboardStats)
def get_dashboard_stats(
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db_session),
):
    """
    Get dashboard statistics.

    Args:
        current_admin: Current authenticated admin
        db: Database session

    Returns:
        Dashboard statistics
    """
    # User statistics
    total_users = db.query(func.count(User.id)).scalar()
    active_users = db.query(func.count(User.id)).filter(User.is_active == True).scalar()
    blocked_users = db.query(func.count(User.id)).filter(User.is_blocked == True).scalar()

    # Deposit statistics
    total_deposits = (
        db.query(func.sum(Deposit.amount))
        .filter(Deposit.status == DepositStatus.APPROVED)
        .scalar()
        or Decimal("0.00")
    )
    pending_deposits = (
        db.query(func.count(Deposit.id))
        .filter(Deposit.status == DepositStatus.PENDING)
        .scalar()
    )

    # Withdrawal statistics
    total_withdrawals = (
        db.query(func.sum(Withdrawal.amount))
        .filter(Withdrawal.status == WithdrawalStatus.APPROVED)
        .scalar()
        or Decimal("0.00")
    )
    pending_withdrawals = (
        db.query(func.count(Withdrawal.id))
        .filter(Withdrawal.status == WithdrawalStatus.PENDING)
        .scalar()
    )

    # Bet statistics
    total_bets = db.query(func.count(Bet.id)).scalar()
    active_bets = (
        db.query(func.count(Bet.id))
        .filter(Bet.status == BetStatus.PENDING)
        .scalar()
    )

    total_wagered = (
        db.query(func.sum(Bet.stake_amount)).scalar() or Decimal("0.00")
    )

    total_payouts = (
        db.query(func.sum(Bet.payout_amount))
        .filter(Bet.status == BetStatus.WON)
        .scalar()
        or Decimal("0.00")
    )

    # Net revenue (deposits - withdrawals - payouts)
    net_revenue = total_deposits - total_withdrawals - total_payouts

    # Platform balance (total deposits - total withdrawals - total payouts)
    platform_balance = net_revenue

    return DashboardStats(
        total_users=total_users,
        active_users=active_users,
        blocked_users=blocked_users,
        total_deposits=float(total_deposits),
        total_withdrawals=float(total_withdrawals),
        pending_deposits=pending_deposits,
        pending_withdrawals=pending_withdrawals,
        total_bets=total_bets,
        active_bets=active_bets,
        total_wagered=float(total_wagered),
        total_payouts=float(total_payouts),
        net_revenue=float(net_revenue),
        platform_balance=float(platform_balance),
    )


@router.get("/revenue")
def get_revenue_breakdown(
    date_from: Optional[date] = Query(None, description="Filter from date"),
    date_to: Optional[date] = Query(None, description="Filter to date"),
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db_session),
):
    """
    Get revenue breakdown by game type.

    Args:
        date_from: Filter from date
        date_to: Filter to date
        current_admin: Current authenticated admin
        db: Database session

    Returns:
        Revenue breakdown by game type
    """
    # Build base query
    query = db.query(Bet)

    # Apply date filters
    if date_from:
        query = query.filter(
            Bet.created_at >= datetime.combine(date_from, datetime.min.time())
        )

    if date_to:
        end_date = datetime.combine(date_to, datetime.max.time()) + timedelta(days=1)
        query = query.filter(Bet.created_at < end_date)

    # Get revenue breakdown by game type
    breakdown: List[RevenueBreakdown] = []

    for bet_type in BetType:
        type_query = query.filter(Bet.bet_type == bet_type)

        bet_count = type_query.count()

        total_wagered = (
            type_query.with_entities(func.sum(Bet.stake_amount)).scalar()
            or Decimal("0.00")
        )

        total_payouts = (
            db.query(func.sum(Bet.payout_amount))
            .filter(Bet.bet_type == bet_type, Bet.status == BetStatus.WON)
            .scalar()
            or Decimal("0.00")
        )

        # Apply date filters to payout query if needed
        if date_from or date_to:
            payout_query = db.query(func.sum(Bet.payout_amount)).filter(
                Bet.bet_type == bet_type, Bet.status == BetStatus.WON
            )
            if date_from:
                payout_query = payout_query.filter(
                    Bet.created_at >= datetime.combine(date_from, datetime.min.time())
                )
            if date_to:
                end_date = datetime.combine(date_to, datetime.max.time()) + timedelta(
                    days=1
                )
                payout_query = payout_query.filter(Bet.created_at < end_date)
            total_payouts = payout_query.scalar() or Decimal("0.00")

        net_revenue = total_wagered - total_payouts

        breakdown.append(
            RevenueBreakdown(
                game_type=bet_type.value,
                total_wagered=float(total_wagered),
                total_payouts=float(total_payouts),
                net_revenue=float(net_revenue),
                bet_count=bet_count,
            )
        )

    return breakdown


@router.get("/users", response_model=UserEngagementMetrics)
def get_user_engagement_metrics(
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db_session),
):
    """
    Get user engagement metrics.

    Args:
        current_admin: Current authenticated admin
        db: Database session

    Returns:
        User engagement metrics
    """
    # Total users
    total_users = db.query(func.count(User.id)).scalar()

    # Active users (users who have placed at least one bet)
    now = datetime.utcnow()

    active_users_24h = (
        db.query(func.count(func.distinct(Bet.user_id)))
        .filter(Bet.created_at >= now - timedelta(hours=24))
        .scalar()
    )

    active_users_7d = (
        db.query(func.count(func.distinct(Bet.user_id)))
        .filter(Bet.created_at >= now - timedelta(days=7))
        .scalar()
    )

    active_users_30d = (
        db.query(func.count(func.distinct(Bet.user_id)))
        .filter(Bet.created_at >= now - timedelta(days=30))
        .scalar()
    )

    # New users
    today_start = datetime.combine(now.date(), datetime.min.time())
    new_users_today = (
        db.query(func.count(User.id))
        .filter(User.created_at >= today_start)
        .scalar()
    )

    new_users_7d = (
        db.query(func.count(User.id))
        .filter(User.created_at >= now - timedelta(days=7))
        .scalar()
    )

    new_users_30d = (
        db.query(func.count(User.id))
        .filter(User.created_at >= now - timedelta(days=30))
        .scalar()
    )

    # Average bets per user
    total_bets = db.query(func.count(Bet.id)).scalar()
    users_with_bets = (
        db.query(func.count(func.distinct(Bet.user_id))).scalar() or 1
    )
    average_bets_per_user = total_bets / users_with_bets if users_with_bets > 0 else 0.0

    # Average deposit per user
    total_deposits = (
        db.query(func.sum(Deposit.amount))
        .filter(Deposit.status == DepositStatus.APPROVED)
        .scalar()
        or Decimal("0.00")
    )
    users_with_deposits = (
        db.query(func.count(func.distinct(Deposit.user_id)))
        .filter(Deposit.status == DepositStatus.APPROVED)
        .scalar()
        or 1
    )
    average_deposit_per_user = (
        float(total_deposits) / users_with_deposits if users_with_deposits > 0 else 0.0
    )

    return UserEngagementMetrics(
        total_users=total_users,
        active_users_24h=active_users_24h,
        active_users_7d=active_users_7d,
        active_users_30d=active_users_30d,
        new_users_today=new_users_today,
        new_users_7d=new_users_7d,
        new_users_30d=new_users_30d,
        average_bets_per_user=average_bets_per_user,
        average_deposit_per_user=average_deposit_per_user,
    )
