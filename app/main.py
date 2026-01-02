"""
FastAPI application entry point.

This module creates and configures the FastAPI application with all
necessary middleware, routes, and lifecycle events.
"""
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import admin, admin_analytics, admin_bets, admin_users, webhook
from app.config import settings
from app.database import init_db
from app.redis_client import check_redis_connection, close_redis_connection, get_redis_client

# Configure logging
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_dir / "app.log"),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup/shutdown events.

    Handles application startup and shutdown tasks such as database
    initialization and cleanup.

    Args:
        app: FastAPI application instance.

    Yields:
        None: Control returns to application runtime.
    """
    # Startup
    logger.info("Starting up application...")
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

    # Initialize Redis connection (non-blocking)
    try:
        redis_client = get_redis_client()
        if redis_client:
            logger.info("Redis connection initialized successfully")
        else:
            logger.warning("Redis connection unavailable - application will continue without Redis")
    except Exception as e:
        logger.warning(f"Redis initialization failed: {e}. Application will continue without Redis.")

    yield

    # Shutdown
    logger.info("Shutting down application...")
    close_redis_connection()


# Create FastAPI app
app = FastAPI(
    title="MyKasiBets WhatsApp Betting Platform",
    description="MVP WhatsApp-based betting platform API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
# Parse CORS origins from comma-separated string
cors_origins = [
    origin.strip()
    for origin in settings.CORS_ORIGINS.split(",")
    if origin.strip()
]

# In development, add common localhost ports if not already present
if settings.ENVIRONMENT == "development":
    common_origins = [
        "http://localhost:5173",  # Vite default
        "http://localhost:3000",   # React default
        "http://localhost:5174",   # Vite alternate
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]
    for origin in common_origins:
        if origin not in cors_origins:
            cors_origins.append(origin)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include routers
# Webhook router at root level for WhatsApp webhook configuration
app.include_router(webhook.router, tags=["webhook"])
# Admin routers with /api prefix
app.include_router(admin.router, prefix="/api", tags=["admin"])
app.include_router(admin_users.router, prefix="/api", tags=["admin"])
app.include_router(admin_bets.router, prefix="/api", tags=["admin"])
app.include_router(admin_analytics.router, prefix="/api", tags=["admin"])


@app.get("/")
async def root() -> dict[str, str]:
    """
    Root endpoint.

    Returns basic API information.

    Returns:
        dict: API name, status, and version.
    """
    return {
        "message": "MyKasiBets WhatsApp Betting Platform API",
        "status": "running",
        "version": "1.0.0",
    }


@app.get("/health")
async def health_check() -> dict[str, str | bool]:
    """
    Health check endpoint.

    Used for monitoring and load balancer health checks.
    Includes database and Redis connection status.

    Returns:
        dict: Health status, environment, and service connectivity information.
    """
    from app.database import check_db_connection

    db_status = check_db_connection()
    redis_status = check_redis_connection()

    return {
        "status": "healthy" if db_status else "unhealthy",
        "environment": settings.ENVIRONMENT,
        "database": db_status,
        "redis": redis_status,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.ENVIRONMENT == "development",
    )
