"""UserService tests for Telegram user creation."""
from decimal import Decimal

from app.models.wallet import Wallet
from app.services.user_service import UserService


def test_get_or_create_user_by_telegram(test_db):
    user = UserService.get_or_create_user_by_telegram("123456789", "tg_user", test_db)
    assert user.telegram_chat_id == "123456789"
    assert user.username == "tg_user"
    w = test_db.query(Wallet).filter(Wallet.user_id == user.id).first()
    assert w is not None
    assert w.balance == Decimal("0.00")


def test_get_or_create_user_by_telegram_is_idempotent(test_db):
    first = UserService.get_or_create_user_by_telegram("55667788", "again", test_db)
    second = UserService.get_or_create_user_by_telegram("55667788", "again", test_db)
    assert first.id == second.id
