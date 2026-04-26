"""UserService tests for WhatsApp vs Telegram user creation."""
from decimal import Decimal

from app.models.user import User
from app.models.wallet import Wallet
from app.services.user_service import UserService


def test_get_or_create_user_whatsapp(test_db):
    user = UserService.get_or_create_user("27821234567", test_db)
    assert user.phone_number == "27821234567"
    assert user.telegram_chat_id is None
    w = test_db.query(Wallet).filter(Wallet.user_id == user.id).first()
    assert w is not None
    assert w.balance == Decimal("0.00")


def test_get_or_create_user_by_telegram(test_db):
    user = UserService.get_or_create_user_by_telegram("123456789", "tg_user", test_db)
    assert user.telegram_chat_id == "123456789"
    assert user.phone_number is None
    assert user.username == "tg_user"
    w = test_db.query(Wallet).filter(Wallet.user_id == user.id).first()
    assert w is not None
