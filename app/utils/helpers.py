"""
Helper utility functions.

This module provides utility functions for phone number normalization,
message cleaning, and other common operations.
"""
import re
from typing import Optional


def normalize_phone_number(phone: str) -> str:
    """
    Normalize phone number to WhatsApp format.

    Converts phone numbers from various formats to the standard WhatsApp
    format: country code + number (no + or spaces).

    Args:
        phone: Phone number in various formats (e.g., "+27 82 123 4567",
               "0821234567", "27821234567")

    Returns:
        Normalized phone number (e.g., "27821234567")

    Examples:
        >>> normalize_phone_number("+27 82 123 4567")
        '27821234567'
        >>> normalize_phone_number("0821234567")
        '27821234567'
        >>> normalize_phone_number("27821234567")
        '27821234567'
    """
    if not phone:
        raise ValueError("Phone number cannot be empty")

    # Remove all non-digit characters
    digits = re.sub(r"\D", "", phone)

    if not digits:
        raise ValueError("Phone number must contain at least one digit")

    # If starts with 0, assume South Africa and replace with 27
    if digits.startswith("0"):
        digits = "27" + digits[1:]

    # If doesn't start with country code, assume South Africa (27)
    if not digits.startswith("27"):
        digits = "27" + digits

    return digits


def validate_phone_number(phone: str) -> bool:
    """
    Validate phone number format.

    Checks if the phone number is in a valid format after normalization.
    South African numbers should be 11 digits (27 + 9 digits).

    Args:
        phone: Phone number to validate

    Returns:
        True if valid, False otherwise

    Examples:
        >>> validate_phone_number("27821234567")
        True
        >>> validate_phone_number("123")
        False
    """
    try:
        normalized = normalize_phone_number(phone)
        # South African numbers: 27 + 9 digits = 11 total
        # Allow 10-15 digits for international compatibility
        return 10 <= len(normalized) <= 15
    except (ValueError, AttributeError):
        return False


def clean_message_text(text: Optional[str]) -> str:
    """
    Clean and normalize message text.

    Removes extra whitespace and converts to lowercase for consistent
    command matching.

    Args:
        text: Raw message text (can be None)

    Returns:
        Cleaned message text (empty string if input is None or empty)

    Examples:
        >>> clean_message_text("  Hello   World  ")
        'hello world'
        >>> clean_message_text(None)
        ''
        >>> clean_message_text("")
        ''
    """
    if not text:
        return ""

    # Remove extra whitespace and normalize
    cleaned = " ".join(text.split())

    # Convert to lowercase for command matching
    return cleaned.lower().strip()
