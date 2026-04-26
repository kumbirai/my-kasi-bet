"""
User domain service.

This module provides business logic for user operations including
registration and wallet creation.
"""
import logging
from decimal import Decimal
from typing import Optional

from sqlalchemy.orm import Session

from app.models.user import User
from app.models.wallet import Wallet

logger = logging.getLogger(__name__)


class UserService:
    """
    Service for user-related business operations.

    Handles user registration, wallet creation, and user state management.
    """

    @staticmethod
    def get_user_by_telegram_chat_id(
        telegram_chat_id: str, db: Session
    ) -> Optional[User]:
        """
        Get user by Telegram chat ID.

        Args:
            telegram_chat_id: Telegram chat ID (string)
            db: Database session

        Returns:
            User instance if found, None otherwise
        """
        return (
            db.query(User)
            .filter(User.telegram_chat_id == telegram_chat_id)
            .first()
        )

    @staticmethod
    def get_or_create_user_by_telegram(
        telegram_chat_id: str,
        username: Optional[str],
        db: Session,
    ) -> User:
        """
        Get existing user or create new user by Telegram chat ID with wallet.

        New users have phone_number=None.

        Args:
            telegram_chat_id: Telegram chat ID
            username: Optional Telegram username
            db: Database session

        Returns:
            User instance (existing or newly created)

        Raises:
            Exception: If database operation fails
        """
        user = (
            db.query(User)
            .filter(User.telegram_chat_id == telegram_chat_id)
            .first()
        )
        if user:
            logger.debug(
                f"User found: {user.id} (telegram_chat_id={telegram_chat_id})"
            )
            return user

        try:
            user = User(
                telegram_chat_id=telegram_chat_id,
                username=username,
                phone_number=None,
            )
            db.add(user)
            db.flush()

            wallet = Wallet(user_id=user.id, balance=Decimal("0.00"))
            db.add(wallet)
            db.commit()
            db.refresh(user)

            logger.info(
                f"New user registered via Telegram: {telegram_chat_id} (ID: {user.id})"
            )
            return user
        except Exception as e:
            db.rollback()
            logger.error(
                f"Error registering user telegram_chat_id={telegram_chat_id}: {e}",
                exc_info=True,
            )
            raise

    @staticmethod
    def get_or_create_user(phone_number: str, db: Session) -> User:
        """
        Get existing user or create new user with wallet.

        This is an atomic operation that ensures a user always has a wallet.
        If the user already exists, returns the existing user. If not,
        creates both user and wallet in a single transaction.

        Args:
            phone_number: Normalized phone number
            db: Database session

        Returns:
            User instance (existing or newly created)

        Raises:
            Exception: If database operation fails
        """
        if not phone_number or not str(phone_number).strip():
            raise ValueError("phone_number is required for WhatsApp registration")

        # Check if user exists
        user = db.query(User).filter(User.phone_number == phone_number).first()

        if user:
            logger.debug(f"User found: {user.id} ({phone_number})")
            return user

        # Create new user
        try:
            user = User(phone_number=phone_number, telegram_chat_id=None)
            db.add(user)
            db.flush()  # Get user.id before committing

            # Create wallet for new user
            wallet = Wallet(user_id=user.id, balance=Decimal("0.00"))
            db.add(wallet)
            db.commit()
            db.refresh(user)

            logger.info(f"New user registered: {phone_number} (ID: {user.id})")
            return user
        except Exception as e:
            db.rollback()
            logger.error(f"Error registering user {phone_number}: {e}", exc_info=True)
            raise

    @staticmethod
    def get_user_by_phone(phone_number: str, db: Session) -> Optional[User]:
        """
        Get user by phone number.

        Args:
            phone_number: Normalized phone number
            db: Database session

        Returns:
            User instance if found, None otherwise
        """
        return db.query(User).filter(User.phone_number == phone_number).first()

    @staticmethod
    def update_last_active(user: User, db: Session) -> None:
        """
        Update user's last active timestamp.

        Args:
            user: User instance to update
            db: Database session
        """
        from sqlalchemy import func

        user.last_active = func.now()
        db.commit()
        logger.debug(f"Updated last_active for user {user.id}")
