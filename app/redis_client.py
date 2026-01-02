"""
Redis client and connection management.

This module provides a Redis client singleton with connection health checks
and error handling. It gracefully handles Redis unavailability.
"""
import logging
from typing import Optional

import redis
from redis.exceptions import ConnectionError, RedisError

from app.config import settings

logger = logging.getLogger(__name__)

# Global Redis client instance
_redis_client: Optional[redis.Redis] = None


def get_redis_client() -> Optional[redis.Redis]:
    """
    Get or create Redis client singleton.

    Returns:
        Redis client instance if connection successful, None otherwise
    """
    global _redis_client

    if _redis_client is not None:
        return _redis_client

    try:
        # Parse Redis URL
        redis_url = settings.REDIS_URL

        # Create Redis client with connection pooling
        _redis_client = redis.from_url(
            redis_url,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True,
            health_check_interval=30,
        )

        # Test connection
        _redis_client.ping()
        logger.info("Redis client connected successfully")
        return _redis_client

    except (ConnectionError, RedisError, ValueError) as e:
        logger.warning(f"Redis connection failed: {e}. Application will continue without Redis.")
        _redis_client = None
        return None
    except Exception as e:
        logger.error(f"Unexpected error initializing Redis: {e}", exc_info=True)
        _redis_client = None
        return None


def check_redis_connection() -> bool:
    """
    Check if Redis connection is healthy.

    Returns:
        True if Redis is connected and responding, False otherwise
    """
    try:
        client = get_redis_client()
        if client is None:
            return False
        client.ping()
        return True
    except Exception as e:
        logger.debug(f"Redis health check failed: {e}")
        return False


def close_redis_connection() -> None:
    """
    Close Redis connection and reset client.

    This should be called during application shutdown.
    """
    global _redis_client

    if _redis_client is not None:
        try:
            _redis_client.close()
            logger.info("Redis connection closed")
        except Exception as e:
            logger.warning(f"Error closing Redis connection: {e}")
        finally:
            _redis_client = None
