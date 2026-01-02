"""
Tests for utility functions.

This module tests helper utility functions.
"""
import pytest

from app.utils.helpers import (
    clean_message_text,
    normalize_phone_number,
    validate_phone_number,
)


def test_normalize_phone_number_with_plus():
    """Test normalizing phone number with + prefix."""
    result = normalize_phone_number("+27 82 123 4567")
    assert result == "27821234567"


def test_normalize_phone_number_with_zero():
    """Test normalizing phone number starting with 0."""
    result = normalize_phone_number("0821234567")
    assert result == "27821234567"


def test_normalize_phone_number_already_normalized():
    """Test normalizing already normalized number."""
    result = normalize_phone_number("27821234567")
    assert result == "27821234567"


def test_normalize_phone_number_empty():
    """Test normalizing empty phone number."""
    with pytest.raises(ValueError):
        normalize_phone_number("")


def test_validate_phone_number_valid():
    """Test validating valid phone number."""
    assert validate_phone_number("27821234567") is True
    assert validate_phone_number("+27 82 123 4567") is True


def test_validate_phone_number_invalid():
    """Test validating invalid phone number."""
    assert validate_phone_number("123") is False
    assert validate_phone_number("") is False


def test_clean_message_text():
    """Test cleaning message text."""
    assert clean_message_text("  Hello   World  ") == "hello world"
    assert clean_message_text("HELLO") == "hello"
    assert clean_message_text("") == ""


def test_clean_message_text_none():
    """Test cleaning None message text."""
    assert clean_message_text(None) == ""
