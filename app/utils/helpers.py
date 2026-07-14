"""
Helper utility functions.

This module provides utility functions for message cleaning and other
common operations.
"""
from typing import Optional


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
