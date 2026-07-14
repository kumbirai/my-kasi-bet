"""
Tests for message router service.

This module tests message routing and user registration functionality.
"""
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.models.user import User
from app.models.wallet import Wallet
from app.services.message_router import MessageRouter


@pytest.fixture
def message_router_instance():
    """Create message router instance."""
    return MessageRouter()


@pytest.mark.asyncio
async def test_route_message_new_user(test_db, message_router_instance):
    """Test routing message for new user (registration)."""
    user = test_db.query(User).filter(User.telegram_chat_id == "999888777").first()
    if user:
        test_db.delete(user)
    test_db.commit()

    with patch(
        "app.services.message_router.telegram_service"
    ) as mock_telegram:
        mock_telegram.send_message = AsyncMock()

        await message_router_instance.route_message_telegram(
            "999888777", "Hello", "42", test_db, username="newbie"
        )

        # Verify user was created
        user = test_db.query(User).filter(
            User.telegram_chat_id == "999888777"
        ).first()
        assert user is not None
        assert user.wallet is not None

        # Verify welcome message was sent
        mock_telegram.send_message.assert_called_once()
        call_args = mock_telegram.send_message.call_args
        assert "Welcome" in call_args[0][1] or "welcome" in call_args[0][1].lower()


@pytest.mark.asyncio
async def test_route_message_existing_user(test_db, test_user, message_router_instance):
    """Test routing message for existing user."""
    with patch(
        "app.services.message_router.telegram_service"
    ) as mock_telegram:
        mock_telegram.send_message = AsyncMock()

        await message_router_instance.route_message_telegram(
            test_user.telegram_chat_id, "menu", "43", test_db
        )

        # Verify response was sent
        mock_telegram.send_message.assert_called_once()


@pytest.mark.asyncio
async def test_route_message_blocked_user(test_db, test_user, message_router_instance):
    """Test routing message for blocked user."""
    test_user.is_blocked = True
    test_db.commit()

    with patch(
        "app.services.message_router.telegram_service"
    ) as mock_telegram:
        mock_telegram.send_message = AsyncMock()

        await message_router_instance.route_message_telegram(
            test_user.telegram_chat_id, "Hello", "44", test_db
        )

        # Verify blocked message was sent
        mock_telegram.send_message.assert_called_once()
        call_args = mock_telegram.send_message.call_args
        assert "blocked" in call_args[0][1].lower()


def test_check_balance(test_db, test_user, message_router_instance):
    """Test balance checking."""
    test_user.wallet.balance = Decimal("150.50")
    test_db.commit()

    response = message_router_instance._check_balance(test_user, test_db)

    assert "150.50" in response or "150.5" in response
    assert "Balance" in response


def test_show_games(message_router_instance):
    """Test games menu display."""
    response = message_router_instance._show_games()

    assert "GAME" in response or "game" in response.lower()
    assert "Lucky Wheel" in response or "lucky" in response.lower()


def test_show_help(message_router_instance):
    """Test help menu display."""
    response = message_router_instance._show_help()

    assert "help" in response.lower() or "HELP" in response
    assert "menu" in response.lower() or "MENU" in response
