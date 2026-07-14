"""
Tests for utility functions.

This module tests helper utility functions.
"""
import pytest

from app.utils.helpers import clean_message_text
from app.utils.security import get_password_hash, verify_password


def test_clean_message_text():
    """Test cleaning message text."""
    assert clean_message_text("  Hello   World  ") == "hello world"
    assert clean_message_text("HELLO") == "hello"
    assert clean_message_text("") == ""


def test_clean_message_text_none():
    """Test cleaning None message text."""
    assert clean_message_text(None) == ""


def test_password_hash_round_trip():
    """A valid password can be verified without a compatibility fallback."""
    password = "ProductionPassword123!"

    hashed_password = get_password_hash(password)

    assert hashed_password != password
    assert verify_password(password, hashed_password) is True
    assert verify_password("wrong-password", hashed_password) is False


def test_password_hash_rejects_values_beyond_bcrypt_limit():
    """Passwords must never be silently truncated to bcrypt's byte limit."""
    with pytest.raises(ValueError, match="72 UTF-8 bytes"):
        get_password_hash("x" * 73)
