# WhatsApp Betting Platform - Complete Python Implementation Guide

## Table of Contents
1. [Project Setup](#project-setup)
2. [Phase 1: Foundation](#phase-1-foundation)
3. [Phase 2: Core Systems](#phase-2-core-systems)
4. [Phase 3: Games](#phase-3-games)
5. [Phase 4: Admin Dashboard](#phase-4-admin)
6. [Phase 5: Testing](#phase-5-testing)

---

## Project Setup

### Directory Structure

```
betting-platform/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app entry point
│   ├── config.py               # Configuration management
│   ├── database.py             # Database connection
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── wallet.py
│   │   ├── bet.py
│   │   ├── deposit.py
│   │   └── admin.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py             # Pydantic schemas
│   │   ├── wallet.py
│   │   └── bet.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── whatsapp.py         # WhatsApp Business API client
│   │   ├── message_router.py   # Message routing logic
│   │   ├── wallet_service.py   # Wallet operations
│   │   └── games/
│   │       ├── __init__.py
│   │       ├── base.py         # Base game class
│   │       ├── lucky_wheel.py
│   │       ├── color_game.py
│   │       ├── pick3.py
│   │       └── football.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── webhook.py          # WhatsApp webhook
│   │   ├── admin.py            # Admin routes
│   │   └── deps.py             # Dependencies
│   └── utils/
│       ├── __init__.py
│       ├── security.py         # JWT, password hashing
│       └── helpers.py
├── tests/
│   ├── __init__.py
│   ├── test_wallet.py
│   ├── test_games.py
│   └── conftest.py
├── alembic/                    # Database migrations
│   ├── versions/
│   └── env.py
├── .env
├── .gitignore
├── requirements.txt
├── alembic.ini
└── README.md
```

### requirements.txt

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

# Redis & Celery
redis==5.0.1
celery==5.3.4

# Utilities
python-dotenv==1.0.0

# Testing
pytest==7.4.4
pytest-asyncio==0.23.3
```

---

## PHASE 1: Foundation (Week 1)

### Day 1: Configuration & Database Setup

#### config.py

```python
from pydantic_settings import BaseSettings
from functools import lru_cache

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
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
```

#### database.py

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from .config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=False  # Set to True for SQL logging during development
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    """
    Dependency for getting database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """
    Initialize database tables
    """
    Base.metadata.create_all(bind=engine)
```

#### models/user.py

```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from sqlalchemy.orm import relationship
from ..database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(20), unique=True, nullable=False, index=True)
    username = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True)
    is_blocked = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_active = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    wallet = relationship("Wallet", back_populates="user", uselist=False)
    bets = relationship("Bet", back_populates="user")
    deposits = relationship("Deposit", back_populates="user")
    withdrawals = relationship("Withdrawal", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")
```

#### models/wallet.py

```python
from sqlalchemy import Column, Integer, Numeric, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from decimal import Decimal
from ..database import Base

class Wallet(Base):
    __tablename__ = "wallets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    balance = Column(Numeric(10, 2), default=Decimal('0.00'), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="wallet")

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    type = Column(String(20), nullable=False)  # deposit, withdrawal, bet, win
    amount = Column(Numeric(10, 2), nullable=False)
    balance_before = Column(Numeric(10, 2), nullable=False)
    balance_after = Column(Numeric(10, 2), nullable=False)
    reference_id = Column(Integer, nullable=True)
    description = Column(String(200), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    user = relationship("User", back_populates="transactions")
```

#### models/bet.py

```python
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from ..database import Base

class Bet(Base):
    __tablename__ = "bets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    game_type = Column(String(50), nullable=False)
    stake_amount = Column(Numeric(10, 2), nullable=False)
    user_selection = Column(String(100), nullable=True)
    game_result = Column(String(100), nullable=True)
    status = Column(String(20), default='pending', index=True)  # pending, won, lost
    potential_win = Column(Numeric(10, 2), nullable=True)
    actual_win = Column(Numeric(10, 2), default=0.00)
    odds = Column(Numeric(10, 2), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    settled_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="bets")
```

### Day 2: WhatsApp Business API Integration

#### services/whatsapp.py

```python
import httpx
import logging
from typing import Dict, Any, Optional
from ..config import settings

logger = logging.getLogger(__name__)

class WhatsAppService:
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
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers=self.headers,
                    json=payload,
                    timeout=10.0
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error sending WhatsApp message: {e}")
            raise
    
    async def send_interactive_buttons(
        self,
        to: str,
        body_text: str,
        buttons: list[Dict[str, str]],
        header_text: Optional[str] = None,
        footer_text: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send interactive button message
        
        Args:
            to: Recipient phone number
            body_text: Main message text
            buttons: List of button dicts with 'id' and 'title'
            header_text: Optional header
            footer_text: Optional footer
            
        Example:
            buttons = [
                {"id": "btn_1", "title": "Check Balance"},
                {"id": "btn_2", "title": "Play Games"}
            ]
        """
        url = f"{self.api_url}/{self.phone_number_id}/messages"
        
        button_components = [
            {
                "type": "button",
                "reply": {
                    "id": btn["id"],
                    "title": btn["title"]
                }
            }
            for btn in buttons[:3]  # WhatsApp allows max 3 buttons
        ]
        
        interactive_body = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {"text": body_text},
                "action": {"buttons": button_components}
            }
        }
        
        if header_text:
            interactive_body["interactive"]["header"] = {
                "type": "text",
                "text": header_text
            }
        
        if footer_text:
            interactive_body["interactive"]["footer"] = {
                "text": footer_text
            }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers=self.headers,
                    json=interactive_body,
                    timeout=10.0
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error sending interactive message: {e}")
            raise
    
    async def mark_as_read(self, message_id: str) -> Dict[str, Any]:
        """Mark message as read"""
        url = f"{self.api_url}/{self.phone_number_id}/messages"
        
        payload = {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message_id
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers=self.headers,
                    json=payload,
                    timeout=5.0
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Error marking message as read: {e}")
            # Non-critical, don't raise
            return {}

# Singleton instance
whatsapp_service = WhatsAppService()
```

### Day 3: Message Router & User Registration

#### services/message_router.py

```python
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from decimal import Decimal
import logging

from ..models.user import User
from ..models.wallet import Wallet
from .whatsapp import whatsapp_service

logger = logging.getLogger(__name__)

class MessageRouter:
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
            
            # Clean message
            clean_message = message_text.lower().strip()
            
            # Get or create user
            user = db.query(User).filter(User.phone_number == from_number).first()
            
            if not user:
                # New user - register
                user = await self._register_new_user(from_number, db)
                response = self._get_welcome_message(user)
            elif user.is_blocked:
                response = "Your account has been blocked. Please contact support."
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
            await whatsapp_service.send_message(from_number, response)
            
        except Exception as e:
            logger.error(f"Error routing message: {e}", exc_info=True)
            await whatsapp_service.send_message(
                from_number,
                "Sorry, something went wrong. Please try again."
            )
    
    async def _register_new_user(self, phone_number: str, db: Session) -> User:
        """Register new user and create wallet"""
        user = User(phone_number=phone_number)
        db.add(user)
        db.flush()  # Get user.id before committing
        
        # Create wallet
        wallet = Wallet(user_id=user.id, balance=Decimal('0.00'))
        db.add(wallet)
        db.commit()
        db.refresh(user)
        
        logger.info(f"New user registered: {phone_number}")
        return user
    
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
            '1': self._check_balance,
            '2': self._show_games,
            '3': self._show_deposit_instructions,
            '4': self._show_help,
            'menu': lambda u, d: self._show_main_menu(),
            'start': lambda u, d: self._show_main_menu(),
            'balance': self._check_balance,
            'games': self._show_games,
            'help': lambda u, d: self._show_help(),
        }
        
        handler = commands.get(message)
        
        if handler:
            return await handler(user, db)
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
    
    async def _show_games(self, user: User, db: Session) -> str:
        """Show available games"""
        return """🎮 CHOOSE YOUR GAME:

1️⃣ Lucky Wheel (1-12) - Win 10x
2️⃣ Color Game - Win 3x
3️⃣ Pick 3 Numbers - Win 800x
4️⃣ Football Yes/No - Various odds

Reply with game number."""
    
    async def _show_deposit_instructions(self, user: User, db: Session) -> str:
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
        # Implement state-based flows (deposits, withdrawals, etc.)
        # This will be expanded in later phases
        return "Processing..."

# Singleton instance
message_router = MessageRouter()
```

### Day 4: FastAPI Webhook Endpoint

#### api/webhook.py

```python
from fastapi import APIRouter, Request, Response, Depends, HTTPException
from sqlalchemy.orm import Session
import logging
import hmac
import hashlib

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
        logger.warning("Webhook verification failed")
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
        logger.info(f"Webhook received: {body}")
        
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

#### main.py

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from .config import settings
from .database import init_db
from .api import webhook, admin

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="MyKasiBets WhatsApp Betting Platform",
    description="MVP WhatsApp-based betting platform",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(webhook.router, prefix="/api", tags=["webhook"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    logger.info("Starting up application...")
    init_db()
    logger.info("Database initialized")

@app.get("/")
async def root():
    return {
        "message": "MyKasiBets WhatsApp Betting Platform API",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Disable in production
    )
```

---

## PHASE 2: Core Systems (Week 2)

### Day 5-7: Wallet System

#### services/wallet_service.py

```python
from sqlalchemy.orm import Session
from sqlalchemy import select
from decimal import Decimal
from typing import Optional
import logging

from ..models.user import User
from ..models.wallet import Wallet, Transaction

logger = logging.getLogger(__name__)

class WalletService:
    
    @staticmethod
    def get_balance(db: Session, user_id: int) -> Decimal:
        """Get user's current wallet balance"""
        wallet = db.query(Wallet).filter(Wallet.user_id == user_id).first()
        return wallet.balance if wallet else Decimal('0.00')
    
    @staticmethod
    def credit(
        db: Session,
        user_id: int,
        amount: Decimal,
        description: str,
        reference_id: Optional[int] = None
    ) -> Decimal:
        """
        Credit user's wallet
        
        Uses database transaction to ensure atomicity
        
        Returns:
            New balance after credit
        """
        try:
            # Lock wallet row for update
            wallet = db.query(Wallet).filter(
                Wallet.user_id == user_id
            ).with_for_update().first()
            
            if not wallet:
                raise ValueError(f"Wallet not found for user {user_id}")
            
            balance_before = wallet.balance
            balance_after = balance_before + amount
            
            # Update wallet
            wallet.balance = balance_after
            
            # Record transaction
            transaction = Transaction(
                user_id=user_id,
                type='credit',
                amount=amount,
                balance_before=balance_before,
                balance_after=balance_after,
                reference_id=reference_id,
                description=description
            )
            db.add(transaction)
            
            db.commit()
            
            logger.info(f"Credited R{amount} to user {user_id}. New balance: R{balance_after}")
            return balance_after
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error crediting wallet: {e}", exc_info=True)
            raise
    
    @staticmethod
    def debit(
        db: Session,
        user_id: int,
        amount: Decimal,
        description: str,
        reference_id: Optional[int] = None
    ) -> Decimal:
        """
        Debit user's wallet
        
        Raises ValueError if insufficient balance
        
        Returns:
            New balance after debit
        """
        try:
            # Lock wallet row for update
            wallet = db.query(Wallet).filter(
                Wallet.user_id == user_id
            ).with_for_update().first()
            
            if not wallet:
                raise ValueError(f"Wallet not found for user {user_id}")
            
            balance_before = wallet.balance
            
            # Check sufficient balance
            if balance_before < amount:
                raise ValueError(
                    f"Insufficient balance. Available: R{balance_before}, Required: R{amount}"
                )
            
            balance_after = balance_before - amount
            
            # Update wallet
            wallet.balance = balance_after
            
            # Record transaction
            transaction = Transaction(
                user_id=user_id,
                type='debit',
                amount=amount,
                balance_before=balance_before,
                balance_after=balance_after,
                reference_id=reference_id,
                description=description
            )
            db.add(transaction)
            
            db.commit()
            
            logger.info(f"Debited R{amount} from user {user_id}. New balance: R{balance_after}")
            return balance_after
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error debiting wallet: {e}", exc_info=True)
            raise
    
    @staticmethod
    def get_transaction_history(
        db: Session,
        user_id: int,
        limit: int = 10
    ) -> list[Transaction]:
        """Get user's recent transaction history"""
        transactions = db.query(Transaction).filter(
            Transaction.user_id == user_id
        ).order_by(Transaction.created_at.desc()).limit(limit).all()
        
        return transactions

# Singleton instance
wallet_service = WalletService()
```

---

## PHASE 3: Games + Betting Engine (Week 3-4)

### Day 8-10: Game Engines

#### services/games/base.py

```python
from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Dict, Any, Tuple
import random

class BaseGame(ABC):
    """Base class for all games"""
    
    def __init__(self, name: str, min_bet: Decimal, max_bet: Decimal, multiplier: Decimal):
        self.name = name
        self.min_bet = min_bet
        self.max_bet = max_bet
        self.multiplier = multiplier
    
    @abstractmethod
    def get_description(self) -> str:
        """Return game description for users"""
        pass
    
    @abstractmethod
    def validate_bet(self, selection: str, stake: Decimal) -> Tuple[bool, str]:
        """
        Validate bet parameters
        
        Returns:
            (is_valid, error_message)
        """
        pass
    
    @abstractmethod
    def generate_result(self) -> Any:
        """Generate game result"""
        pass
    
    @abstractmethod
    def calculate_win(self, selection: str, stake: Decimal, result: Any) -> Tuple[bool, Decimal]:
        """
        Calculate if user won and win amount
        
        Returns:
            (did_win, win_amount)
        """
        pass
    
    @abstractmethod
    def format_result(
        self,
        selection: str,
        stake: Decimal,
        result: Any,
        won: bool,
        win_amount: Decimal
    ) -> str:
        """Format result message for user"""
        pass
```

#### services/games/lucky_wheel.py

```python
from decimal import Decimal
from typing import Tuple, Any
import random
from .base import BaseGame

class LuckyWheelGame(BaseGame):
    def __init__(self):
        super().__init__(
            name="Lucky Wheel",
            min_bet=Decimal('5.00'),
            max_bet=Decimal('100.00'),
            multiplier=Decimal('10.0')
        )
    
    def get_description(self) -> str:
        return f"""🎡 Lucky Wheel

Pick a number from 1-12
If you match the wheel result, win {self.multiplier}x!

Min bet: R{self.min_bet}
Max bet: R{self.max_bet}

Example: "wheel 7 10" (pick 7, bet R10)"""
    
    def validate_bet(self, selection: str, stake: Decimal) -> Tuple[bool, str]:
        # Validate selection
        try:
            number = int(selection)
            if number < 1 or number > 12:
                return False, "Please pick a number between 1-12"
        except ValueError:
            return False, "Invalid number. Pick between 1-12"
        
        # Validate stake
        if stake < self.min_bet:
            return False, f"Minimum bet is R{self.min_bet}"
        if stake > self.max_bet:
            return False, f"Maximum bet is R{self.max_bet}"
        
        return True, ""
    
    def generate_result(self) -> int:
        """Spin the wheel"""
        return random.randint(1, 12)
    
    def calculate_win(self, selection: str, stake: Decimal, result: int) -> Tuple[bool, Decimal]:
        user_number = int(selection)
        
        if user_number == result:
            win_amount = stake * self.multiplier
            return True, win_amount
        else:
            return False, Decimal('0.00')
    
    def format_result(
        self,
        selection: str,
        stake: Decimal,
        result: int,
        won: bool,
        win_amount: Decimal
    ) -> str:
        if won:
            return f"""🎉 WINNER!

Your pick: {selection}
Wheel landed on: {result}

You won: R{float(win_amount):.2f}!

Play again? Reply 'wheel'"""
        else:
            return f"""❌ Not this time!

Your pick: {selection}
Wheel landed on: {result}

Better luck next time!

Try again? Reply 'wheel'"""

# Singleton instance
lucky_wheel_game = LuckyWheelGame()
```

#### services/games/color_game.py

```python
from decimal import Decimal
from typing import Tuple
import random
from .base import BaseGame

class ColorGame(BaseGame):
    COLORS = ['red', 'green', 'blue', 'yellow']
    COLOR_EMOJIS = {
        'red': '🔴',
        'green': '🟢',
        'blue': '🔵',
        'yellow': '🟡'
    }
    
    def __init__(self):
        super().__init__(
            name="Color Game",
            min_bet=Decimal('2.00'),
            max_bet=Decimal('50.00'),
            multiplier=Decimal('3.0')
        )
    
    def get_description(self) -> str:
        return f"""🎨 Color Game

Pick a color: Red, Green, Blue, or Yellow
Match the color, win {self.multiplier}x!

Min bet: R{self.min_bet}
Max bet: R{self.max_bet}

Example: "color red 5" (pick red, bet R5)"""
    
    def validate_bet(self, selection: str, stake: Decimal) -> Tuple[bool, str]:
        # Validate selection
        color = selection.lower()
        if color not in self.COLORS:
            return False, f"Please pick: {', '.join(self.COLORS)}"
        
        # Validate stake
        if stake < self.min_bet:
            return False, f"Minimum bet is R{self.min_bet}"
        if stake > self.max_bet:
            return False, f"Maximum bet is R{self.max_bet}"
        
        return True, ""
    
    def generate_result(self) -> str:
        """Pick random color"""
        return random.choice(self.COLORS)
    
    def calculate_win(self, selection: str, stake: Decimal, result: str) -> Tuple[bool, Decimal]:
        if selection.lower() == result:
            win_amount = stake * self.multiplier
            return True, win_amount
        else:
            return False, Decimal('0.00')
    
    def format_result(
        self,
        selection: str,
        stake: Decimal,
        result: str,
        won: bool,
        win_amount: Decimal
    ) -> str:
        selection_lower = selection.lower()
        user_emoji = self.COLOR_EMOJIS.get(selection_lower, '')
        result_emoji = self.COLOR_EMOJIS.get(result, '')
        
        if won:
            return f"""🎉 COLOR MATCH!

Your pick: {user_emoji} {selection_lower.upper()}
Result: {result_emoji} {result.upper()}

You won: R{float(win_amount):.2f}!

Play again? Reply 'color'"""
        else:
            return f"""❌ No match!

Your pick: {user_emoji} {selection_lower.upper()}
Result: {result_emoji} {result.upper()}

Try again? Reply 'color'"""

# Singleton instance
color_game = ColorGame()
```

Continue in next file for space...

---

## Quick Start Commands

### Setup
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Database
```bash
# Create database
createdb betting_db

# Run migrations
alembic upgrade head
```

### Run Server
```bash
uvicorn app.main:app --reload --port 8000
```

### Testing
```bash
pytest tests/ -v
```

### Deploy to Railway
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link project
railway link

# Deploy
railway up
```

---

END OF PYTHON IMPLEMENTATION GUIDE (Part 1)
See supplementary files for complete games, admin routes, and testing code.
