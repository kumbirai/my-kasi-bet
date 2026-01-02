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
    # Ensure user doesn't exist (cascade will delete wallet too)
    from app.models.wallet import Wallet
    
    user = test_db.query(User).filter(User.phone_number == "27829999999").first()
    if user:
        test_db.delete(user)
    test_db.commit()

    with patch(
        "app.services.message_router.whatsapp_service"
    ) as mock_whatsapp:
        mock_whatsapp.mark_as_read = AsyncMock()
        mock_whatsapp.send_message = AsyncMock()

        await message_router_instance.route_message(
            "27829999999", "Hello", "wamid.test123", test_db
        )

        # Verify user was created
        user = test_db.query(User).filter(
            User.phone_number == "27829999999"
        ).first()
        assert user is not None
        assert user.wallet is not None

        # Verify welcome message was sent
        mock_whatsapp.send_message.assert_called_once()
        call_args = mock_whatsapp.send_message.call_args
        assert "Welcome" in call_args[0][1] or "welcome" in call_args[0][1].lower()


@pytest.mark.asyncio
async def test_route_message_existing_user(test_db, test_user, message_router_instance):
    """Test routing message for existing user."""
    with patch(
        "app.services.message_router.whatsapp_service"
    ) as mock_whatsapp:
        mock_whatsapp.mark_as_read = AsyncMock()
        mock_whatsapp.send_message = AsyncMock()

        await message_router_instance.route_message(
            test_user.phone_number, "menu", "wamid.test456", test_db
        )

        # Verify response was sent
        mock_whatsapp.send_message.assert_called_once()


@pytest.mark.asyncio
async def test_route_message_blocked_user(test_db, test_user, message_router_instance):
    """Test routing message for blocked user."""
    test_user.is_blocked = True
    test_db.commit()

    with patch(
        "app.services.message_router.whatsapp_service"
    ) as mock_whatsapp:
        mock_whatsapp.mark_as_read = AsyncMock()
        mock_whatsapp.send_message = AsyncMock()

        await message_router_instance.route_message(
            test_user.phone_number, "Hello", "wamid.test789", test_db
        )

        # Verify blocked message was sent
        mock_whatsapp.send_message.assert_called_once()
        call_args = mock_whatsapp.send_message.call_args
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
