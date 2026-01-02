# Phase 1 Implementation Plan
## WhatsApp Betting Platform MVP - Foundation Week

**Version:** 1.0  
**Date:** December 2024  
**Duration:** Week 1 (5 days)  
**Goal:** Set up Python FastAPI server, WhatsApp Business API integration, PostgreSQL database, and basic user registration

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Phase 1 Objectives](#phase-1-objectives)
3. [Success Criteria](#success-criteria)
4. [Day 1: Environment Setup & Project Structure](#day-1-environment-setup--project-structure)
5. [Day 2: Database Setup & Models](#day-2-database-setup--models)
6. [Day 3: WhatsApp Business API Integration](#day-3-whatsapp-business-api-integration)
7. [Day 4: Message Router & User Registration](#day-4-message-router--user-registration)
8. [Day 5: Webhook Endpoint & Testing](#day-5-webhook-endpoint--testing)
9. [Deliverables Checklist](#deliverables-checklist)
10. [Testing Strategy](#testing-strategy)
11. [Troubleshooting Guide](#troubleshooting-guide)
12. [Next Steps](#next-steps)

---

## Executive Summary

Phase 1 establishes the foundational infrastructure for the WhatsApp betting platform. This phase focuses on:

- **Backend Framework**: Python 3.10+ with FastAPI
- **Database**: PostgreSQL 14+ with SQLAlchemy ORM
- **WhatsApp Integration**: WhatsApp Business API webhook setup
- **User Management**: Basic user registration and authentication flow
- **Project Structure**: Clean, scalable codebase organization

By the end of Phase 1, the system will be able to:
- Receive WhatsApp messages via webhook
- Register new users automatically
- Respond to basic commands
- Store user data in PostgreSQL
- Handle webhook verification

---

## Phase 1 Objectives

### Primary Objectives

1. ✅ **Project Infrastructure**
   - Set up Python virtual environment
   - Configure FastAPI application
   - Establish project directory structure
   - Configure environment variables

2. ✅ **Database Foundation**
   - Create PostgreSQL database
   - Design and implement core database schema
   - Set up SQLAlchemy models (User, Wallet)
   - Configure database connection pooling

3. ✅ **WhatsApp Integration**
   - Configure WhatsApp Business API credentials
   - Implement WhatsApp service client
   - Set up webhook verification endpoint
   - Implement message sending functionality

4. ✅ **User Registration System**
   - Implement automatic user registration on first message
   - Create wallet for new users
   - Store user phone numbers and metadata
   - Handle user state management

5. ✅ **Message Routing**
   - Implement message router service
   - Create command parsing logic
   - Build main menu system
   - Handle basic user commands (balance, menu, help)

### Secondary Objectives

- Set up logging infrastructure
- Configure error handling
- Create health check endpoints
- Document API endpoints
- Set up development environment

---

## Success Criteria

Phase 1 is considered complete when:

### Functional Requirements

- [ ] WhatsApp webhook successfully verifies with Meta
- [ ] System receives incoming WhatsApp messages
- [ ] New users are automatically registered on first message
- [ ] System sends welcome message to new users
- [ ] System responds to basic commands (menu, balance, help)
- [ ] User data is stored in PostgreSQL
- [ ] Wallet is created for each new user
- [ ] FastAPI server runs without errors
- [ ] Database connection is stable
- [ ] All endpoints are accessible via FastAPI docs

### Technical Requirements

- [ ] All code follows Python best practices
- [ ] Type hints are used throughout
- [ ] Error handling is implemented
- [ ] Logging is configured and working
- [ ] Environment variables are properly loaded
- [ ] Database migrations are set up (if using Alembic)
- [ ] Code is organized in clean module structure
- [ ] No critical security vulnerabilities

### Testing Requirements

- [ ] Webhook verification endpoint tested
- [ ] User registration flow tested
- [ ] Message routing tested
- [ ] Database operations tested
- [ ] WhatsApp message sending tested

---

## Day 1: Environment Setup & Project Structure

**Duration:** 4-6 hours  
**Goal:** Establish project foundation, virtual environment, and basic FastAPI application structure

### Prerequisites

Before starting, ensure you have:
- Python 3.10+ installed (`python --version`)
- PostgreSQL 14+ installed and running
- Git installed
- Code editor (VS Code recommended)
- WhatsApp Business API account (credentials obtained)

### Step 1: Project Initialization (30 minutes)

#### 1.1 Create Project Directory

```bash
cd /home/coach/cursor/python/my-kasi-bet
mkdir -p app/{models,schemas,services/games,api,utils}
mkdir -p tests
mkdir -p alembic/versions
mkdir -p logs
```

#### 1.2 Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

Verify activation: `which python` should point to `venv/bin/python`

#### 1.3 Create Project Structure

Create the following directory structure:

```
my-kasi-bet/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app entry point
│   ├── config.py               # Configuration management
│   ├── database.py             # Database connection
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── wallet.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── user.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── whatsapp.py
│   │   └── message_router.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── webhook.py
│   └── utils/
│       ├── __init__.py
│       └── security.py
├── tests/
│   ├── __init__.py
│   └── conftest.py
├── alembic/
│   └── versions/
├── logs/
├── .env
├── .gitignore
├── requirements.txt
├── alembic.ini
└── README.md
```

### Step 2: Create requirements.txt (15 minutes)

Create `requirements.txt` with the following dependencies:

```txt
# FastAPI and Server
fastapi==0.109.0
uvicorn[standard]==0.27.0
python-multipart==0.0.6

# Database
sqlalchemy==2.0.25
psycopg2-binary==2.9.9
alembic==1.13.1

# Data Validation
pydantic==2.5.3
pydantic-settings==2.1.0

# Security
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4

# HTTP Client
httpx==0.26.0

# Redis & Celery (optional for Phase 1)
redis==5.0.1
celery==5.3.4

# Utilities
python-dotenv==1.0.0

# Testing
pytest==7.4.4
pytest-asyncio==0.23.3
pytest-cov==4.1.0
```

#### 2.1 Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Expected time:** 2-3 minutes

### Step 3: Environment Configuration (20 minutes)

#### 3.1 Create .env File

Create `.env` file in project root:

```env
# WhatsApp Business API
WHATSAPP_API_URL=https://graph.facebook.com/v18.0
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id_here
WHATSAPP_ACCESS_TOKEN=your_permanent_access_token_here
WHATSAPP_VERIFY_TOKEN=choose_a_random_string_min_20_chars

# Database
DATABASE_URL=postgresql://postgres:secret@localhost:5432/betting_db

# Redis (optional for Phase 1)
REDIS_URL=redis://localhost:6379/0

# JWT Security
SECRET_KEY=generate_random_32_char_string_use_secrets_token_hex
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Server
PORT=8000
ENVIRONMENT=development

# Logging
LOG_LEVEL=INFO
```

#### 3.2 Generate Secret Key

```python
# Run in Python REPL
import secrets
print(secrets.token_hex(32))
```

Copy the output to `SECRET_KEY` in `.env`

#### 3.3 Create .gitignore

Create `.gitignore`:

```gitignore
# Virtual Environment
venv/
env/
ENV/
.venv

# Environment Variables
.env
.env.local
.env.*.local

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
*.egg-info/
dist/
build/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*.sublime-project
*.sublime-workspace

# Logs
logs/
*.log

# Database
*.db
*.sqlite3

# OS
.DS_Store
Thumbs.db

# Testing
.pytest_cache/
.coverage
htmlcov/

# Alembic
alembic.ini.bak
```

### Step 4: Create Core Configuration Files (45 minutes)

#### 4.1 Create app/config.py

```python
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    # WhatsApp Business API
    WHATSAPP_API_URL: str = "https://graph.facebook.com/v18.0"
    WHATSAPP_PHONE_NUMBER_ID: str
    WHATSAPP_ACCESS_TOKEN: str
    WHATSAPP_VERIFY_TOKEN: str
    
    # Database
    DATABASE_URL: str
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # Server
    PORT: int = 8000
    ENVIRONMENT: str = "development"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


settings = get_settings()
```

#### 4.2 Create app/database.py

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import logging

from .config import settings

logger = logging.getLogger(__name__)

# Create database engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before using
    pool_size=10,
    max_overflow=20,
    echo=False  # Set to True for SQL logging during development
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for getting database session
    
    Usage:
        @app.get("/items")
        def read_items(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database tables
    Creates all tables defined in models
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise
```

#### 4.3 Create app/main.py

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from contextlib import asynccontextmanager

from .config import settings
from .database import init_db

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events"""
    # Startup
    logger.info("Starting up application...")
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")


# Create FastAPI app
app = FastAPI(
    title="MyKasiBets WhatsApp Betting Platform",
    description="MVP WhatsApp-based betting platform API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.ENVIRONMENT == "development" else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "MyKasiBets WhatsApp Betting Platform API",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.ENVIRONMENT == "development"
    )
```

### Step 5: Create __init__.py Files (10 minutes)

Create empty `__init__.py` files in all package directories:

```bash
touch app/__init__.py
touch app/models/__init__.py
touch app/schemas/__init__.py
touch app/services/__init__.py
touch app/api/__init__.py
touch app/utils/__init__.py
touch tests/__init__.py
```

### Step 6: Test Basic Setup (30 minutes)

#### 6.1 Create Test Script

Create `test_setup.py` in project root:

```python
"""Test script to verify basic setup"""
import sys
from app.config import settings
from app.database import engine, SessionLocal
from sqlalchemy import text

def test_imports():
    """Test that all imports work"""
    print("Testing imports...")
    try:
        from app import main
        from app.config import settings
        from app.database import get_db
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_config():
    """Test configuration loading"""
    print("\nTesting configuration...")
    try:
        assert settings.WHATSAPP_API_URL
        assert settings.DATABASE_URL
        assert settings.SECRET_KEY
        print("✅ Configuration loaded successfully")
        print(f"   Environment: {settings.ENVIRONMENT}")
        print(f"   Port: {settings.PORT}")
        return True
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def test_database():
    """Test database connection"""
    print("\nTesting database connection...")
    try:
        db = SessionLocal()
        result = db.execute(text("SELECT 1"))
        db.close()
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("   Make sure PostgreSQL is running and DATABASE_URL is correct")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("Phase 1 - Setup Verification")
    print("=" * 50)
    
    results = [
        test_imports(),
        test_config(),
        test_database()
    ]
    
    print("\n" + "=" * 50)
    if all(results):
        print("✅ All tests passed! Setup is complete.")
        sys.exit(0)
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        sys.exit(1)
```

#### 6.2 Run Test Script

```bash
python test_setup.py
```

**Expected output:**
```
==================================================
Phase 1 - Setup Verification
==================================================
Testing imports...
✅ All imports successful

Testing configuration...
✅ Configuration loaded successfully
   Environment: development
   Port: 8000

Testing database connection...
✅ Database connection successful

==================================================
✅ All tests passed! Setup is complete.
```

#### 6.3 Start FastAPI Server

```bash
uvicorn app.main:app --reload --port 8000
```

**Expected output:**
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Database tables initialized successfully
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000
```

#### 6.4 Verify Endpoints

- Open browser: http://localhost:8000
- Should see: `{"message": "MyKasiBets WhatsApp Betting Platform API", "status": "running", "version": "1.0.0"}`
- Open: http://localhost:8000/docs
- Should see FastAPI automatic interactive API documentation
- Open: http://localhost:8000/health
- Should see: `{"status": "healthy", "environment": "development"}`

### Day 1 Deliverables

By end of Day 1, you should have:

- [x] Project directory structure created
- [x] Virtual environment set up and activated
- [x] All dependencies installed
- [x] `.env` file configured with all required variables
- [x] `app/config.py` created and working
- [x] `app/database.py` created and tested
- [x] `app/main.py` created with basic FastAPI app
- [x] FastAPI server running successfully
- [x] Database connection verified
- [x] All endpoints accessible
- [x] `.gitignore` configured
- [x] Logging configured

### Day 1 Checklist

- [ ] Python 3.10+ installed
- [ ] Virtual environment created and activated
- [ ] All packages installed from requirements.txt
- [ ] `.env` file created with all variables
- [ ] Database connection tested
- [ ] FastAPI server starts without errors
- [ ] Root endpoint (`/`) returns expected response
- [ ] Health endpoint (`/health`) returns expected response
- [ ] FastAPI docs accessible at `/docs`
- [ ] Logs directory created and logging works

### Common Issues & Solutions

**Issue:** `ModuleNotFoundError` when running scripts
- **Solution:** Ensure virtual environment is activated: `source venv/bin/activate`

**Issue:** Database connection refused
- **Solution:** 
  - Check PostgreSQL is running: `pg_isready`
  - Verify DATABASE_URL in `.env` is correct
  - Ensure database exists: `psql -l` to list databases

**Issue:** Port 8000 already in use
- **Solution:** 
  - Use different port: `uvicorn app.main:app --port 8001`
  - Or kill process: `lsof -ti:8000 | xargs kill -9`

**Issue:** Environment variables not loading
- **Solution:** 
  - Ensure `.env` file is in project root
  - Check `python-dotenv` is installed
  - Verify variable names match exactly (case-sensitive)

---

## Day 2: Database Setup & Models

**Duration:** 4-6 hours  
**Goal:** Create database schema, implement SQLAlchemy models, and set up database migrations

### Prerequisites

- Day 1 completed successfully
- PostgreSQL database created
- Database connection tested and working

### Step 1: Create Database Schema (30 minutes)

#### 1.1 Create Database

```bash
# Connect to PostgreSQL
PGPASSWORD=secret psql -h localhost -p 5432 -U postgres -d postgres

# Create database
CREATE DATABASE betting_db;

# Exit
\q
```

#### 1.2 Verify Database

```bash
PGPASSWORD=secret psql -h localhost -p 5432 -U postgres -d betting_db -c "\dt"
```

Should show no tables yet (empty list).

### Step 2: Create SQLAlchemy Models (2 hours)

#### 2.1 Create app/models/user.py

```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from sqlalchemy.orm import relationship
from ..database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(20), unique=True, nullable=False, index=True)
    username = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_blocked = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_active = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    wallet = relationship("Wallet", back_populates="user", uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, phone={self.phone_number}, active={self.is_active})>"
```

#### 2.2 Create app/models/wallet.py

```python
from sqlalchemy import Column, Integer, Numeric, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from decimal import Decimal
from ..database import Base


class Wallet(Base):
    __tablename__ = "wallets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    balance = Column(Numeric(10, 2), default=Decimal('0.00'), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="wallet")
    
    def __repr__(self):
        return f"<Wallet(user_id={self.user_id}, balance={self.balance})>"
```

#### 2.3 Update app/models/__init__.py

```python
from .user import User
from .wallet import Wallet

__all__ = ["User", "Wallet"]
```

### Step 3: Update Database Initialization (15 minutes)

Update `app/database.py` to import models:

```python
# Add at the end of app/database.py

# Import all models to ensure they're registered with Base
from app.models import User, Wallet  # noqa: F401
```

### Step 4: Test Model Creation (30 minutes)

#### 4.1 Create Test Script

Create `test_models.py`:

```python
"""Test database models"""
from app.database import SessionLocal, init_db
from app.models import User, Wallet
from decimal import Decimal

def test_create_user():
    """Test creating a user"""
    db = SessionLocal()
    try:
        # Create user
        user = User(
            phone_number="27821234567",
            username="TestUser"
        )
        db.add(user)
        db.flush()  # Get user.id
        
        # Create wallet
        wallet = Wallet(
            user_id=user.id,
            balance=Decimal('0.00')
        )
        db.add(wallet)
        db.commit()
        
        print(f"✅ Created user: {user.id} with wallet: {wallet.id}")
        
        # Verify
        db.refresh(user)
        db.refresh(wallet)
        assert user.wallet is not None
        assert user.wallet.balance == Decimal('0.00')
        print("✅ User-wallet relationship verified")
        
        # Cleanup
        db.delete(user)
        db.commit()
        print("✅ Test user cleaned up")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("\nTesting models...")
    test_create_user()
    print("\n✅ All model tests passed!")
```

#### 4.2 Run Test

```bash
python test_models.py
```

**Expected output:**
```
Initializing database...
Database tables initialized successfully

Testing models...
✅ Created user: 1 with wallet: 1
✅ User-wallet relationship verified
✅ Test user cleaned up

✅ All model tests passed!
```

### Step 5: Create Pydantic Schemas (45 minutes)

#### 5.1 Create app/schemas/user.py

```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from decimal import Decimal


class UserBase(BaseModel):
    phone_number: str = Field(..., min_length=10, max_length=20)
    username: Optional[str] = Field(None, max_length=50)


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    id: int
    is_active: bool
    is_blocked: bool
    created_at: datetime
    last_active: datetime
    
    class Config:
        from_attributes = True


class WalletResponse(BaseModel):
    id: int
    user_id: int
    balance: Decimal
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserWithWallet(UserResponse):
    wallet: Optional[WalletResponse] = None
```

#### 5.2 Update app/schemas/__init__.py

```python
from .user import (
    UserBase,
    UserCreate,
    UserResponse,
    WalletResponse,
    UserWithWallet
)

__all__ = [
    "UserBase",
    "UserCreate",
    "UserResponse",
    "WalletResponse",
    "UserWithWallet"
]
```

### Step 6: Verify Database Tables (15 minutes)

#### 6.1 Check Tables Created

```bash
PGPASSWORD=secret psql -h localhost -p 5432 -U postgres -d betting_db -c "\dt"
```

**Expected output:**
```
              List of relations
 Schema |   Name   | Type  |  Owner   
--------+----------+-------+----------
 public | users    | table | postgres
 public | wallets  | table | postgres
```

#### 6.2 Check Table Structure

```bash
PGPASSWORD=secret psql -h localhost -p 5432 -U postgres -d betting_db -c "\d users"
PGPASSWORD=secret psql -h localhost -p 5432 -U postgres -d betting_db -c "\d wallets"
```

### Day 2 Deliverables

By end of Day 2, you should have:

- [x] Database created (`betting_db`)
- [x] User model created and tested
- [x] Wallet model created and tested
- [x] Database relationships configured
- [x] Pydantic schemas created
- [x] Tables created in database
- [x] Model tests passing
- [x] Database initialization working

### Day 2 Checklist

- [ ] Database `betting_db` exists
- [ ] User model created with all fields
- [ ] Wallet model created with all fields
- [ ] Foreign key relationship configured
- [ ] Models can be imported without errors
- [ ] Tables created in database
- [ ] Can create User and Wallet instances
- [ ] User-wallet relationship works
- [ ] Pydantic schemas created
- [ ] Model tests pass

---

## Day 3: WhatsApp Business API Integration

**Duration:** 4-6 hours  
**Goal:** Implement WhatsApp service client for sending and receiving messages

### Prerequisites

- Day 2 completed successfully
- WhatsApp Business API credentials obtained
- WhatsApp Business API account configured

### Step 1: Create WhatsApp Service (2 hours)

#### 1.1 Create app/services/whatsapp.py

```python
import httpx
import logging
from typing import Dict, Any, Optional
from ..config import settings

logger = logging.getLogger(__name__)


class WhatsAppService:
    """Service for interacting with WhatsApp Business API"""
    
    def __init__(self):
        self.api_url = settings.WHATSAPP_API_URL
        self.phone_number_id = settings.WHATSAPP_PHONE_NUMBER_ID
        self.access_token = settings.WHATSAPP_ACCESS_TOKEN
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    async def send_message(
        self, 
        to: str, 
        message: str,
        reply_to_message_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send text message via WhatsApp Business API
        
        Args:
            to: Recipient phone number (with country code, no +)
            message: Text message to send
            reply_to_message_id: Optional message ID to reply to
            
        Returns:
            API response dict
            
        Raises:
            httpx.HTTPError: If API request fails
        """
        url = f"{self.api_url}/{self.phone_number_id}/messages"
        
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": message
            }
        }
        
        if reply_to_message_id:
            payload["context"] = {"message_id": reply_to_message_id}
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    url,
                    headers=self.headers,
                    json=payload
                )
                response.raise_for_status()
                result = response.json()
                logger.info(f"Message sent to {to}: {result.get('messages', [{}])[0].get('id', 'unknown')}")
                return result
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error sending message: {e.response.status_code} - {e.response.text}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Request error sending message: {e}")
            raise
    
    async def mark_as_read(self, message_id: str) -> Dict[str, Any]:
        """
        Mark message as read
        
        Args:
            message_id: WhatsApp message ID to mark as read
            
        Returns:
            API response dict
        """
        url = f"{self.api_url}/{self.phone_number_id}/messages"
        
        payload = {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message_id
        }
        
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(
                    url,
                    headers=self.headers,
                    json=payload
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.warning(f"Error marking message as read: {e}")
            # Non-critical, don't raise
            return {}


# Singleton instance
whatsapp_service = WhatsAppService()
```

### Step 2: Test WhatsApp Service (30 minutes)

#### 2.1 Create Test Script

Create `test_whatsapp.py`:

```python
"""Test WhatsApp service"""
import asyncio
from app.services.whatsapp import whatsapp_service
from app.config import settings

async def test_send_message():
    """Test sending a message"""
    # Replace with your test phone number
    test_number = "27821234567"  # Format: country code + number (no +)
    
    try:
        message = "Hello! This is a test message from MyKasiBets platform."
        result = await whatsapp_service.send_message(
            to=test_number,
            message=message
        )
        print(f"✅ Message sent successfully!")
        print(f"   Message ID: {result.get('messages', [{}])[0].get('id', 'unknown')}")
        return True
    except Exception as e:
        print(f"❌ Error sending message: {e}")
        return False

async def test_mark_as_read():
    """Test marking message as read"""
    # This requires a real message ID from a received message
    test_message_id = "wamid.test123"
    
    try:
        result = await whatsapp_service.mark_as_read(test_message_id)
        print("✅ Mark as read called (may fail if message ID is invalid)")
        return True
    except Exception as e:
        print(f"⚠️  Mark as read test: {e}")
        return True  # Non-critical

if __name__ == "__main__":
    print("=" * 50)
    print("WhatsApp Service Test")
    print("=" * 50)
    print(f"API URL: {settings.WHATSAPP_API_URL}")
    print(f"Phone Number ID: {settings.WHATSAPP_PHONE_NUMBER_ID}")
    print()
    
    # Test send message
    print("Testing send_message...")
    result = asyncio.run(test_send_message())
    
    if result:
        print("\n✅ WhatsApp service is working!")
    else:
        print("\n❌ WhatsApp service test failed")
        print("   Check your credentials in .env file")
```

#### 2.2 Run Test

```bash
python test_whatsapp.py
```

**Note:** This will actually send a WhatsApp message. Make sure you have:
- Valid WhatsApp Business API credentials
- Test phone number that's registered with your WhatsApp Business account

### Step 3: Create Utility Functions (30 minutes)

#### 3.1 Create app/utils/helpers.py

```python
"""Helper utility functions"""
import re
from typing import Optional


def normalize_phone_number(phone: str) -> str:
    """
    Normalize phone number to WhatsApp format
    
    Args:
        phone: Phone number in various formats
        
    Returns:
        Normalized phone number (country code + number, no + or spaces)
        
    Example:
        "+27 82 123 4567" -> "27821234567"
        "0821234567" -> "27821234567" (assumes South Africa)
    """
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone)
    
    # If starts with 0, assume South Africa and replace with 27
    if digits.startswith('0'):
        digits = '27' + digits[1:]
    
    # If doesn't start with country code, assume South Africa
    if not digits.startswith('27'):
        digits = '27' + digits
    
    return digits


def validate_phone_number(phone: str) -> bool:
    """
    Validate phone number format
    
    Args:
        phone: Phone number to validate
        
    Returns:
        True if valid, False otherwise
    """
    normalized = normalize_phone_number(phone)
    # South African numbers: 27 + 9 digits = 11 total
    return len(normalized) >= 10 and len(normalized) <= 15


def clean_message_text(text: str) -> str:
    """
    Clean and normalize message text
    
    Args:
        text: Raw message text
        
    Returns:
        Cleaned message text
    """
    if not text:
        return ""
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    # Convert to lowercase for command matching
    return text.lower().strip()
```

### Day 3 Deliverables

By end of Day 3, you should have:

- [x] WhatsApp service created
- [x] Message sending functionality implemented
- [x] Mark as read functionality implemented
- [x] Error handling implemented
- [x] Logging configured
- [x] Helper utilities created
- [x] WhatsApp service tested (if credentials available)

### Day 3 Checklist

- [ ] WhatsApp service class created
- [ ] `send_message` method implemented
- [ ] `mark_as_read` method implemented
- [ ] Error handling added
- [ ] Logging configured
- [ ] Helper functions created
- [ ] Phone number normalization works
- [ ] Service can be imported without errors
- [ ] Test script created (optional: run if credentials available)

---

## Day 4: Message Router & User Registration

**Duration:** 5-7 hours  
**Goal:** Implement message routing logic and automatic user registration

### Prerequisites

- Day 3 completed successfully
- WhatsApp service working
- Database models ready

### Step 1: Create Message Router Service (3 hours)

#### 1.1 Create app/services/message_router.py

```python
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from decimal import Decimal
import logging

from ..models.user import User
from ..models.wallet import Wallet
from .whatsapp import whatsapp_service
from ..utils.helpers import normalize_phone_number, clean_message_text

logger = logging.getLogger(__name__)


class MessageRouter:
    """Routes incoming WhatsApp messages to appropriate handlers"""
    
    def __init__(self):
        # In-memory state storage (replace with Redis in production)
        self.user_states: Dict[int, Dict[str, Any]] = {}
    
    async def route_message(
        self,
        from_number: str,
        message_text: str,
        message_id: str,
        db: Session
    ) -> None:
        """
        Route incoming WhatsApp message to appropriate handler
        
        Args:
            from_number: Sender's phone number (format: 27821234567)
            message_text: Message content
            message_id: WhatsApp message ID
            db: Database session
        """
        try:
            # Mark message as read
            await whatsapp_service.mark_as_read(message_id)
            
            # Normalize phone number
            normalized_phone = normalize_phone_number(from_number)
            
            # Clean message
            clean_message = clean_message_text(message_text)
            
            # Get or create user
            user = db.query(User).filter(User.phone_number == normalized_phone).first()
            
            if not user:
                # New user - register
                user = await self._register_new_user(normalized_phone, db)
                response = self._get_welcome_message(user)
            elif user.is_blocked:
                response = "❌ Your account has been blocked. Please contact support."
            else:
                # Update last active
                user.last_active = func.now()
                db.commit()
                
                # Check if user has active state (multi-step flow)
                state = self.user_states.get(user.id)
                
                if state:
                    response = await self._handle_state_flow(user, clean_message, state, db)
                else:
                    response = await self._handle_main_menu(user, clean_message, db)
            
            # Send response
            await whatsapp_service.send_message(normalized_phone, response, reply_to_message_id=message_id)
            
        except Exception as e:
            logger.error(f"Error routing message: {e}", exc_info=True)
            try:
                await whatsapp_service.send_message(
                    normalized_phone,
                    "Sorry, something went wrong. Please try again later."
                )
            except:
                pass
    
    async def _register_new_user(self, phone_number: str, db: Session) -> User:
        """Register new user and create wallet"""
        try:
            user = User(phone_number=phone_number)
            db.add(user)
            db.flush()  # Get user.id before committing
            
            # Create wallet
            wallet = Wallet(user_id=user.id, balance=Decimal('0.00'))
            db.add(wallet)
            db.commit()
            db.refresh(user)
            
            logger.info(f"New user registered: {phone_number} (ID: {user.id})")
            return user
        except Exception as e:
            db.rollback()
            logger.error(f"Error registering user: {e}", exc_info=True)
            raise
    
    def _get_welcome_message(self, user: User) -> str:
        """Generate welcome message for new users"""
        return f"""🎉 Welcome to MyKasiBets!

You're all set! Your account has been created.

📱 Phone: {user.phone_number}
💰 Balance: R0.00

What would you like to do?

1️⃣ Check Balance
2️⃣ Play Games
3️⃣ Deposit Money
4️⃣ Help

Reply with the number of your choice."""
    
    async def _handle_main_menu(
        self,
        user: User,
        message: str,
        db: Session
    ) -> str:
        """Handle main menu selections"""
        
        # Command mappings
        commands = {
            '1': lambda: self._check_balance(user, db),
            '2': lambda: self._show_games(),
            '3': lambda: self._show_deposit_instructions(),
            '4': lambda: self._show_help(),
            'menu': lambda: self._show_main_menu(),
            'start': lambda: self._show_main_menu(),
            'balance': lambda: self._check_balance(user, db),
            'games': lambda: self._show_games(),
            'help': lambda: self._show_help(),
        }
        
        handler = commands.get(message)
        
        if handler:
            return await handler()
        else:
            return "❌ Invalid option. Reply 'menu' to see options."
    
    async def _check_balance(self, user: User, db: Session) -> str:
        """Get user's wallet balance"""
        wallet = db.query(Wallet).filter(Wallet.user_id == user.id).first()
        balance = wallet.balance if wallet else Decimal('0.00')
        
        return f"""💰 Your Balance: R{float(balance):.2f}

What would you like to do?

1️⃣ Play Games
2️⃣ Deposit Money
3️⃣ Withdraw Money
4️⃣ Back to Menu

Reply with number."""
    
    async def _show_games(self) -> str:
        """Show available games"""
        return """🎮 CHOOSE YOUR GAME:

1️⃣ Lucky Wheel (1-12) - Win 10x
2️⃣ Color Game - Win 3x
3️⃣ Pick 3 Numbers - Win 800x
4️⃣ Football Yes/No - Various odds

Reply with game number."""
    
    async def _show_deposit_instructions(self) -> str:
        """Show deposit instructions"""
        return """💳 DEPOSIT MONEY:

Send money via:
- 1Voucher
- SnapScan  
- Capitec
- Bank Transfer

Then send us:
📸 Proof of Payment
💵 Amount

Example: "Paid R50 SnapScan"

An admin will approve it within 5 minutes!"""
    
    def _show_help(self) -> str:
        """Show help information"""
        return """❓ HELP & COMMANDS:

'menu' - Main menu
'balance' - Check balance
'games' - See all games
'deposit' - Deposit info
'withdraw' - Withdrawal info
'help' - This message

📞 Support: support@mykasibets.com
⏰ Available 24/7"""
    
    def _show_main_menu(self) -> str:
        """Show main menu"""
        return """📱 MAIN MENU:

1️⃣ Check Balance
2️⃣ Play Games
3️⃣ Deposit Money
4️⃣ Help

Reply with number."""
    
    async def _handle_state_flow(
        self,
        user: User,
        message: str,
        state: Dict[str, Any],
        db: Session
    ) -> str:
        """Handle multi-step conversation flows"""
        # This will be expanded in later phases for deposits, withdrawals, etc.
        # For now, clear state and return to main menu
        self.user_states.pop(user.id, None)
        return await self._handle_main_menu(user, message, db)


# Singleton instance
message_router = MessageRouter()
```

### Step 2: Test Message Router (1 hour)

#### 2.1 Create Test Script

Create `test_message_router.py`:

```python
"""Test message router"""
import asyncio
from app.database import SessionLocal
from app.services.message_router import message_router
from app.models import User

async def test_user_registration():
    """Test new user registration"""
    db = SessionLocal()
    try:
        test_phone = "27829999999"
        
        # Delete if exists
        existing = db.query(User).filter(User.phone_number == test_phone).first()
        if existing:
            db.delete(existing)
            db.commit()
        
        # Simulate incoming message
        await message_router.route_message(
            from_number=test_phone,
            message_text="Hello",
            message_id="test_msg_123",
            db=db
        )
        
        # Verify user created
        user = db.query(User).filter(User.phone_number == test_phone).first()
        assert user is not None, "User should be created"
        assert user.wallet is not None, "Wallet should be created"
        print(f"✅ User registration test passed: User ID {user.id}")
        
        # Cleanup
        db.delete(user)
        db.commit()
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("Testing message router...")
    asyncio.run(test_user_registration())
    print("✅ Message router tests passed!")
```

### Day 4 Deliverables

By end of Day 4, you should have:

- [x] Message router service created
- [x] User registration flow implemented
- [x] Main menu system working
- [x] Command parsing implemented
- [x] Basic commands responding (menu, balance, help, games)
- [x] User state management (basic)
- [x] Welcome message for new users
- [x] Error handling implemented

### Day 4 Checklist

- [ ] Message router class created
- [ ] `route_message` method implemented
- [ ] User registration flow works
- [ ] Wallet created for new users
- [ ] Main menu commands work
- [ ] Balance command works
- [ ] Help command works
- [ ] Games command works
- [ ] Error handling implemented
- [ ] Test script created

---

## Day 5: Webhook Endpoint & Testing

**Duration:** 4-6 hours  
**Goal:** Create webhook endpoint, integrate all components, and test end-to-end

### Prerequisites

- Day 4 completed successfully
- All services working
- WhatsApp Business API credentials ready

### Step 1: Create Webhook Endpoint (2 hours)

#### 1.1 Create app/api/webhook.py

```python
from fastapi import APIRouter, Request, Response, Depends, HTTPException
from sqlalchemy.orm import Session
import logging

from ..database import get_db
from ..config import settings
from ..services.message_router import message_router

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/webhook")
async def verify_webhook(request: Request):
    """
    Verify webhook endpoint for WhatsApp Business API
    
    WhatsApp will make a GET request with:
    - hub.mode = "subscribe"
    - hub.verify_token = your verification token
    - hub.challenge = challenge string to echo back
    """
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")
    
    if mode == "subscribe" and token == settings.WHATSAPP_VERIFY_TOKEN:
        logger.info("Webhook verified successfully")
        return Response(content=challenge, media_type="text/plain")
    else:
        logger.warning(f"Webhook verification failed: mode={mode}, token_match={token == settings.WHATSAPP_VERIFY_TOKEN}")
        raise HTTPException(status_code=403, detail="Verification failed")


@router.post("/webhook")
async def receive_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Receive incoming WhatsApp messages
    
    Payload structure:
    {
        "object": "whatsapp_business_account",
        "entry": [{
            "id": "WHATSAPP_BUSINESS_ACCOUNT_ID",
            "changes": [{
                "value": {
                    "messaging_product": "whatsapp",
                    "metadata": {...},
                    "messages": [{
                        "from": "27821234567",
                        "id": "wamid.XXX",
                        "timestamp": "1234567890",
                        "type": "text",
                        "text": {
                            "body": "Hello"
                        }
                    }]
                },
                "field": "messages"
            }]
        }]
    }
    """
    try:
        body = await request.json()
        
        # Log incoming webhook for debugging
        logger.info(f"Webhook received: {body.get('object', 'unknown')}")
        
        # Extract message data
        if body.get("object") == "whatsapp_business_account":
            for entry in body.get("entry", []):
                for change in entry.get("changes", []):
                    value = change.get("value", {})
                    
                    # Check if there are messages
                    messages = value.get("messages", [])
                    
                    for message in messages:
                        # Only process text messages for now
                        if message.get("type") == "text":
                            from_number = message.get("from")
                            message_text = message.get("text", {}).get("body", "")
                            message_id = message.get("id")
                            
                            if from_number and message_text and message_id:
                                # Route message to handler
                                await message_router.route_message(
                                    from_number,
                                    message_text,
                                    message_id,
                                    db
                                )
        
        return {"status": "ok"}
        
    except Exception as e:
        logger.error(f"Error processing webhook: {e}", exc_info=True)
        # Still return 200 to WhatsApp so they don't retry
        return {"status": "error", "message": str(e)}
```

#### 1.2 Update app/main.py

Add webhook router:

```python
# Add after CORS middleware
from .api import webhook

# Include routers
app.include_router(webhook.router, prefix="/api", tags=["webhook"])
```

### Step 2: Test Webhook Locally (1 hour)

#### 2.1 Start Server

```bash
uvicorn app.main:app --reload --port 8000
```

#### 2.2 Test Webhook Verification

Use curl or Postman:

```bash
curl "http://localhost:8000/api/webhook?hub.mode=subscribe&hub.verify_token=YOUR_VERIFY_TOKEN&hub.challenge=test123"
```

Should return: `test123`

#### 2.3 Test Webhook POST (Simulate)

Create `test_webhook.py`:

```python
"""Test webhook endpoint"""
import requests
import json

# Simulate WhatsApp webhook payload
payload = {
    "object": "whatsapp_business_account",
    "entry": [{
        "id": "test_entry",
        "changes": [{
            "value": {
                "messaging_product": "whatsapp",
                "metadata": {
                    "display_phone_number": "1234567890",
                    "phone_number_id": "test_phone_id"
                },
                "messages": [{
                    "from": "27821234567",
                    "id": "wamid.test123",
                    "timestamp": "1234567890",
                    "type": "text",
                    "text": {
                        "body": "Hello"
                    }
                }]
            },
            "field": "messages"
        }]
    }]
}

response = requests.post(
    "http://localhost:8000/api/webhook",
    json=payload
)

print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")
```

### Step 3: Deploy and Configure Webhook (2 hours)

#### 3.1 Deploy to Railway/Render

Follow deployment steps from Quick Start Guide.

#### 3.2 Configure Webhook in Meta Dashboard

1. Go to Meta Developer Console
2. Select your app
3. Go to WhatsApp → Configuration
4. Click "Edit" on Webhook
5. Enter:
   - **Callback URL**: `https://your-app.railway.app/api/webhook`
   - **Verify Token**: Same as `WHATSAPP_VERIFY_TOKEN` in `.env`
6. Click "Verify and Save"
7. Subscribe to "messages" field

#### 3.3 Test with Real WhatsApp

1. Send message from WhatsApp to your test number
2. Check server logs
3. Verify response received

### Step 4: End-to-End Testing (1 hour)

#### 4.1 Test Scenarios

1. **New User Registration**
   - Send "Hello" from new number
   - Should receive welcome message
   - User should be created in database

2. **Existing User Commands**
   - Send "menu"
   - Send "1" (balance)
   - Send "help"
   - All should respond correctly

3. **Error Handling**
   - Send invalid command
   - Should receive error message

#### 4.2 Create Test Checklist

- [ ] Webhook verification works
- [ ] Webhook receives messages
- [ ] New user registration works
- [ ] Welcome message sent
- [ ] Menu command works
- [ ] Balance command works
- [ ] Help command works
- [ ] Games command works
- [ ] Error messages work
- [ ] Database records created correctly

### Day 5 Deliverables

By end of Day 5, you should have:

- [x] Webhook endpoint created
- [x] Webhook verification working
- [x] Webhook receiving messages
- [x] End-to-end flow working
- [x] Deployed to hosting platform
- [x] Webhook configured in Meta Dashboard
- [x] Real WhatsApp messages working
- [x] All Phase 1 features complete

### Day 5 Checklist

- [ ] Webhook GET endpoint works (verification)
- [ ] Webhook POST endpoint works (receiving)
- [ ] Server deployed successfully
- [ ] Webhook URL configured in Meta
- [ ] Can receive real WhatsApp messages
- [ ] Can send WhatsApp responses
- [ ] All commands working
- [ ] Database operations working
- [ ] Logging working
- [ ] Error handling working

---

## Deliverables Checklist

### Code Deliverables

- [ ] Project structure created
- [ ] All Python packages installed
- [ ] Configuration system working
- [ ] Database models created
- [ ] Database tables created
- [ ] WhatsApp service implemented
- [ ] Message router implemented
- [ ] Webhook endpoint created
- [ ] All services integrated
- [ ] Error handling implemented
- [ ] Logging configured

### Documentation Deliverables

- [ ] README.md created
- [ ] Code comments added
- [ ] API documentation (FastAPI auto-docs)
- [ ] Environment setup documented
- [ ] Deployment instructions documented

### Testing Deliverables

- [ ] Unit tests for models
- [ ] Integration tests for services
- [ ] End-to-end tests for webhook
- [ ] Manual testing completed
- [ ] All tests passing

---

## Testing Strategy

### Unit Tests

Test individual components in isolation:
- Model creation and relationships
- Service methods
- Utility functions

### Integration Tests

Test component interactions:
- Database operations
- WhatsApp API calls (mocked)
- Message routing flow

### End-to-End Tests

Test complete user flows:
- New user registration
- Command processing
- Message sending

### Manual Testing

- Real WhatsApp messages
- Webhook verification
- Error scenarios

---

## Troubleshooting Guide

### Common Issues

**Webhook verification fails**
- Check `WHATSAPP_VERIFY_TOKEN` matches exactly
- Ensure webhook URL is accessible (HTTPS required)
- Check server logs for errors

**Messages not received**
- Verify webhook is subscribed to "messages" field
- Check server is running and accessible
- Review server logs for incoming webhooks

**Database errors**
- Verify PostgreSQL is running
- Check DATABASE_URL is correct
- Ensure database exists

**WhatsApp API errors**
- Verify access token is valid
- Check phone number ID is correct
- Ensure phone number is registered

---

## Next Steps

After completing Phase 1, proceed to:

### Phase 2: Core Systems (Week 2)
- Wallet service (credit/debit)
- Transaction logging
- Deposit/withdrawal flows
- Admin approval system

### Phase 3: Games (Week 3-4)
- Game engines (Lucky Wheel, Color Game, Pick 3, Football)
- Betting logic
- Win/loss calculation
- Game result generation

### Phase 4: Admin Dashboard (Week 4-5)
- React admin interface
- User management
- Deposit/withdrawal approval
- Bet settlement

### Phase 5: Testing & Beta (Week 5-6)
- Comprehensive testing
- Beta user testing
- Bug fixes
- Performance optimization

---

**End of Phase 1 Implementation Plan**


