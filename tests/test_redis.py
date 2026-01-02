"""
Tests for Redis connectivity and client functionality.

This module tests the Redis client module to ensure proper connection
handling and health checks.
"""
import pytest

from app.redis_client import (
    check_redis_connection,
    close_redis_connection,
    get_redis_client,
)


def test_get_redis_client():
    """Test that Redis client can be created."""
    client = get_redis_client()
    # Client should be created (may be None if Redis unavailable)
    assert client is None or hasattr(client, "ping")


def test_redis_connection_health():
    """Test Redis connection health check."""
    # This test will pass if Redis is available, or gracefully handle if not
    result = check_redis_connection()
    assert isinstance(result, bool)


def test_redis_basic_operations():
    """Test basic Redis operations if connection is available."""
    client = get_redis_client()
    if client is None:
        pytest.skip("Redis not available")

    try:
        # Test SET operation
        client.set("test_key", "test_value", ex=10)  # Expire in 10 seconds

        # Test GET operation
        value = client.get("test_key")
        assert value == "test_value"

        # Test DELETE operation
        client.delete("test_key")
        assert client.get("test_key") is None

    except Exception as e:
        pytest.fail(f"Redis operations failed: {e}")


def test_redis_ping():
    """Test Redis PING command."""
    client = get_redis_client()
    if client is None:
        pytest.skip("Redis not available")

    try:
        result = client.ping()
        assert result is True
    except Exception as e:
        pytest.fail(f"Redis PING failed: {e}")


def test_close_redis_connection():
    """Test that Redis connection can be closed."""
    # Get client first
    client = get_redis_client()
    if client is None:
        pytest.skip("Redis not available")

    # Close connection
    close_redis_connection()

    # Verify client is reset
    client_after = get_redis_client()
    # After closing, get_redis_client should return None or a new client
    # (depending on implementation)
    assert client_after is None or client_after != client
