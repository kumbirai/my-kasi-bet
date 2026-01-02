"""
Application configuration management using Pydantic Settings.

This module provides centralized configuration management with validation
and environment variable support.
"""
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    All settings are validated on initialization and can be accessed
    as attributes of the Settings instance.
    """
    
    # WhatsApp Business API Configuration
    WHATSAPP_API_URL: str = "https://graph.facebook.com/v18.0"
    WHATSAPP_PHONE_NUMBER_ID: Optional[str] = None
    WHATSAPP_ACCESS_TOKEN: Optional[str] = None
    WHATSAPP_VERIFY_TOKEN: Optional[str] = None
    
    # Database Configuration
    DATABASE_URL: str
    
    # Redis Configuration
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Security Configuration
    SECRET_KEY: Optional[str] = None
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # Server Configuration
    PORT: int = 8000
    ENVIRONMENT: str = "development"
    
    # CORS Configuration
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000,http://localhost:5174"
    
    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    
    Uses LRU cache to ensure settings are loaded only once,
    improving performance and ensuring consistency.
    
    Returns:
        Settings: The application settings instance
    """
    return Settings()


# Global settings instance
settings = get_settings()
