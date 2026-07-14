"""Reusable FastAPI dependencies."""
import json
import logging
from typing import Generator
from urllib.parse import parse_qsl

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.admin import AdminUser
from app.models.user import User
from app.services.user_service import UserService
from app.utils.security import verify_token
from app.utils.telegram_auth import InitDataError, verify_init_data

# Re-export get_db for convenience
__all__ = ["current_tg_user", "get_db_session", "get_current_admin"]

logger = logging.getLogger(__name__)

security = HTTPBearer()


def get_db_session() -> Generator[Session, None, None]:
    """
    Dependency for getting database session.

    This is an alias for app.database.get_db for consistency
    with API route naming conventions.

    Yields:
        Session: SQLAlchemy database session
    """
    yield from get_db()


def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> AdminUser:
    """
    Get current authenticated admin user.

    This dependency validates the JWT token and returns the admin user.
    It raises HTTPException if authentication fails.

    Args:
        credentials: HTTP Bearer token credentials
        db: Database session

    Returns:
        AdminUser instance

    Raises:
        HTTPException: If authentication fails
    """
    token = credentials.credentials
    payload = verify_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

    admin_id = payload.get("sub")
    if not admin_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    admin = db.query(AdminUser).filter(AdminUser.id == int(admin_id)).first()

    if not admin or not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin user not found or inactive",
        )

    return admin


def _claimed_telegram_user_id(init_data: str) -> str:
    """Extract an untrusted numeric user id for security logging only."""
    try:
        raw_user = dict(parse_qsl(init_data, keep_blank_values=True)).get("user")
        user = json.loads(raw_user) if raw_user else {}
        user_id = user.get("id") if isinstance(user, dict) else None
        is_numeric_id = isinstance(user_id, int) and not isinstance(user_id, bool)
        return str(user_id) if is_numeric_id else "unknown"
    except (TypeError, ValueError, json.JSONDecodeError):
        return "unknown"


def current_tg_user(
    x_init_data: str | None = Header(default=None, alias="X-Init-Data"),
    db: Session = Depends(get_db_session),
) -> User:
    """Resolve an active user from Telegram's signed Mini App init data."""
    try:
        fields = verify_init_data(x_init_data or "")
    except InitDataError as exc:
        logger.warning(
            "Rejected Telegram Mini App authentication: claimed_user_id=%s reason=%s",
            _claimed_telegram_user_id(x_init_data or ""),
            exc,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid Telegram auth",
        ) from exc

    telegram_user = fields["user"]
    user = UserService.get_or_create_user_by_telegram(
        telegram_chat_id=str(telegram_user["id"]),
        username=telegram_user.get("username"),
        db=db,
    )
    if user.is_blocked or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="account unavailable",
        )
    return user
