"""
Database connection and session management.

This module provides SQLAlchemy engine, session factory, and base
declarative class for database models.
"""
import logging
from typing import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings

logger = logging.getLogger(__name__)

# Create database engine with connection pooling
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before using
    pool_size=10,
    max_overflow=20,
    echo=False,  # Set to True for SQL logging during development
    connect_args={
        "connect_timeout": 10,
    },
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# Base class for all models
Base = declarative_base()

# Import all models to ensure they're registered with Base
from app.models import (  # noqa: E402, F401
    AdminActionLog,
    AdminUser,
    Bet,
    Deposit,
    Match,
    Transaction,
    User,
    Wallet,
    Withdrawal,
)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for getting database session.
    
    This function is used as a FastAPI dependency to provide
    database sessions to route handlers. The session is automatically
    closed after the request completes.
    
    Yields:
        Session: SQLAlchemy database session
        
    Example:
        @app.get("/items")
        def read_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Initialize database tables.
    
    Creates all tables defined in models using SQLAlchemy Base metadata.
    This should be called during application startup.
    
    Raises:
        Exception: If database initialization fails
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}", exc_info=True)
        raise


def check_db_connection() -> bool:
    """
    Check if database connection is working.
    
    Returns:
        bool: True if connection is successful, False otherwise
    """
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database connection check failed: {e}")
        return False
