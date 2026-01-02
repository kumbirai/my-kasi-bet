"""
FastAPI dependencies.

This module provides reusable dependencies for route handlers.
"""
from typing import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.admin import AdminUser
from app.utils.security import verify_token

# Re-export get_db for convenience
__all__ = ["get_db_session", "get_current_admin"]

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
