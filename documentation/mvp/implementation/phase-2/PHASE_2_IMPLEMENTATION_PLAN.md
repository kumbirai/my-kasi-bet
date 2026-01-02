# Phase 2 Implementation Plan
## WhatsApp Betting Platform MVP - Core Systems Week

**Version:** 1.0
**Date:** January 2026
**Duration:** Week 2 (5 days)
**Goal:** Implement wallet service with credit/debit operations, transaction logging, deposit/withdrawal flows, and admin approval system

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Phase 2 Objectives](#phase-2-objectives)
3. [Success Criteria](#success-criteria)
4. [Prerequisites](#prerequisites)
5. [Day 1: Wallet Service & Transaction System](#day-1-wallet-service--transaction-system)
6. [Day 2: Deposit Flow & Payment Integration](#day-2-deposit-flow--payment-integration)
7. [Day 3: Withdrawal System](#day-3-withdrawal-system)
8. [Day 4: Admin Models & Basic API Endpoints](#day-4-admin-models--basic-api-endpoints)
9. [Day 5: Testing & Integration](#day-5-testing--integration)
10. [Deliverables Checklist](#deliverables-checklist)
11. [Testing Strategy](#testing-strategy)
12. [Troubleshooting Guide](#troubleshooting-guide)
13. [Next Steps](#next-steps)

---

## Executive Summary

Phase 2 builds upon the foundation established in Phase 1 by implementing the core financial systems of the platform. This phase focuses on:

- **Wallet Service**: Robust credit/debit operations with ACID transaction guarantees
- **Transaction Logging**: Complete audit trail of all financial movements
- **Deposit System**: Multi-payment provider support with manual approval workflow
- **Withdrawal System**: Secure withdrawal requests with admin verification
- **Admin Foundation**: Database models and API endpoints for administrative operations

By the end of Phase 2, the system will be able to:
- Process deposits via multiple payment methods (1Voucher, SnapScan, Bank Transfer, Capitec)
- Maintain accurate wallet balances with transaction atomicity
- Handle withdrawal requests with admin approval workflow
- Log all financial transactions for audit purposes
- Provide admin API endpoints for deposit/withdrawal approval
- Prevent common financial bugs (race conditions, double-spending, negative balances)

---

## Phase 2 Objectives

### Primary Objectives

1. ✅ **Wallet Service**
   - Implement atomic credit/debit operations
   - Add balance validation and constraints
   - Create transaction logging for all wallet changes
   - Implement optimistic locking to prevent race conditions
   - Add wallet operation rollback support

2. ✅ **Transaction System**
   - Design transaction model with complete audit trail
   - Implement transaction creation for all financial events
   - Add transaction history queries
   - Create transaction export functionality
   - Implement balance snapshot verification

3. ✅ **Deposit Flow**
   - Create deposit request model
   - Implement multi-payment provider support
   - Build deposit submission via WhatsApp
   - Add proof of payment handling
   - Create admin approval/rejection workflow
   - Implement automatic wallet crediting on approval

4. ✅ **Withdrawal System**
   - Create withdrawal request model
   - Implement withdrawal submission via WhatsApp
   - Add balance validation before withdrawal
   - Build admin approval workflow
   - Implement automatic wallet debiting
   - Add withdrawal limits and fraud checks

5. ✅ **Admin Foundation**
   - Create admin user model with role-based access
   - Implement JWT authentication for admin API
   - Build admin API endpoints for deposit approval
   - Build admin API endpoints for withdrawal approval
   - Add admin activity logging

### Secondary Objectives

- Implement Redis caching for wallet balances
- Add rate limiting for withdrawal requests
- Create notification system for admins
- Implement comprehensive error handling
- Add detailed logging for all financial operations
- Create database migration scripts

---

## Success Criteria

Phase 2 is considered complete when:

### Functional Requirements

- [ ] Users can submit deposit requests via WhatsApp
- [ ] System supports multiple payment methods (1Voucher, SnapScan, Bank Transfer, Capitec)
- [ ] Users can attach proof of payment (image/reference number)
- [ ] Admins can approve/reject deposit requests
- [ ] Wallet is credited automatically on deposit approval
- [ ] Users can request withdrawals via WhatsApp
- [ ] System validates sufficient balance before withdrawal
- [ ] Admins can approve/reject withdrawal requests
- [ ] Wallet is debited automatically on withdrawal approval
- [ ] All financial transactions are logged with complete audit trail
- [ ] Users can check transaction history via WhatsApp
- [ ] Balance integrity is maintained (no negative balances)
- [ ] No race conditions in concurrent wallet operations

### Technical Requirements

- [ ] Wallet operations use database transactions (ACID compliance)
- [ ] Transaction model captures all required audit fields
- [ ] Deposit/withdrawal models include all necessary metadata
- [ ] Admin authentication uses JWT tokens
- [ ] API endpoints follow REST conventions
- [ ] All financial amounts use Decimal type (no floating point)
- [ ] Optimistic locking prevents double-processing
- [ ] Database migrations are reversible
- [ ] Code follows Python best practices with type hints
- [ ] Error handling covers all edge cases

### Testing Requirements

- [ ] Unit tests for wallet service operations
- [ ] Integration tests for deposit flow
- [ ] Integration tests for withdrawal flow
- [ ] Race condition tests for concurrent operations
- [ ] Balance integrity tests
- [ ] Transaction logging verification tests
- [ ] Admin authentication tests
- [ ] End-to-end tests for complete flows

---

## Prerequisites

Before starting Phase 2, ensure:

- [ ] Phase 1 is fully complete and tested
- [ ] FastAPI server is running without errors
- [ ] PostgreSQL database is accessible
- [ ] User registration and basic commands are working
- [ ] WhatsApp webhook is receiving and responding to messages
- [ ] Redis is installed and running (optional but recommended)
- [ ] Development environment is set up
- [ ] All Phase 1 tests are passing

### Required Tools

- Python 3.10+ with FastAPI
- PostgreSQL 14+
- Redis 6+ (optional for Phase 2)
- Alembic for database migrations
- pytest for testing
- Postman or curl for API testing

---

## Day 1: Wallet Service & Transaction System

**Duration:** 5-7 hours
**Goal:** Implement robust wallet service with atomic operations and complete transaction logging

### Prerequisites

- Phase 1 completed
- Database models (User, Wallet) already exist
- Basic wallet table created

### Step 1: Enhance Transaction Model (1 hour)

#### 1.1 Update app/models/wallet.py

Add the Transaction model if not already present from Phase 1:

```python
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, func, Index
from sqlalchemy.orm import relationship
from decimal import Decimal
from ..database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Transaction details
    type = Column(String(20), nullable=False, index=True)  # deposit, withdrawal, bet, win, refund
    amount = Column(Numeric(10, 2), nullable=False)

    # Balance snapshots for audit
    balance_before = Column(Numeric(10, 2), nullable=False)
    balance_after = Column(Numeric(10, 2), nullable=False)

    # Reference to related entity
    reference_type = Column(String(20), nullable=True)  # deposit_id, withdrawal_id, bet_id
    reference_id = Column(Integer, nullable=True)

    # Metadata
    description = Column(String(200), nullable=True)
    metadata = Column(String(500), nullable=True)  # JSON string for additional data

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    # Relationships
    user = relationship("User", back_populates="transactions")

    # Composite index for efficient queries
    __table_args__ = (
        Index('ix_user_created', 'user_id', 'created_at'),
        Index('ix_user_type', 'user_id', 'type'),
    )

    def __repr__(self):
        return f"<Transaction(id={self.id}, user_id={self.user_id}, type={self.type}, amount={self.amount})>"
```

#### 1.2 Update User Model Relationship

Add to `app/models/user.py`:

```python
# Add this to the User class relationships section
transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")
```

### Step 2: Create Wallet Service (2.5 hours)

#### 2.1 Create app/services/wallet_service.py

```python
from typing import Optional, Dict, Any, List
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from datetime import datetime
import logging
import json

from ..models.user import User
from ..models.wallet import Wallet, Transaction
from ..database import get_db

logger = logging.getLogger(__name__)


class InsufficientBalanceError(Exception):
    """Raised when wallet has insufficient balance"""
    pass


class WalletNotFoundError(Exception):
    """Raised when wallet doesn't exist"""
    pass


class WalletService:
    """
    Service for handling all wallet operations with ACID guarantees

    All operations that modify wallet balance MUST use this service
    to ensure proper transaction logging and balance integrity.
    """

    @staticmethod
    def get_balance(user_id: int, db: Session) -> Decimal:
        """
        Get current wallet balance for a user

        Args:
            user_id: User ID
            db: Database session

        Returns:
            Current balance as Decimal

        Raises:
            WalletNotFoundError: If wallet doesn't exist
        """
        wallet = db.query(Wallet).filter(Wallet.user_id == user_id).first()

        if not wallet:
            raise WalletNotFoundError(f"Wallet not found for user {user_id}")

        return wallet.balance

    @staticmethod
    def credit(
        user_id: int,
        amount: Decimal,
        transaction_type: str,
        description: str,
        db: Session,
        reference_type: Optional[str] = None,
        reference_id: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Transaction:
        """
        Credit (add money to) a user's wallet

        This operation is atomic - either both wallet update and transaction log
        succeed, or both are rolled back.

        Args:
            user_id: User ID
            amount: Amount to credit (must be positive)
            transaction_type: Type of transaction (deposit, win, refund)
            description: Human-readable description
            db: Database session
            reference_type: Optional reference type (deposit_id, bet_id)
            reference_id: Optional reference ID
            metadata: Optional additional data as dict

        Returns:
            Created Transaction object

        Raises:
            ValueError: If amount is not positive
            WalletNotFoundError: If wallet doesn't exist
        """
        if amount <= 0:
            raise ValueError(f"Credit amount must be positive, got {amount}")

        # Get wallet with row-level lock to prevent race conditions
        wallet = db.query(Wallet).filter(
            Wallet.user_id == user_id
        ).with_for_update().first()

        if not wallet:
            raise WalletNotFoundError(f"Wallet not found for user {user_id}")

        # Capture balance before
        balance_before = wallet.balance

        # Update balance
        wallet.balance += amount
        balance_after = wallet.balance

        # Create transaction log
        transaction = Transaction(
            user_id=user_id,
            type=transaction_type,
            amount=amount,
            balance_before=balance_before,
            balance_after=balance_after,
            reference_type=reference_type,
            reference_id=reference_id,
            description=description,
            metadata=json.dumps(metadata) if metadata else None
        )

        db.add(transaction)
        db.flush()  # Get transaction ID before commit

        logger.info(
            f"Credited wallet: user_id={user_id}, amount={amount}, "
            f"balance: {balance_before} -> {balance_after}, "
            f"transaction_id={transaction.id}"
        )

        return transaction

    @staticmethod
    def debit(
        user_id: int,
        amount: Decimal,
        transaction_type: str,
        description: str,
        db: Session,
        reference_type: Optional[str] = None,
        reference_id: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
        allow_negative: bool = False
    ) -> Transaction:
        """
        Debit (subtract money from) a user's wallet

        This operation is atomic - either both wallet update and transaction log
        succeed, or both are rolled back.

        Args:
            user_id: User ID
            amount: Amount to debit (must be positive)
            transaction_type: Type of transaction (withdrawal, bet)
            description: Human-readable description
            db: Database session
            reference_type: Optional reference type (withdrawal_id, bet_id)
            reference_id: Optional reference ID
            metadata: Optional additional data as dict
            allow_negative: Allow balance to go negative (default: False)

        Returns:
            Created Transaction object

        Raises:
            ValueError: If amount is not positive
            WalletNotFoundError: If wallet doesn't exist
            InsufficientBalanceError: If insufficient balance and allow_negative=False
        """
        if amount <= 0:
            raise ValueError(f"Debit amount must be positive, got {amount}")

        # Get wallet with row-level lock to prevent race conditions
        wallet = db.query(Wallet).filter(
            Wallet.user_id == user_id
        ).with_for_update().first()

        if not wallet:
            raise WalletNotFoundError(f"Wallet not found for user {user_id}")

        # Check sufficient balance
        if not allow_negative and wallet.balance < amount:
            raise InsufficientBalanceError(
                f"Insufficient balance: has {wallet.balance}, needs {amount}"
            )

        # Capture balance before
        balance_before = wallet.balance

        # Update balance
        wallet.balance -= amount
        balance_after = wallet.balance

        # Create transaction log
        transaction = Transaction(
            user_id=user_id,
            type=transaction_type,
            amount=amount,
            balance_before=balance_before,
            balance_after=balance_after,
            reference_type=reference_type,
            reference_id=reference_id,
            description=description,
            metadata=json.dumps(metadata) if metadata else None
        )

        db.add(transaction)
        db.flush()  # Get transaction ID before commit

        logger.info(
            f"Debited wallet: user_id={user_id}, amount={amount}, "
            f"balance: {balance_before} -> {balance_after}, "
            f"transaction_id={transaction.id}"
        )

        return transaction

    @staticmethod
    def get_transaction_history(
        user_id: int,
        db: Session,
        limit: int = 10,
        offset: int = 0,
        transaction_type: Optional[str] = None
    ) -> List[Transaction]:
        """
        Get transaction history for a user

        Args:
            user_id: User ID
            db: Database session
            limit: Maximum number of transactions to return
            offset: Number of transactions to skip
            transaction_type: Filter by transaction type (optional)

        Returns:
            List of Transaction objects, ordered by created_at desc
        """
        query = db.query(Transaction).filter(Transaction.user_id == user_id)

        if transaction_type:
            query = query.filter(Transaction.type == transaction_type)

        transactions = query.order_by(
            desc(Transaction.created_at)
        ).limit(limit).offset(offset).all()

        return transactions

    @staticmethod
    def verify_balance_integrity(user_id: int, db: Session) -> bool:
        """
        Verify wallet balance matches transaction history

        This is useful for debugging and audit purposes.

        Args:
            user_id: User ID
            db: Database session

        Returns:
            True if balance is correct, False otherwise
        """
        wallet = db.query(Wallet).filter(Wallet.user_id == user_id).first()

        if not wallet:
            logger.error(f"Wallet not found for user {user_id}")
            return False

        # Get all transactions
        transactions = db.query(Transaction).filter(
            Transaction.user_id == user_id
        ).order_by(Transaction.created_at).all()

        if not transactions:
            # No transactions, balance should be 0
            return wallet.balance == Decimal('0.00')

        # Last transaction's balance_after should match wallet balance
        last_transaction = transactions[-1]

        if wallet.balance != last_transaction.balance_after:
            logger.error(
                f"Balance mismatch for user {user_id}: "
                f"wallet={wallet.balance}, "
                f"last_transaction={last_transaction.balance_after}"
            )
            return False

        return True


# Export singleton instance
wallet_service = WalletService()
```

### Step 3: Create Pydantic Schemas (45 minutes)

#### 3.1 Create app/schemas/wallet.py

```python
from pydantic import BaseModel, Field, field_validator
from decimal import Decimal
from datetime import datetime
from typing import Optional


class TransactionBase(BaseModel):
    type: str
    amount: Decimal
    description: Optional[str] = None


class TransactionCreate(TransactionBase):
    user_id: int
    reference_type: Optional[str] = None
    reference_id: Optional[int] = None


class TransactionResponse(BaseModel):
    id: int
    user_id: int
    type: str
    amount: Decimal
    balance_before: Decimal
    balance_after: Decimal
    description: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class WalletBalanceResponse(BaseModel):
    user_id: int
    balance: Decimal
    updated_at: datetime

    class Config:
        from_attributes = True


class TransactionHistoryResponse(BaseModel):
    transactions: list[TransactionResponse]
    total: int
    limit: int
    offset: int
```

#### 3.2 Update app/schemas/__init__.py

```python
from .user import (
    UserBase,
    UserCreate,
    UserResponse,
    WalletResponse,
    UserWithWallet
)
from .wallet import (
    TransactionBase,
    TransactionCreate,
    TransactionResponse,
    WalletBalanceResponse,
    TransactionHistoryResponse
)

__all__ = [
    "UserBase",
    "UserCreate",
    "UserResponse",
    "WalletResponse",
    "UserWithWallet",
    "TransactionBase",
    "TransactionCreate",
    "TransactionResponse",
    "WalletBalanceResponse",
    "TransactionHistoryResponse"
]
```

### Step 4: Test Wallet Service (1.5 hours)

#### 4.1 Create tests/test_wallet_service.py

```python
import pytest
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models.user import User
from app.models.wallet import Wallet, Transaction
from app.services.wallet_service import (
    WalletService,
    InsufficientBalanceError,
    WalletNotFoundError
)

# Test database setup
TEST_DATABASE_URL = "postgresql://postgres:secret@localhost:5432/betting_test_db"

engine = create_engine(TEST_DATABASE_URL)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db():
    """Create test database"""
    Base.metadata.create_all(bind=engine)
    session = TestSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user(db):
    """Create test user with wallet"""
    user = User(phone_number="27821234567", username="testuser")
    db.add(user)
    db.flush()

    wallet = Wallet(user_id=user.id, balance=Decimal('100.00'))
    db.add(wallet)
    db.commit()
    db.refresh(user)

    return user


def test_get_balance(db, test_user):
    """Test getting wallet balance"""
    balance = WalletService.get_balance(test_user.id, db)
    assert balance == Decimal('100.00')


def test_credit_wallet(db, test_user):
    """Test crediting wallet"""
    transaction = WalletService.credit(
        user_id=test_user.id,
        amount=Decimal('50.00'),
        transaction_type='deposit',
        description='Test deposit',
        db=db
    )

    db.commit()

    # Verify balance
    new_balance = WalletService.get_balance(test_user.id, db)
    assert new_balance == Decimal('150.00')

    # Verify transaction
    assert transaction.amount == Decimal('50.00')
    assert transaction.balance_before == Decimal('100.00')
    assert transaction.balance_after == Decimal('150.00')
    assert transaction.type == 'deposit'


def test_debit_wallet(db, test_user):
    """Test debiting wallet"""
    transaction = WalletService.debit(
        user_id=test_user.id,
        amount=Decimal('30.00'),
        transaction_type='bet',
        description='Test bet',
        db=db
    )

    db.commit()

    # Verify balance
    new_balance = WalletService.get_balance(test_user.id, db)
    assert new_balance == Decimal('70.00')

    # Verify transaction
    assert transaction.amount == Decimal('30.00')
    assert transaction.balance_before == Decimal('100.00')
    assert transaction.balance_after == Decimal('70.00')


def test_insufficient_balance(db, test_user):
    """Test debit with insufficient balance"""
    with pytest.raises(InsufficientBalanceError):
        WalletService.debit(
            user_id=test_user.id,
            amount=Decimal('150.00'),
            transaction_type='bet',
            description='Test bet',
            db=db
        )


def test_transaction_history(db, test_user):
    """Test transaction history"""
    # Create multiple transactions
    WalletService.credit(test_user.id, Decimal('50.00'), 'deposit', 'Deposit 1', db)
    WalletService.debit(test_user.id, Decimal('20.00'), 'bet', 'Bet 1', db)
    WalletService.credit(test_user.id, Decimal('10.00'), 'win', 'Win 1', db)
    db.commit()

    # Get history
    history = WalletService.get_transaction_history(test_user.id, db, limit=10)

    assert len(history) == 3
    # Should be ordered by created_at desc
    assert history[0].type == 'win'
    assert history[1].type == 'bet'
    assert history[2].type == 'deposit'


def test_balance_integrity(db, test_user):
    """Test balance integrity verification"""
    # Create transactions
    WalletService.credit(test_user.id, Decimal('50.00'), 'deposit', 'Test', db)
    WalletService.debit(test_user.id, Decimal('20.00'), 'bet', 'Test', db)
    db.commit()

    # Verify integrity
    assert WalletService.verify_balance_integrity(test_user.id, db) is True


def test_concurrent_operations(db, test_user):
    """Test concurrent wallet operations don't cause race conditions"""
    # This test requires multiple database sessions to truly test concurrency
    # For now, we test sequential operations work correctly

    WalletService.credit(test_user.id, Decimal('10.00'), 'deposit', 'Test 1', db)
    WalletService.credit(test_user.id, Decimal('20.00'), 'deposit', 'Test 2', db)
    WalletService.debit(test_user.id, Decimal('15.00'), 'bet', 'Test 3', db)
    db.commit()

    final_balance = WalletService.get_balance(test_user.id, db)
    # 100 + 10 + 20 - 15 = 115
    assert final_balance == Decimal('115.00')

    # Verify integrity
    assert WalletService.verify_balance_integrity(test_user.id, db) is True
```

#### 4.2 Run Tests

```bash
# Create test database
PGPASSWORD=secret psql -h localhost -p 5432 -U postgres -c "CREATE DATABASE betting_test_db;"

# Run tests
pytest tests/test_wallet_service.py -v

# Drop test database when done
PGPASSWORD=secret psql -h localhost -p 5432 -U postgres -c "DROP DATABASE betting_test_db;"
```

### Day 1 Deliverables

By end of Day 1, you should have:

- [x] Enhanced Transaction model with audit fields
- [x] Wallet service with credit/debit operations
- [x] Row-level locking to prevent race conditions
- [x] Complete transaction logging
- [x] Transaction history queries
- [x] Balance integrity verification
- [x] Pydantic schemas for wallet operations
- [x] Comprehensive unit tests
- [x] All tests passing

### Day 1 Checklist

- [ ] Transaction model created with all audit fields
- [ ] Wallet service implements credit operation
- [ ] Wallet service implements debit operation
- [ ] Balance validation prevents negative balances
- [ ] Transaction logging works for all operations
- [ ] Transaction history query works
- [ ] Balance integrity verification works
- [ ] Pydantic schemas created
- [ ] Unit tests written and passing
- [ ] Code follows Python best practices
- [ ] Type hints used throughout
- [ ] Logging configured

### Common Issues & Solutions

**Issue:** Tests fail with "database does not exist"
- **Solution:** Create test database: `createdb betting_test_db`

**Issue:** Decimal precision errors
- **Solution:** Always use `Decimal('10.00')` not `Decimal(10.0)` or `10.00`

**Issue:** Race conditions in concurrent tests
- **Solution:** Use `with_for_update()` for row-level locking

**Issue:** Balance mismatch after transactions
- **Solution:** Always use WalletService methods, never update wallet.balance directly

---

## Day 2: Deposit Flow & Payment Integration

**Duration:** 5-7 hours
**Goal:** Implement deposit request system with multi-payment provider support and admin approval workflow

### Prerequisites

- Day 1 completed
- Wallet service tested and working
- Transaction logging operational

### Step 1: Create Deposit Model (1 hour)

#### 1.1 Create app/models/deposit.py

```python
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, func, Enum as SQLEnum
from sqlalchemy.orm import relationship
from decimal import Decimal
import enum
from ..database import Base


class DepositStatus(str, enum.Enum):
    """Deposit request status"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


class PaymentMethod(str, enum.Enum):
    """Supported payment methods"""
    VOUCHER_1 = "1voucher"
    SNAPSCAN = "snapscan"
    CAPITEC = "capitec"
    BANK_TRANSFER = "bank_transfer"
    OTHER = "other"


class Deposit(Base):
    __tablename__ = "deposits"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Deposit details
    amount = Column(Numeric(10, 2), nullable=False)
    payment_method = Column(SQLEnum(PaymentMethod), nullable=False)

    # Proof of payment
    proof_type = Column(String(20), nullable=True)  # reference_number, image_url
    proof_value = Column(String(500), nullable=True)  # The actual reference or URL

    # Status and workflow
    status = Column(SQLEnum(DepositStatus), default=DepositStatus.PENDING, nullable=False, index=True)

    # Admin review
    reviewed_by = Column(Integer, ForeignKey("admin_users.id"), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    rejection_reason = Column(String(200), nullable=True)

    # Transaction reference
    transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=True)

    # Metadata
    notes = Column(String(500), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)  # Optional expiry for pending deposits

    # Relationships
    user = relationship("User", back_populates="deposits")
    transaction = relationship("Transaction", foreign_keys=[transaction_id])

    def __repr__(self):
        return f"<Deposit(id={self.id}, user_id={self.user_id}, amount={self.amount}, status={self.status})>"
```

#### 1.2 Update User Model

Add to `app/models/user.py`:

```python
# Add this to the User class relationships section
deposits = relationship("Deposit", back_populates="user", cascade="all, delete-orphan")
```

### Step 2: Create Deposit Service (2.5 hours)

#### 2.1 Create app/services/deposit_service.py

```python
from typing import Optional, List, Dict, Any
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from datetime import datetime, timedelta
import logging

from ..models.deposit import Deposit, DepositStatus, PaymentMethod
from ..models.user import User
from .wallet_service import wallet_service
from .whatsapp import whatsapp_service

logger = logging.getLogger(__name__)


class DepositService:
    """Service for handling deposit requests and approvals"""

    @staticmethod
    def create_deposit_request(
        user_id: int,
        amount: Decimal,
        payment_method: PaymentMethod,
        proof_type: Optional[str],
        proof_value: Optional[str],
        notes: Optional[str],
        db: Session
    ) -> Deposit:
        """
        Create a new deposit request

        Args:
            user_id: User ID
            amount: Deposit amount
            payment_method: Payment method used
            proof_type: Type of proof (reference_number, image_url)
            proof_value: Actual proof value
            notes: Additional notes from user
            db: Database session

        Returns:
            Created Deposit object

        Raises:
            ValueError: If amount is invalid
        """
        if amount <= 0:
            raise ValueError(f"Deposit amount must be positive, got {amount}")

        # Minimum deposit validation
        MIN_DEPOSIT = Decimal('10.00')
        if amount < MIN_DEPOSIT:
            raise ValueError(f"Minimum deposit is R{MIN_DEPOSIT}")

        # Create deposit request
        deposit = Deposit(
            user_id=user_id,
            amount=amount,
            payment_method=payment_method,
            proof_type=proof_type,
            proof_value=proof_value,
            notes=notes,
            status=DepositStatus.PENDING,
            expires_at=datetime.utcnow() + timedelta(hours=24)  # 24 hour expiry
        )

        db.add(deposit)
        db.flush()

        logger.info(
            f"Deposit request created: deposit_id={deposit.id}, "
            f"user_id={user_id}, amount={amount}, method={payment_method}"
        )

        return deposit

    @staticmethod
    async def approve_deposit(
        deposit_id: int,
        admin_user_id: int,
        db: Session
    ) -> Deposit:
        """
        Approve a deposit request and credit user's wallet

        This operation is atomic - either deposit is approved AND wallet is credited,
        or both operations are rolled back.

        Args:
            deposit_id: Deposit ID to approve
            admin_user_id: Admin user ID approving the deposit
            db: Database session

        Returns:
            Updated Deposit object

        Raises:
            ValueError: If deposit is not in pending status
        """
        # Get deposit with lock
        deposit = db.query(Deposit).filter(
            Deposit.id == deposit_id
        ).with_for_update().first()

        if not deposit:
            raise ValueError(f"Deposit {deposit_id} not found")

        if deposit.status != DepositStatus.PENDING:
            raise ValueError(f"Deposit {deposit_id} is not pending (status: {deposit.status})")

        # Credit wallet using wallet service
        transaction = wallet_service.credit(
            user_id=deposit.user_id,
            amount=deposit.amount,
            transaction_type='deposit',
            description=f"Deposit via {deposit.payment_method.value}",
            db=db,
            reference_type='deposit',
            reference_id=deposit.id,
            metadata={
                'payment_method': deposit.payment_method.value,
                'approved_by': admin_user_id
            }
        )

        # Update deposit status
        deposit.status = DepositStatus.APPROVED
        deposit.reviewed_by = admin_user_id
        deposit.reviewed_at = datetime.utcnow()
        deposit.transaction_id = transaction.id

        db.flush()

        logger.info(
            f"Deposit approved: deposit_id={deposit_id}, "
            f"user_id={deposit.user_id}, amount={deposit.amount}, "
            f"transaction_id={transaction.id}"
        )

        # Notify user via WhatsApp
        try:
            user = db.query(User).filter(User.id == deposit.user_id).first()
            if user:
                message = f"""✅ DEPOSIT APPROVED

Amount: R{float(deposit.amount):.2f}
Method: {deposit.payment_method.value.replace('_', ' ').title()}
New Balance: R{float(transaction.balance_after):.2f}

Your account has been credited!
Reply 'balance' to check your balance."""

                await whatsapp_service.send_message(user.phone_number, message)
        except Exception as e:
            logger.error(f"Error sending deposit approval notification: {e}")

        return deposit

    @staticmethod
    async def reject_deposit(
        deposit_id: int,
        admin_user_id: int,
        rejection_reason: str,
        db: Session
    ) -> Deposit:
        """
        Reject a deposit request

        Args:
            deposit_id: Deposit ID to reject
            admin_user_id: Admin user ID rejecting the deposit
            rejection_reason: Reason for rejection
            db: Database session

        Returns:
            Updated Deposit object

        Raises:
            ValueError: If deposit is not in pending status
        """
        # Get deposit with lock
        deposit = db.query(Deposit).filter(
            Deposit.id == deposit_id
        ).with_for_update().first()

        if not deposit:
            raise ValueError(f"Deposit {deposit_id} not found")

        if deposit.status != DepositStatus.PENDING:
            raise ValueError(f"Deposit {deposit_id} is not pending (status: {deposit.status})")

        # Update deposit status
        deposit.status = DepositStatus.REJECTED
        deposit.reviewed_by = admin_user_id
        deposit.reviewed_at = datetime.utcnow()
        deposit.rejection_reason = rejection_reason

        db.flush()

        logger.info(
            f"Deposit rejected: deposit_id={deposit_id}, "
            f"user_id={deposit.user_id}, reason={rejection_reason}"
        )

        # Notify user via WhatsApp
        try:
            user = db.query(User).filter(User.id == deposit.user_id).first()
            if user:
                message = f"""❌ DEPOSIT REJECTED

Amount: R{float(deposit.amount):.2f}
Method: {deposit.payment_method.value.replace('_', ' ').title()}

Reason: {rejection_reason}

Please contact support if you have questions."""

                await whatsapp_service.send_message(user.phone_number, message)
        except Exception as e:
            logger.error(f"Error sending deposit rejection notification: {e}")

        return deposit

    @staticmethod
    def get_pending_deposits(db: Session, limit: int = 50) -> List[Deposit]:
        """
        Get all pending deposit requests

        Args:
            db: Database session
            limit: Maximum number of deposits to return

        Returns:
            List of pending Deposit objects
        """
        deposits = db.query(Deposit).filter(
            Deposit.status == DepositStatus.PENDING
        ).order_by(desc(Deposit.created_at)).limit(limit).all()

        return deposits

    @staticmethod
    def get_user_deposits(
        user_id: int,
        db: Session,
        limit: int = 10,
        status: Optional[DepositStatus] = None
    ) -> List[Deposit]:
        """
        Get deposit history for a user

        Args:
            user_id: User ID
            db: Database session
            limit: Maximum number of deposits to return
            status: Filter by status (optional)

        Returns:
            List of Deposit objects
        """
        query = db.query(Deposit).filter(Deposit.user_id == user_id)

        if status:
            query = query.filter(Deposit.status == status)

        deposits = query.order_by(desc(Deposit.created_at)).limit(limit).all()

        return deposits


# Export singleton instance
deposit_service = DepositService()
```

### Step 3: Update Message Router for Deposits (1.5 hours)

#### 3.1 Update app/services/message_router.py

Add deposit handling to the message router:

```python
# Add these imports at the top
from ..models.deposit import PaymentMethod
from .deposit_service import deposit_service

# Add this state type to handle deposit flow
class UserState:
    AWAITING_DEPOSIT_AMOUNT = "awaiting_deposit_amount"
    AWAITING_DEPOSIT_METHOD = "awaiting_deposit_method"
    AWAITING_DEPOSIT_PROOF = "awaiting_deposit_proof"

# Update the _handle_main_menu method to include deposit option
async def _handle_main_menu(self, user: User, message: str, db: Session) -> str:
    """Handle main menu selections"""

    commands = {
        '1': lambda: self._check_balance(user, db),
        '2': lambda: self._show_games(),
        '3': lambda: self._start_deposit_flow(user),  # New deposit flow
        '4': lambda: self._show_help(),
        'menu': lambda: self._show_main_menu(),
        'start': lambda: self._show_main_menu(),
        'balance': lambda: self._check_balance(user, db),
        'deposit': lambda: self._start_deposit_flow(user),  # New deposit flow
        'games': lambda: self._show_games(),
        'help': lambda: self._show_help(),
    }

    handler = commands.get(message)

    if handler:
        return await handler()
    else:
        return "❌ Invalid option. Reply 'menu' to see options."

# Add these new methods to MessageRouter class:

async def _start_deposit_flow(self, user: User) -> str:
    """Start deposit flow"""
    self.user_states[user.id] = {
        'state': UserState.AWAITING_DEPOSIT_AMOUNT
    }

    return """💰 DEPOSIT MONEY

Minimum deposit: R10
Maximum deposit: R10,000

How much would you like to deposit?
Example: 50 (for R50)

Reply 'cancel' to go back."""

async def _handle_state_flow(
    self,
    user: User,
    message: str,
    state: Dict[str, Any],
    db: Session
) -> str:
    """Handle multi-step conversation flows"""

    if message == 'cancel':
        self.user_states.pop(user.id, None)
        return await self._show_main_menu()

    current_state = state.get('state')

    if current_state == UserState.AWAITING_DEPOSIT_AMOUNT:
        return await self._handle_deposit_amount(user, message, state, db)
    elif current_state == UserState.AWAITING_DEPOSIT_METHOD:
        return await self._handle_deposit_method(user, message, state, db)
    elif current_state == UserState.AWAITING_DEPOSIT_PROOF:
        return await self._handle_deposit_proof(user, message, state, db)
    else:
        # Unknown state, clear and return to main menu
        self.user_states.pop(user.id, None)
        return await self._handle_main_menu(user, message, db)

async def _handle_deposit_amount(
    self,
    user: User,
    message: str,
    state: Dict[str, Any],
    db: Session
) -> str:
    """Handle deposit amount input"""
    try:
        amount = Decimal(message.strip())

        if amount < 10:
            return "❌ Minimum deposit is R10. Please enter a valid amount:"

        if amount > 10000:
            return "❌ Maximum deposit is R10,000. Please enter a valid amount:"

        # Store amount in state
        state['amount'] = amount
        state['state'] = UserState.AWAITING_DEPOSIT_METHOD

        return f"""💳 PAYMENT METHOD

Amount: R{float(amount):.2f}

Choose your payment method:

1️⃣ 1Voucher
2️⃣ SnapScan
3️⃣ Capitec
4️⃣ Bank Transfer

Reply with the number (1-4)"""

    except (ValueError, InvalidOperation):
        return "❌ Invalid amount. Please enter a number (e.g., 50):"

async def _handle_deposit_method(
    self,
    user: User,
    message: str,
    state: Dict[str, Any],
    db: Session
) -> str:
    """Handle payment method selection"""

    method_map = {
        '1': (PaymentMethod.VOUCHER_1, "1Voucher"),
        '2': (PaymentMethod.SNAPSCAN, "SnapScan"),
        '3': (PaymentMethod.CAPITEC, "Capitec"),
        '4': (PaymentMethod.BANK_TRANSFER, "Bank Transfer"),
    }

    method_info = method_map.get(message.strip())

    if not method_info:
        return "❌ Invalid choice. Please reply with a number (1-4):"

    payment_method, method_name = method_info

    # Store method in state
    state['payment_method'] = payment_method
    state['method_name'] = method_name
    state['state'] = UserState.AWAITING_DEPOSIT_PROOF

    amount = state['amount']

    # Provide payment instructions based on method
    instructions = self._get_payment_instructions(payment_method, amount)

    return f"""{instructions}

Once you've made the payment, send us the proof:
📸 Send payment reference number or screenshot

Example: "REF123456" or attach image"""

def _get_payment_instructions(self, method: PaymentMethod, amount: Decimal) -> str:
    """Get payment instructions for specific method"""

    if method == PaymentMethod.VOUCHER_1:
        return f"""💳 1VOUCHER PAYMENT

Amount: R{float(amount):.2f}

Buy a 1Voucher at any retailer
Then send us the voucher PIN"""

    elif method == PaymentMethod.SNAPSCAN:
        return f"""📱 SNAPSCAN PAYMENT

Amount: R{float(amount):.2f}

Scan this SnapScan code: [QR CODE]
Or use SnapScan to: 0821234567"""

    elif method == PaymentMethod.CAPITEC:
        return f"""🏦 CAPITEC PAYMENT

Amount: R{float(amount):.2f}

Send to: +27 82 123 4567
Name: MyKasiBets"""

    elif method == PaymentMethod.BANK_TRANSFER:
        return f"""🏦 BANK TRANSFER

Amount: R{float(amount):.2f}

Bank: FNB
Account: 1234567890
Branch: 250655
Account Type: Cheque
Reference: Your phone number"""

    return "Payment instructions will be provided."

async def _handle_deposit_proof(
    self,
    user: User,
    message: str,
    state: Dict[str, Any],
    db: Session
) -> str:
    """Handle deposit proof submission"""

    amount = state['amount']
    payment_method = state['payment_method']
    method_name = state['method_name']

    # Create deposit request
    try:
        deposit = deposit_service.create_deposit_request(
            user_id=user.id,
            amount=amount,
            payment_method=payment_method,
            proof_type='reference_number',
            proof_value=message.strip(),
            notes=f"Submitted via WhatsApp",
            db=db
        )

        db.commit()

        # Clear state
        self.user_states.pop(user.id, None)

        return f"""✅ DEPOSIT REQUEST SUBMITTED

Deposit ID: #{deposit.id}
Amount: R{float(amount):.2f}
Method: {method_name}

Your deposit is being reviewed.
You'll receive a notification within 5-30 minutes.

Reply 'menu' for main menu."""

    except Exception as e:
        logger.error(f"Error creating deposit request: {e}")
        self.user_states.pop(user.id, None)
        return f"""❌ Error submitting deposit request.

Please try again or contact support.

Reply 'menu' for main menu."""
```

### Step 4: Create Pydantic Schemas (30 minutes)

#### 4.1 Create app/schemas/deposit.py

```python
from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import datetime
from typing import Optional
from ..models.deposit import DepositStatus, PaymentMethod


class DepositCreate(BaseModel):
    amount: Decimal = Field(..., gt=0, description="Deposit amount")
    payment_method: PaymentMethod
    proof_type: Optional[str] = None
    proof_value: Optional[str] = None
    notes: Optional[str] = None


class DepositResponse(BaseModel):
    id: int
    user_id: int
    amount: Decimal
    payment_method: PaymentMethod
    status: DepositStatus
    proof_type: Optional[str]
    proof_value: Optional[str]
    created_at: datetime
    reviewed_at: Optional[datetime]
    rejection_reason: Optional[str]

    class Config:
        from_attributes = True


class DepositApproval(BaseModel):
    deposit_id: int
    admin_user_id: int


class DepositRejection(BaseModel):
    deposit_id: int
    admin_user_id: int
    rejection_reason: str = Field(..., min_length=10, max_length=200)
```

### Day 2 Deliverables

By end of Day 2, you should have:

- [x] Deposit model created with all fields
- [x] Deposit service with create/approve/reject operations
- [x] Multi-payment provider support
- [x] WhatsApp deposit flow integrated
- [x] Automatic wallet crediting on approval
- [x] User notifications for approval/rejection
- [x] Pydantic schemas for deposits
- [x] State management for deposit flow

### Day 2 Checklist

- [ ] Deposit model created
- [ ] Payment method enum defined
- [ ] Deposit status enum defined
- [ ] Deposit service implements create operation
- [ ] Deposit service implements approve operation
- [ ] Deposit service implements reject operation
- [ ] Wallet is credited on approval
- [ ] Transaction is logged for approved deposits
- [ ] WhatsApp deposit flow works
- [ ] Payment instructions provided for each method
- [ ] User receives notifications
- [ ] Pydantic schemas created
- [ ] State management working

### Common Issues & Solutions

**Issue:** Deposit approved but wallet not credited
- **Solution:** Check that transaction is committed within same database transaction

**Issue:** User state persists after deposit completion
- **Solution:** Ensure `user_states.pop(user.id, None)` is called after completion

**Issue:** Invalid decimal conversion in deposit amount
- **Solution:** Use `Decimal(str(amount))` not `Decimal(float(amount))`

**Issue:** WhatsApp notification fails but deposit approved
- **Solution:** This is acceptable - approval should complete even if notification fails

---

## Day 3: Withdrawal System

**Duration:** 4-6 hours
**Goal:** Implement withdrawal request system with balance validation and admin approval workflow

### Prerequisites

- Day 2 completed
- Deposit system tested and working
- Wallet service operational

### Step 1: Create Withdrawal Model (45 minutes)

#### 1.1 Create app/models/withdrawal.py

```python
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, func, Enum as SQLEnum
from sqlalchemy.orm import relationship
from decimal import Decimal
import enum
from ..database import Base


class WithdrawalStatus(str, enum.Enum):
    """Withdrawal request status"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class WithdrawalMethod(str, enum.Enum):
    """Withdrawal methods"""
    BANK_TRANSFER = "bank_transfer"
    CASH_PICKUP = "cash_pickup"
    EWALLET = "ewallet"


class Withdrawal(Base):
    __tablename__ = "withdrawals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Withdrawal details
    amount = Column(Numeric(10, 2), nullable=False)
    withdrawal_method = Column(SQLEnum(WithdrawalMethod), nullable=False)

    # Banking details (encrypted in production)
    bank_name = Column(String(100), nullable=True)
    account_number = Column(String(50), nullable=True)
    account_holder = Column(String(100), nullable=True)

    # Status and workflow
    status = Column(SQLEnum(WithdrawalStatus), default=WithdrawalStatus.PENDING, nullable=False, index=True)

    # Admin review
    reviewed_by = Column(Integer, ForeignKey("admin_users.id"), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    rejection_reason = Column(String(200), nullable=True)

    # Transaction references
    debit_transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=True)  # Wallet debit
    refund_transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=True)  # If rejected

    # Payment tracking
    payment_reference = Column(String(100), nullable=True)  # External payment reference
    paid_at = Column(DateTime(timezone=True), nullable=True)

    # Metadata
    notes = Column(String(500), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    # Relationships
    user = relationship("User", back_populates="withdrawals")
    debit_transaction = relationship("Transaction", foreign_keys=[debit_transaction_id])
    refund_transaction = relationship("Transaction", foreign_keys=[refund_transaction_id])

    def __repr__(self):
        return f"<Withdrawal(id={self.id}, user_id={self.user_id}, amount={self.amount}, status={self.status})>"
```

#### 1.2 Update User Model

Add to `app/models/user.py`:

```python
# Add this to the User class relationships section
withdrawals = relationship("Withdrawal", back_populates="user", cascade="all, delete-orphan")
```

### Step 2: Create Withdrawal Service (2 hours)

#### 2.1 Create app/services/withdrawal_service.py

```python
from typing import Optional, List
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime
import logging

from ..models.withdrawal import Withdrawal, WithdrawalStatus, WithdrawalMethod
from ..models.user import User
from .wallet_service import wallet_service, InsufficientBalanceError

logger = logging.getLogger(__name__)


class WithdrawalService:
    """Service for handling withdrawal requests and approvals"""

    # Withdrawal limits
    MIN_WITHDRAWAL = Decimal('50.00')
    MAX_WITHDRAWAL = Decimal('10000.00')
    DAILY_WITHDRAWAL_LIMIT = Decimal('20000.00')

    @staticmethod
    def create_withdrawal_request(
        user_id: int,
        amount: Decimal,
        withdrawal_method: WithdrawalMethod,
        bank_name: Optional[str],
        account_number: Optional[str],
        account_holder: Optional[str],
        notes: Optional[str],
        db: Session
    ) -> Withdrawal:
        """
        Create a withdrawal request and immediately debit wallet

        The wallet is debited when request is created (not when approved).
        If rejected, amount is refunded to wallet.

        Args:
            user_id: User ID
            amount: Withdrawal amount
            withdrawal_method: Withdrawal method
            bank_name: Bank name (for bank transfer)
            account_number: Account number
            account_holder: Account holder name
            notes: Additional notes
            db: Database session

        Returns:
            Created Withdrawal object

        Raises:
            ValueError: If amount is invalid or exceeds limits
            InsufficientBalanceError: If insufficient balance
        """
        # Validate amount
        if amount <= 0:
            raise ValueError(f"Withdrawal amount must be positive, got {amount}")

        if amount < WithdrawalService.MIN_WITHDRAWAL:
            raise ValueError(f"Minimum withdrawal is R{WithdrawalService.MIN_WITHDRAWAL}")

        if amount > WithdrawalService.MAX_WITHDRAWAL:
            raise ValueError(f"Maximum withdrawal is R{WithdrawalService.MAX_WITHDRAWAL}")

        # Check daily withdrawal limit
        daily_total = WithdrawalService._get_daily_withdrawal_total(user_id, db)
        if daily_total + amount > WithdrawalService.DAILY_WITHDRAWAL_LIMIT:
            remaining = WithdrawalService.DAILY_WITHDRAWAL_LIMIT - daily_total
            raise ValueError(f"Daily withdrawal limit exceeded. Remaining: R{remaining}")

        # Debit wallet immediately
        transaction = wallet_service.debit(
            user_id=user_id,
            amount=amount,
            transaction_type='withdrawal',
            description=f"Withdrawal request #{user_id}-pending",
            db=db,
            reference_type='withdrawal',
            reference_id=None,  # Will update after withdrawal created
            metadata={'withdrawal_method': withdrawal_method.value}
        )

        # Create withdrawal request
        withdrawal = Withdrawal(
            user_id=user_id,
            amount=amount,
            withdrawal_method=withdrawal_method,
            bank_name=bank_name,
            account_number=account_number,
            account_holder=account_holder,
            notes=notes,
            status=WithdrawalStatus.PENDING,
            debit_transaction_id=transaction.id
        )

        db.add(withdrawal)
        db.flush()

        # Update transaction reference
        transaction.reference_id = withdrawal.id
        transaction.description = f"Withdrawal request #{withdrawal.id}"

        logger.info(
            f"Withdrawal request created: withdrawal_id={withdrawal.id}, "
            f"user_id={user_id}, amount={amount}, "
            f"transaction_id={transaction.id}"
        )

        return withdrawal

    @staticmethod
    async def approve_withdrawal(
        withdrawal_id: int,
        admin_user_id: int,
        payment_reference: Optional[str],
        db: Session
    ) -> Withdrawal:
        """
        Approve a withdrawal request

        Wallet was already debited when request was created.
        This just marks it as approved and ready for payment.

        Args:
            withdrawal_id: Withdrawal ID to approve
            admin_user_id: Admin user ID approving
            payment_reference: External payment reference
            db: Database session

        Returns:
            Updated Withdrawal object
        """
        # Get withdrawal with lock
        withdrawal = db.query(Withdrawal).filter(
            Withdrawal.id == withdrawal_id
        ).with_for_update().first()

        if not withdrawal:
            raise ValueError(f"Withdrawal {withdrawal_id} not found")

        if withdrawal.status != WithdrawalStatus.PENDING:
            raise ValueError(f"Withdrawal {withdrawal_id} is not pending (status: {withdrawal.status})")

        # Update withdrawal status
        withdrawal.status = WithdrawalStatus.APPROVED
        withdrawal.reviewed_by = admin_user_id
        withdrawal.reviewed_at = datetime.utcnow()
        withdrawal.payment_reference = payment_reference
        withdrawal.paid_at = datetime.utcnow()

        db.flush()

        logger.info(
            f"Withdrawal approved: withdrawal_id={withdrawal_id}, "
            f"user_id={withdrawal.user_id}, amount={withdrawal.amount}"
        )

        # Notify user via WhatsApp
        try:
            from .whatsapp import whatsapp_service
            user = db.query(User).filter(User.id == withdrawal.user_id).first()
            if user:
                message = f"""✅ WITHDRAWAL APPROVED

Amount: R{float(withdrawal.amount):.2f}
Method: {withdrawal.withdrawal_method.value.replace('_', ' ').title()}
Reference: {payment_reference or 'Processing'}

Your withdrawal is being processed.
Funds will arrive within 24-48 hours.

Reply 'menu' for main menu."""

                await whatsapp_service.send_message(user.phone_number, message)
        except Exception as e:
            logger.error(f"Error sending withdrawal approval notification: {e}")

        return withdrawal

    @staticmethod
    async def reject_withdrawal(
        withdrawal_id: int,
        admin_user_id: int,
        rejection_reason: str,
        db: Session
    ) -> Withdrawal:
        """
        Reject a withdrawal request and refund to wallet

        Args:
            withdrawal_id: Withdrawal ID to reject
            admin_user_id: Admin user ID rejecting
            rejection_reason: Reason for rejection
            db: Database session

        Returns:
            Updated Withdrawal object
        """
        # Get withdrawal with lock
        withdrawal = db.query(Withdrawal).filter(
            Withdrawal.id == withdrawal_id
        ).with_for_update().first()

        if not withdrawal:
            raise ValueError(f"Withdrawal {withdrawal_id} not found")

        if withdrawal.status != WithdrawalStatus.PENDING:
            raise ValueError(f"Withdrawal {withdrawal_id} is not pending (status: {withdrawal.status})")

        # Refund amount to wallet
        refund_transaction = wallet_service.credit(
            user_id=withdrawal.user_id,
            amount=withdrawal.amount,
            transaction_type='refund',
            description=f"Withdrawal #{withdrawal.id} rejected - refund",
            db=db,
            reference_type='withdrawal',
            reference_id=withdrawal.id,
            metadata={'reason': rejection_reason}
        )

        # Update withdrawal status
        withdrawal.status = WithdrawalStatus.REJECTED
        withdrawal.reviewed_by = admin_user_id
        withdrawal.reviewed_at = datetime.utcnow()
        withdrawal.rejection_reason = rejection_reason
        withdrawal.refund_transaction_id = refund_transaction.id

        db.flush()

        logger.info(
            f"Withdrawal rejected: withdrawal_id={withdrawal_id}, "
            f"user_id={withdrawal.user_id}, refunded={withdrawal.amount}"
        )

        # Notify user via WhatsApp
        try:
            from .whatsapp import whatsapp_service
            user = db.query(User).filter(User.id == withdrawal.user_id).first()
            if user:
                message = f"""❌ WITHDRAWAL REJECTED

Amount: R{float(withdrawal.amount):.2f}
Reason: {rejection_reason}

Your funds have been refunded to your wallet.
New Balance: R{float(refund_transaction.balance_after):.2f}

Reply 'menu' for main menu."""

                await whatsapp_service.send_message(user.phone_number, message)
        except Exception as e:
            logger.error(f"Error sending withdrawal rejection notification: {e}")

        return withdrawal

    @staticmethod
    def _get_daily_withdrawal_total(user_id: int, db: Session) -> Decimal:
        """Get total withdrawal amount for user today"""
        from datetime import date
        today_start = datetime.combine(date.today(), datetime.min.time())

        total = db.query(func.sum(Withdrawal.amount)).filter(
            Withdrawal.user_id == user_id,
            Withdrawal.created_at >= today_start,
            Withdrawal.status.in_([WithdrawalStatus.PENDING, WithdrawalStatus.APPROVED])
        ).scalar()

        return total or Decimal('0.00')

    @staticmethod
    def get_pending_withdrawals(db: Session, limit: int = 50) -> List[Withdrawal]:
        """Get all pending withdrawal requests"""
        withdrawals = db.query(Withdrawal).filter(
            Withdrawal.status == WithdrawalStatus.PENDING
        ).order_by(desc(Withdrawal.created_at)).limit(limit).all()

        return withdrawals

    @staticmethod
    def get_user_withdrawals(
        user_id: int,
        db: Session,
        limit: int = 10,
        status: Optional[WithdrawalStatus] = None
    ) -> List[Withdrawal]:
        """Get withdrawal history for a user"""
        query = db.query(Withdrawal).filter(Withdrawal.user_id == user_id)

        if status:
            query = query.filter(Withdrawal.status == status)

        withdrawals = query.order_by(desc(Withdrawal.created_at)).limit(limit).all()

        return withdrawals


# Export singleton instance
withdrawal_service = WithdrawalService()
```

### Step 3: Update Message Router for Withdrawals (1.5 hours)

#### 3.1 Add to app/services/message_router.py

```python
# Add withdrawal imports
from ..models.withdrawal import WithdrawalMethod
from .withdrawal_service import withdrawal_service

# Add withdrawal states
class UserState:
    AWAITING_DEPOSIT_AMOUNT = "awaiting_deposit_amount"
    AWAITING_DEPOSIT_METHOD = "awaiting_deposit_method"
    AWAITING_DEPOSIT_PROOF = "awaiting_deposit_proof"
    AWAITING_WITHDRAWAL_AMOUNT = "awaiting_withdrawal_amount"
    AWAITING_WITHDRAWAL_METHOD = "awaiting_withdrawal_method"
    AWAITING_WITHDRAWAL_DETAILS = "awaiting_withdrawal_details"

# Add withdrawal handlers

async def _start_withdrawal_flow(self, user: User, db: Session) -> str:
    """Start withdrawal flow"""
    # Check minimum balance
    try:
        balance = wallet_service.get_balance(user.id, db)
        if balance < withdrawal_service.MIN_WITHDRAWAL:
            return f"""❌ INSUFFICIENT BALANCE

Your balance: R{float(balance):.2f}
Minimum withdrawal: R{float(withdrawal_service.MIN_WITHDRAWAL):.2f}

Please deposit more funds or play games to win!
Reply 'menu' for main menu."""

        self.user_states[user.id] = {
            'state': UserState.AWAITING_WITHDRAWAL_AMOUNT
        }

        return f"""💸 WITHDRAW MONEY

Your balance: R{float(balance):.2f}

Minimum: R{float(withdrawal_service.MIN_WITHDRAWAL):.2f}
Maximum: R{float(withdrawal_service.MAX_WITHDRAWAL):.2f}

How much would you like to withdraw?
Example: 100 (for R100)

Reply 'cancel' to go back."""

    except Exception as e:
        logger.error(f"Error starting withdrawal flow: {e}")
        return "❌ Error checking balance. Please try again later."

async def _handle_withdrawal_amount(
    self,
    user: User,
    message: str,
    state: Dict[str, Any],
    db: Session
) -> str:
    """Handle withdrawal amount input"""
    try:
        amount = Decimal(message.strip())

        # Validate amount
        if amount < withdrawal_service.MIN_WITHDRAWAL:
            return f"❌ Minimum withdrawal is R{float(withdrawal_service.MIN_WITHDRAWAL):.2f}. Please enter a valid amount:"

        if amount > withdrawal_service.MAX_WITHDRAWAL:
            return f"❌ Maximum withdrawal is R{float(withdrawal_service.MAX_WITHDRAWAL):.2f}. Please enter a valid amount:"

        # Check balance
        balance = wallet_service.get_balance(user.id, db)
        if amount > balance:
            return f"❌ Insufficient balance. You have R{float(balance):.2f}. Please enter a valid amount:"

        # Store amount
        state['amount'] = amount
        state['state'] = UserState.AWAITING_WITHDRAWAL_METHOD

        return f"""💳 WITHDRAWAL METHOD

Amount: R{float(amount):.2f}

Choose withdrawal method:

1️⃣ Bank Transfer (2-3 days)
2️⃣ Cash Pickup (24 hours)
3️⃣ eWallet (Instant)

Reply with the number (1-3)"""

    except (ValueError, InvalidOperation):
        return "❌ Invalid amount. Please enter a number (e.g., 100):"

async def _handle_withdrawal_method(
    self,
    user: User,
    message: str,
    state: Dict[str, Any],
    db: Session
) -> str:
    """Handle withdrawal method selection"""
    method_map = {
        '1': (WithdrawalMethod.BANK_TRANSFER, "Bank Transfer"),
        '2': (WithdrawalMethod.CASH_PICKUP, "Cash Pickup"),
        '3': (WithdrawalMethod.EWALLET, "eWallet"),
    }

    method_info = method_map.get(message.strip())

    if not method_info:
        return "❌ Invalid choice. Please reply with a number (1-3):"

    withdrawal_method, method_name = method_info

    state['withdrawal_method'] = withdrawal_method
    state['method_name'] = method_name
    state['state'] = UserState.AWAITING_WITHDRAWAL_DETAILS

    if withdrawal_method == WithdrawalMethod.BANK_TRANSFER:
        return """🏦 BANK DETAILS

Please provide your bank details in this format:

Bank Name
Account Number
Account Holder Name

Example:
FNB
1234567890
John Doe"""

    elif withdrawal_method == WithdrawalMethod.CASH_PICKUP:
        return """📍 PICKUP LOCATION

Cash pickup locations:
- Johannesburg CBD
- Pretoria Central
- Cape Town City Center

Which location is convenient for you?"""

    else:  # eWallet
        return """📱 EWALLET DETAILS

Please provide your cellphone number for eWallet:

Example: 0821234567"""

async def _handle_withdrawal_details(
    self,
    user: User,
    message: str,
    state: Dict[str, Any],
    db: Session
) -> str:
    """Handle withdrawal details submission"""
    amount = state['amount']
    withdrawal_method = state['withdrawal_method']
    method_name = state['method_name']

    # Parse details based on method
    try:
        if withdrawal_method == WithdrawalMethod.BANK_TRANSFER:
            lines = [line.strip() for line in message.strip().split('\n') if line.strip()]
            if len(lines) < 3:
                return "❌ Please provide all bank details (Bank, Account Number, Account Holder):"

            bank_name = lines[0]
            account_number = lines[1]
            account_holder = lines[2]
        else:
            bank_name = None
            account_number = message.strip()
            account_holder = None

        # Create withdrawal request
        withdrawal = withdrawal_service.create_withdrawal_request(
            user_id=user.id,
            amount=amount,
            withdrawal_method=withdrawal_method,
            bank_name=bank_name,
            account_number=account_number,
            account_holder=account_holder,
            notes=f"Submitted via WhatsApp",
            db=db
        )

        db.commit()

        # Clear state
        self.user_states.pop(user.id, None)

        # Get new balance
        new_balance = wallet_service.get_balance(user.id, db)

        return f"""✅ WITHDRAWAL REQUEST SUBMITTED

Withdrawal ID: #{withdrawal.id}
Amount: R{float(amount):.2f}
Method: {method_name}
New Balance: R{float(new_balance):.2f}

Your request is being reviewed.
Processing time: 24-48 hours

You'll receive a notification once approved.

Reply 'menu' for main menu."""

    except ValueError as e:
        self.user_states.pop(user.id, None)
        return f"""❌ {str(e)}

Reply 'menu' for main menu."""
    except Exception as e:
        logger.error(f"Error creating withdrawal request: {e}")
        self.user_states.pop(user.id, None)
        return f"""❌ Error submitting withdrawal request.

Please try again or contact support.

Reply 'menu' for main menu."""
```

### Step 4: Create Pydantic Schemas (30 minutes)

#### 4.1 Create app/schemas/withdrawal.py

```python
from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import datetime
from typing import Optional
from ..models.withdrawal import WithdrawalStatus, WithdrawalMethod


class WithdrawalCreate(BaseModel):
    amount: Decimal = Field(..., gt=0)
    withdrawal_method: WithdrawalMethod
    bank_name: Optional[str] = None
    account_number: Optional[str] = None
    account_holder: Optional[str] = None
    notes: Optional[str] = None


class WithdrawalResponse(BaseModel):
    id: int
    user_id: int
    amount: Decimal
    withdrawal_method: WithdrawalMethod
    status: WithdrawalStatus
    bank_name: Optional[str]
    account_number: Optional[str]
    created_at: datetime
    reviewed_at: Optional[datetime]
    rejection_reason: Optional[str]
    payment_reference: Optional[str]

    class Config:
        from_attributes = True


class WithdrawalApproval(BaseModel):
    withdrawal_id: int
    admin_user_id: int
    payment_reference: Optional[str] = None


class WithdrawalRejection(BaseModel):
    withdrawal_id: int
    admin_user_id: int
    rejection_reason: str = Field(..., min_length=10, max_length=200)
```

### Day 3 Deliverables

By end of Day 3, you should have:

- [x] Withdrawal model created
- [x] Withdrawal service with create/approve/reject operations
- [x] Immediate wallet debiting on request
- [x] Wallet refund on rejection
- [x] WhatsApp withdrawal flow integrated
- [x] Balance and limit validation
- [x] User notifications
- [x] Pydantic schemas

### Day 3 Checklist

- [ ] Withdrawal model created
- [ ] Withdrawal status enum defined
- [ ] Withdrawal method enum defined
- [ ] Withdrawal service implements create operation
- [ ] Withdrawal service implements approve operation
- [ ] Withdrawal service implements reject operation
- [ ] Wallet is debited on request creation
- [ ] Wallet is refunded on rejection
- [ ] Balance validation works
- [ ] Daily withdrawal limits enforced
- [ ] WhatsApp withdrawal flow works
- [ ] User receives notifications
- [ ] Pydantic schemas created

### Common Issues & Solutions

**Issue:** Withdrawal created but wallet not debited
- **Solution:** Ensure debit happens in same transaction as withdrawal creation

**Issue:** Rejected withdrawal not refunded
- **Solution:** Check that refund transaction is created and committed

**Issue:** Daily limit not enforced
- **Solution:** Verify `_get_daily_withdrawal_total` queries correct date range

---
## Day 4: Admin Models & Basic API Endpoints

**Duration:** 3-5 hours
**Goal:** Create admin user model, authentication, and API endpoints for deposit/withdrawal approval

### Prerequisites

- Days 1-3 completed
- Deposit and withdrawal services working

### Step 1: Create Admin User Model (45 minutes)

#### 1.1 Create app/models/admin.py

```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum
from ..database import Base


class AdminRole(str, enum.Enum):
    """Admin user roles"""
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    SUPPORT = "support"


class AdminUser(Base):
    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True, index=True)
    
    # Authentication
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(200), nullable=False)
    
    # Profile
    full_name = Column(String(100), nullable=False)
    role = Column(SQLEnum(AdminRole), default=AdminRole.SUPPORT, nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<AdminUser(id={self.id}, email={self.email}, role={self.role})>"
```

### Step 2: Create Authentication Utilities (1 hour)

#### 2.1 Update app/utils/security.py

```python
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from ..config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None
```

### Step 3: Create Admin API Endpoints (2 hours)

#### 3.1 Create app/api/deps.py

```python
from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.admin import AdminUser
from ..utils.security import verify_token

security = HTTPBearer()


def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> AdminUser:
    """Get current authenticated admin user"""
    token = credentials.credentials
    payload = verify_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    admin_id = payload.get("sub")
    if not admin_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    admin = db.query(AdminUser).filter(AdminUser.id == int(admin_id)).first()
    
    if not admin or not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin user not found or inactive"
        )
    
    return admin
```

#### 3.2 Create app/api/admin.py

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import timedelta

from ..database import get_db
from ..models.admin import AdminUser
from ..schemas.deposit import DepositResponse, DepositApproval, DepositRejection
from ..schemas.withdrawal import WithdrawalResponse, WithdrawalApproval, WithdrawalRejection
from ..services.deposit_service import deposit_service
from ..services.withdrawal_service import withdrawal_service
from ..utils.security import verify_password, create_access_token
from .deps import get_current_admin
from pydantic import BaseModel

router = APIRouter(prefix="/admin", tags=["admin"])


class AdminLogin(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post("/login", response_model=TokenResponse)
def admin_login(login: AdminLogin, db: Session = Depends(get_db)):
    """Admin login endpoint"""
    admin = db.query(AdminUser).filter(AdminUser.email == login.email).first()
    
    if not admin or not verify_password(login.password, admin.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin account is inactive"
        )
    
    # Create access token
    access_token = create_access_token(
        data={"sub": str(admin.id), "role": admin.role.value},
        expires_delta=timedelta(hours=24)
    )
    
    # Update last login
    from datetime import datetime
    admin.last_login = datetime.utcnow()
    db.commit()
    
    return {"access_token": access_token}


@router.get("/deposits/pending", response_model=List[DepositResponse])
def get_pending_deposits(
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get all pending deposit requests"""
    deposits = deposit_service.get_pending_deposits(db, limit=100)
    return deposits


@router.post("/deposits/approve")
async def approve_deposit(
    approval: DepositApproval,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Approve a deposit request"""
    try:
        deposit = await deposit_service.approve_deposit(
            deposit_id=approval.deposit_id,
            admin_user_id=current_admin.id,
            db=db
        )
        db.commit()
        return {"message": "Deposit approved successfully", "deposit_id": deposit.id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/deposits/reject")
async def reject_deposit(
    rejection: DepositRejection,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Reject a deposit request"""
    try:
        deposit = await deposit_service.reject_deposit(
            deposit_id=rejection.deposit_id,
            admin_user_id=current_admin.id,
            rejection_reason=rejection.rejection_reason,
            db=db
        )
        db.commit()
        return {"message": "Deposit rejected successfully", "deposit_id": deposit.id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/withdrawals/pending", response_model=List[WithdrawalResponse])
def get_pending_withdrawals(
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get all pending withdrawal requests"""
    withdrawals = withdrawal_service.get_pending_withdrawals(db, limit=100)
    return withdrawals


@router.post("/withdrawals/approve")
async def approve_withdrawal(
    approval: WithdrawalApproval,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Approve a withdrawal request"""
    try:
        withdrawal = await withdrawal_service.approve_withdrawal(
            withdrawal_id=approval.withdrawal_id,
            admin_user_id=current_admin.id,
            payment_reference=approval.payment_reference,
            db=db
        )
        db.commit()
        return {"message": "Withdrawal approved successfully", "withdrawal_id": withdrawal.id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/withdrawals/reject")
async def reject_withdrawal(
    rejection: WithdrawalRejection,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Reject a withdrawal request"""
    try:
        withdrawal = await withdrawal_service.reject_withdrawal(
            withdrawal_id=rejection.withdrawal_id,
            admin_user_id=current_admin.id,
            rejection_reason=rejection.rejection_reason,
            db=db
        )
        db.commit()
        return {"message": "Withdrawal rejected successfully", "withdrawal_id": withdrawal.id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

#### 3.3 Update app/main.py

```python
# Add admin router
from .api import webhook, admin

# Include routers
app.include_router(webhook.router, prefix="/api", tags=["webhook"])
app.include_router(admin.router, prefix="/api", tags=["admin"])
```

### Step 4: Create Initial Admin User Script (30 minutes)

#### 4.1 Create scripts/create_admin.py

```python
"""Script to create initial admin user"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.database import SessionLocal
from app.models.admin import AdminUser, AdminRole
from app.utils.security import get_password_hash


def create_admin_user(email: str, password: str, full_name: str, role: AdminRole = AdminRole.ADMIN):
    """Create a new admin user"""
    db = SessionLocal()
    
    try:
        # Check if user already exists
        existing = db.query(AdminUser).filter(AdminUser.email == email).first()
        if existing:
            print(f"❌ Admin user with email {email} already exists")
            return
        
        # Create new admin user
        admin = AdminUser(
            email=email,
            hashed_password=get_password_hash(password),
            full_name=full_name,
            role=role,
            is_active=True
        )
        
        db.add(admin)
        db.commit()
        db.refresh(admin)
        
        print(f"✅ Admin user created successfully")
        print(f"   Email: {email}")
        print(f"   Name: {full_name}")
        print(f"   Role: {role.value}")
        print(f"   ID: {admin.id}")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating admin user: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("Creating initial admin user...")
    create_admin_user(
        email="admin@mykasibets.com",
        password="ChangeThisPassword123!",  # Change this!
        full_name="Super Admin",
        role=AdminRole.SUPER_ADMIN
    )
```

Run with:
```bash
python scripts/create_admin.py
```

### Day 4 Deliverables

By end of Day 4, you should have:

- [x] Admin user model created
- [x] Admin authentication with JWT
- [x] Admin login endpoint
- [x] Deposit approval/rejection endpoints
- [x] Withdrawal approval/rejection endpoints
- [x] Admin user creation script
- [x] Authentication middleware

### Day 4 Checklist

- [ ] Admin model created
- [ ] Admin role enum defined
- [ ] Password hashing utilities work
- [ ] JWT token creation works
- [ ] Admin login endpoint works
- [ ] Deposit approval endpoint works
- [ ] Deposit rejection endpoint works
- [ ] Withdrawal approval endpoint works
- [ ] Withdrawal rejection endpoint works
- [ ] Authentication middleware protects endpoints
- [ ] Initial admin user created

---

## Day 5: Testing & Integration

**Duration:** 4-6 hours
**Goal:** Comprehensive testing of all Phase 2 components and end-to-end flows

### Step 1: Integration Tests (2 hours)

#### 1.1 Create tests/test_deposit_flow.py

```python
import pytest
from decimal import Decimal
from app.models.deposit import DepositStatus, PaymentMethod
from app.services.deposit_service import deposit_service
from app.services.wallet_service import wallet_service


@pytest.mark.asyncio
async def test_deposit_approval_flow(db, test_user, test_admin):
    """Test complete deposit approval flow"""
    # Create deposit request
    deposit = deposit_service.create_deposit_request(
        user_id=test_user.id,
        amount=Decimal('100.00'),
        payment_method=PaymentMethod.BANK_TRANSFER,
        proof_type='reference',
        proof_value='REF123',
        notes='Test deposit',
        db=db
    )
    db.commit()
    
    assert deposit.status == DepositStatus.PENDING
    
    # Get initial balance
    initial_balance = wallet_service.get_balance(test_user.id, db)
    
    # Approve deposit
    approved = await deposit_service.approve_deposit(
        deposit_id=deposit.id,
        admin_user_id=test_admin.id,
        db=db
    )
    db.commit()
    
    assert approved.status == DepositStatus.APPROVED
    assert approved.transaction_id is not None
    
    # Check balance increased
    new_balance = wallet_service.get_balance(test_user.id, db)
    assert new_balance == initial_balance + Decimal('100.00')


@pytest.mark.asyncio
async def test_deposit_rejection_flow(db, test_user, test_admin):
    """Test deposit rejection flow"""
    deposit = deposit_service.create_deposit_request(
        user_id=test_user.id,
        amount=Decimal('50.00'),
        payment_method=PaymentMethod.SNAPSCAN,
        proof_type='reference',
        proof_value='SNAP456',
        notes='Test',
        db=db
    )
    db.commit()
    
    initial_balance = wallet_service.get_balance(test_user.id, db)
    
    # Reject deposit
    rejected = await deposit_service.reject_deposit(
        deposit_id=deposit.id,
        admin_user_id=test_admin.id,
        rejection_reason="Invalid proof of payment",
        db=db
    )
    db.commit()
    
    assert rejected.status == DepositStatus.REJECTED
    
    # Balance should not change
    final_balance = wallet_service.get_balance(test_user.id, db)
    assert final_balance == initial_balance
```

#### 1.2 Create tests/test_withdrawal_flow.py

```python
import pytest
from decimal import Decimal
from app.models.withdrawal import WithdrawalStatus, WithdrawalMethod
from app.services.withdrawal_service import withdrawal_service
from app.services.wallet_service import wallet_service


@pytest.mark.asyncio
async def test_withdrawal_approval_flow(db, test_user_with_balance, test_admin):
    """Test complete withdrawal approval flow"""
    initial_balance = wallet_service.get_balance(test_user_with_balance.id, db)
    
    # Create withdrawal request
    withdrawal = withdrawal_service.create_withdrawal_request(
        user_id=test_user_with_balance.id,
        amount=Decimal('100.00'),
        withdrawal_method=WithdrawalMethod.BANK_TRANSFER,
        bank_name="FNB",
        account_number="1234567890",
        account_holder="Test User",
        notes="Test withdrawal",
        db=db
    )
    db.commit()
    
    assert withdrawal.status == WithdrawalStatus.PENDING
    
    # Balance should be debited immediately
    after_request_balance = wallet_service.get_balance(test_user_with_balance.id, db)
    assert after_request_balance == initial_balance - Decimal('100.00')
    
    # Approve withdrawal
    approved = await withdrawal_service.approve_withdrawal(
        withdrawal_id=withdrawal.id,
        admin_user_id=test_admin.id,
        payment_reference="PAY123",
        db=db
    )
    db.commit()
    
    assert approved.status == WithdrawalStatus.APPROVED
    assert approved.payment_reference == "PAY123"
    
    # Balance should remain the same (already debited)
    final_balance = wallet_service.get_balance(test_user_with_balance.id, db)
    assert final_balance == after_request_balance


@pytest.mark.asyncio
async def test_withdrawal_rejection_refund(db, test_user_with_balance, test_admin):
    """Test withdrawal rejection refunds to wallet"""
    initial_balance = wallet_service.get_balance(test_user_with_balance.id, db)
    
    withdrawal = withdrawal_service.create_withdrawal_request(
        user_id=test_user_with_balance.id,
        amount=Decimal('50.00'),
        withdrawal_method=WithdrawalMethod.EWALLET,
        bank_name=None,
        account_number="0821234567",
        account_holder=None,
        notes="Test",
        db=db
    )
    db.commit()
    
    # Reject withdrawal
    rejected = await withdrawal_service.reject_withdrawal(
        withdrawal_id=withdrawal.id,
        admin_user_id=test_admin.id,
        rejection_reason="Invalid account details",
        db=db
    )
    db.commit()
    
    assert rejected.status == WithdrawalStatus.REJECTED
    assert rejected.refund_transaction_id is not None
    
    # Balance should be refunded
    final_balance = wallet_service.get_balance(test_user_with_balance.id, db)
    assert final_balance == initial_balance
```

### Step 2: End-to-End Testing (1.5 hours)

Test these scenarios manually or with integration tests:

1. **Complete Deposit Flow**
   - User submits deposit via WhatsApp
   - Admin approves via API
   - User receives WhatsApp notification
   - Wallet is credited
   - Transaction logged

2. **Complete Withdrawal Flow**
   - User requests withdrawal via WhatsApp
   - Wallet debited immediately
   - Admin approves via API
   - User receives notification

3. **Edge Cases**
   - Insufficient balance for withdrawal
   - Daily withdrawal limit exceeded
   - Double approval attempts
   - Invalid amounts

### Step 3: Database Migrations (1 hour)

#### 3.1 Initialize Alembic (if not done)

```bash
alembic init alembic
```

#### 3.2 Create Migration

```bash
alembic revision --autogenerate -m "Add deposit, withdrawal, and admin models"
```

#### 3.3 Run Migration

```bash
alembic upgrade head
```

### Step 4: Documentation Updates (30 minutes)

Create/update:
- API documentation (automatically via FastAPI /docs)
- Admin user guide
- Testing documentation
- Deployment checklist

### Day 5 Deliverables

By end of Day 5, you should have:

- [x] Integration tests for deposit flow
- [x] Integration tests for withdrawal flow
- [x] End-to-end testing completed
- [x] Database migrations created
- [x] All Phase 2 functionality tested
- [x] Documentation updated

### Day 5 Checklist

- [ ] Deposit approval flow tested
- [ ] Deposit rejection flow tested
- [ ] Withdrawal approval flow tested
- [ ] Withdrawal rejection flow tested
- [ ] Balance integrity verified
- [ ] Transaction logging verified
- [ ] WhatsApp notifications tested
- [ ] Admin API endpoints tested
- [ ] Database migrations working
- [ ] All edge cases handled

---

## Deliverables Checklist

### Core Functionality

- [ ] Wallet service with credit/debit operations
- [ ] Complete transaction logging
- [ ] Deposit request system
- [ ] Deposit approval/rejection workflow
- [ ] Withdrawal request system
- [ ] Withdrawal approval/rejection workflow
- [ ] Admin authentication
- [ ] Admin API endpoints

### Database

- [ ] Transaction model
- [ ] Deposit model
- [ ] Withdrawal model
- [ ] Admin user model
- [ ] All relationships configured
- [ ] Indexes created
- [ ] Migrations created

### Services

- [ ] WalletService
- [ ] DepositService
- [ ] WithdrawalService
- [ ] Admin authentication utilities

### WhatsApp Integration

- [ ] Deposit flow via WhatsApp
- [ ] Withdrawal flow via WhatsApp
- [ ] User notifications for approvals
- [ ] User notifications for rejections
- [ ] State management working

### Testing

- [ ] Unit tests for wallet service
- [ ] Integration tests for deposits
- [ ] Integration tests for withdrawals
- [ ] End-to-end flow tests
- [ ] Edge case tests

---

## Testing Strategy

### Unit Testing

Test individual components:
- Wallet service credit/debit operations
- Transaction creation and logging
- Balance validation
- Amount validation
- Limit enforcement

### Integration Testing

Test component interactions:
- Deposit approval credits wallet and creates transaction
- Withdrawal rejection refunds wallet
- Admin authentication and authorization
- Database transaction atomicity

### End-to-End Testing

Test complete user flows:
- User deposits money via WhatsApp → Admin approves → Wallet credited
- User withdraws money via WhatsApp → Admin approves → Withdrawal processed
- User withdrawal rejected → Funds refunded

### Performance Testing

- Concurrent wallet operations
- Race condition prevention
- Database query performance
- API response times

---

## Troubleshooting Guide

### Wallet Issues

**Issue:** Balance mismatch after transactions
- **Check:** Transaction logs match wallet balance
- **Solution:** Run `verify_balance_integrity` for affected users

**Issue:** Negative balance created
- **Check:** Balance validation in debit operation
- **Solution:** Fix validation and add database constraint

**Issue:** Race condition in concurrent operations
- **Check:** Row-level locking is applied (`with_for_update`)
- **Solution:** Ensure all wallet operations use locking

### Deposit Issues

**Issue:** Deposit approved but wallet not credited
- **Check:** Transaction committed within same database session
- **Solution:** Verify commit happens after both operations

**Issue:** Duplicate deposit approval
- **Check:** Status validation before approval
- **Solution:** Add optimistic locking on deposit status

**Issue:** WhatsApp notification fails
- **Check:** User exists and has valid phone number
- **Solution:** Log error but don't fail approval

### Withdrawal Issues

**Issue:** Withdrawal created without debiting wallet
- **Check:** Debit operation in same transaction
- **Solution:** Wrap in database transaction

**Issue:** Rejected withdrawal not refunded
- **Check:** Refund transaction created
- **Solution:** Verify refund in rejection handler

**Issue:** Daily limit bypass
- **Check:** `_get_daily_withdrawal_total` calculation
- **Solution:** Fix date range query

### Admin API Issues

**Issue:** JWT token expired
- **Check:** Token expiration time
- **Solution:** Refresh token or re-login

**Issue:** Unauthorized access
- **Check:** Token validity and admin status
- **Solution:** Verify token and admin.is_active

**Issue:** Admin can't approve/reject
- **Check:** Admin role permissions
- **Solution:** Verify role-based access control

---

## Next Steps

After completing Phase 2, proceed to:

### Phase 3: Games Implementation (Week 3-4)
- Lucky Wheel game engine
- Color Game implementation
- Pick 3 Numbers game
- Football Yes/No betting
- Game result generation
- Bet settlement logic

### Phase 4: Admin Dashboard (Week 4-5)
- React dashboard frontend
- User management interface
- Deposit/withdrawal approval UI
- Bet management and settlement
- Analytics and reporting
- Real-time updates

### Phase 5: Testing & Launch (Week 5-6)
- Comprehensive testing
- Beta user onboarding
- Performance optimization
- Security audit
- Production deployment
- Monitoring setup

### Enhancements for Future Phases
- Automated deposit verification (payment gateway integration)
- Automated withdrawal processing
- Push notifications
- Transaction export/reporting
- Fraud detection
- KYC verification
- Multi-currency support

---

**End of Phase 2 Implementation Plan**

**Document Version:** 1.0
**Last Updated:** January 2026
**Status:** Ready for Implementation

For questions or issues during implementation, refer to:
- Phase 1 Implementation Plan
- Python Implementation Guide
- WhatsApp Business API Documentation
- FastAPI Documentation
