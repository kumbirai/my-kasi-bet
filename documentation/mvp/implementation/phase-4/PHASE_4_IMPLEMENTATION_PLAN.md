# PHASE 4 IMPLEMENTATION PLAN: Admin Dashboard & Management Interface

**MyKasiBets WhatsApp Betting Platform MVP**
**Phase 4: Week 4-5 (10 Days)**
**Version:** 1.0
**Last Updated:** 2026-01-01

---

## EXECUTIVE SUMMARY

Phase 4 focuses on building a comprehensive **React Admin Dashboard** with a supporting **FastAPI Admin API** to manage the entire MyKasiBets platform. This phase delivers the management interface that admins need to:

- Monitor and manage users
- Approve/reject deposit and withdrawal requests
- Monitor bets and gaming activity
- Create and settle football matches
- View financial reports and analytics
- Block/unblock users
- View real-time platform statistics

By the end of Phase 4, administrators will have a modern, responsive web interface to manage all platform operations without needing database access or command-line tools.

### What This Phase Delivers

1. **Admin API Backend** (FastAPI)
   - JWT authentication for admin users
   - Protected admin endpoints with role-based access
   - User management API
   - Deposit/withdrawal approval API
   - Bet monitoring API
   - Match management API (Football)
   - Analytics and reporting API

2. **React Admin Dashboard** (Frontend)
   - Modern React 18 application with Vite
   - Tailwind CSS for styling
   - Authentication with JWT token management
   - User management interface
   - Deposit approval workflow UI
   - Withdrawal approval workflow UI
   - Bet monitoring dashboard
   - Match creation and settlement UI
   - Financial reports and analytics
   - Real-time updates

3. **Security & Performance**
   - Role-based access control (RBAC)
   - Secure JWT token handling
   - API rate limiting
   - Input validation and sanitization
   - Optimized database queries
   - Caching for analytics

### Success Metrics

- ✅ Admin can log in securely via web interface
- ✅ All deposit requests visible and approvable
- ✅ All withdrawal requests visible and approvable
- ✅ Complete user list with search and filtering
- ✅ Real-time bet monitoring dashboard
- ✅ Football match creation and settlement workflow
- ✅ Financial reports showing revenue, payouts, balances
- ✅ Block/unblock users functionality
- ✅ Dashboard loads in <2 seconds
- ✅ All admin actions logged for audit trail

---

## PHASE OBJECTIVES

### Primary Objectives

1. **Build Secure Admin API**
   - Implement JWT authentication for admin users
   - Create protected API endpoints for all admin operations
   - Add role-based access control (superadmin, admin, support)
   - Implement audit logging for all admin actions

2. **Create User Management Interface**
   - List all users with pagination
   - Search and filter users
   - View user details (wallet, bets, transactions)
   - Block/unblock users
   - View user activity timeline

3. **Implement Deposit/Withdrawal Management**
   - View pending requests in real-time
   - Display proof of payment for deposits
   - Approve/reject with reason and notes
   - Track approval history
   - Filter by status, payment method, date

4. **Build Bet Monitoring Dashboard**
   - View active bets across all games
   - View settled bets history
   - Filter by game type, user, date, status
   - Display win/loss statistics
   - Export bet data

5. **Create Match Management System**
   - Create football matches with teams and odds
   - Mark matches as in-progress or settled
   - Set results (Yes/No outcome)
   - View match betting statistics
   - Manage match schedules

6. **Develop Analytics & Reporting**
   - Total deposits, withdrawals, revenue
   - Platform balance and liabilities
   - Game-specific statistics
   - User engagement metrics
   - Export financial reports

### Secondary Objectives

1. **Real-time Updates**
   - Polling or WebSocket for live data
   - Notifications for new requests
   - Live bet updates

2. **Responsive Design**
   - Mobile-friendly admin interface
   - Tablet optimization
   - Accessible UI components

3. **Performance Optimization**
   - Lazy loading for large datasets
   - Query optimization with indexes
   - Caching for analytics endpoints
   - Efficient pagination

---

## SUCCESS CRITERIA

### Functional Requirements

**Admin Authentication:**
- [ ] Admin can register (superadmin only creates other admins)
- [ ] Admin can log in with email/password
- [ ] JWT tokens issued with 24-hour expiry
- [ ] Refresh token mechanism implemented
- [ ] Role-based access control working

**User Management:**
- [ ] List all users with pagination (50 per page)
- [ ] Search users by phone number or name
- [ ] Filter users by status (active, blocked)
- [ ] View user profile with wallet balance
- [ ] View user transaction history
- [ ] View user bet history
- [ ] Block/unblock users
- [ ] Blocked users cannot place bets

**Deposit Management:**
- [ ] View all pending deposits
- [ ] Display deposit details (amount, method, timestamp)
- [ ] View proof of payment metadata
- [ ] Approve deposit (credits wallet)
- [ ] Reject deposit with reason
- [ ] Filter deposits by status, method, date
- [ ] WhatsApp notification sent on approval/rejection

**Withdrawal Management:**
- [ ] View all pending withdrawals
- [ ] Display withdrawal details (amount, bank info)
- [ ] Approve withdrawal (debits wallet)
- [ ] Reject withdrawal with reason
- [ ] Filter withdrawals by status, date
- [ ] WhatsApp notification sent on approval/rejection

**Bet Monitoring:**
- [ ] View active bets across all games
- [ ] View settled bets history
- [ ] Filter by game type, user, date, status
- [ ] Display bet details (stake, selection, payout)
- [ ] Win/loss statistics per game
- [ ] Export bet data to CSV

**Match Management:**
- [ ] Create football match (team A vs team B)
- [ ] Set Yes/No odds for each match
- [ ] Mark match as in-progress
- [ ] Settle match with result (Yes/No)
- [ ] View bets on each match
- [ ] Cancel unsettled matches

**Analytics & Reporting:**
- [ ] Total deposits and withdrawals
- [ ] Platform revenue (deposits - withdrawals - payouts)
- [ ] Current platform balance
- [ ] Game-specific revenue
- [ ] User engagement metrics
- [ ] Date range filters
- [ ] Export reports to CSV/PDF

### Technical Requirements

**Backend (FastAPI):**
- [ ] JWT authentication middleware
- [ ] Admin user model with password hashing
- [ ] Protected admin API routes
- [ ] Role-based permission decorators
- [ ] Admin action audit log model
- [ ] Optimized queries with SQLAlchemy
- [ ] Pagination helpers
- [ ] Input validation with Pydantic
- [ ] Error handling for all endpoints

**Frontend (React):**
- [ ] React 18 with Vite build tool
- [ ] Tailwind CSS for styling
- [ ] React Router for navigation
- [ ] JWT token storage (localStorage/sessionStorage)
- [ ] Protected routes with auth guards
- [ ] Reusable UI components
- [ ] Form validation with react-hook-form
- [ ] Data tables with sorting and filtering
- [ ] Loading states and error boundaries
- [ ] Responsive design (mobile, tablet, desktop)

**Security:**
- [ ] Password hashing with bcrypt
- [ ] JWT tokens with short expiry
- [ ] HTTPS only in production
- [ ] CORS configuration
- [ ] Rate limiting on admin API
- [ ] Input sanitization
- [ ] SQL injection prevention
- [ ] XSS prevention

**Performance:**
- [ ] Database indexes on frequently queried fields
- [ ] Query result caching for analytics
- [ ] Lazy loading for large lists
- [ ] Optimistic UI updates
- [ ] Debounced search inputs
- [ ] Code splitting for faster load times

### Testing Requirements

**Backend Tests:**
- [ ] Unit tests for admin service methods
- [ ] Integration tests for admin API endpoints
- [ ] Authentication and authorization tests
- [ ] Permission tests for different roles
- [ ] Edge cases (invalid tokens, expired tokens)

**Frontend Tests:**
- [ ] Component unit tests
- [ ] Integration tests for key workflows
- [ ] Auth flow tests
- [ ] Form validation tests
- [ ] API integration tests

**End-to-End Tests:**
- [ ] Admin login flow
- [ ] Deposit approval workflow
- [ ] Withdrawal approval workflow
- [ ] Match creation and settlement
- [ ] User blocking/unblocking

---

## PREREQUISITES

Before starting Phase 4, ensure these are completed:

### From Phase 3 (Games Implementation)
- [ ] All 4 games fully functional (Lucky Wheel, Color, Pick 3, Football)
- [ ] Bet model and betting service working
- [ ] Game results properly calculated and settled
- [ ] Wallet credits/debits working correctly

### From Phase 2 (Core Systems)
- [ ] Deposit model and service implemented
- [ ] Withdrawal model and service implemented
- [ ] Transaction logging working
- [ ] Wallet service with atomic operations

### From Phase 1 (Foundation)
- [ ] User model with phone_number field
- [ ] PostgreSQL database configured
- [ ] FastAPI server running
- [ ] Basic API structure in place

### Development Environment
- [ ] Node.js 18+ installed
- [ ] npm or yarn installed
- [ ] React development tools installed
- [ ] Vite CLI installed globally
- [ ] Python 3.10+ running
- [ ] FastAPI development server working

### Database
- [ ] PostgreSQL accessible
- [ ] All Phase 1-3 tables created
- [ ] Sample data for testing available

---

## DAY-BY-DAY IMPLEMENTATION BREAKDOWN

### **DAY 1: Admin Backend Setup (6-8 hours)**

**Goal:** Create admin user model, authentication system, and JWT token handling.

#### Step 1: Create Admin User Model (1 hour)

Create `app/models/admin_user.py`:

```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.sql import func
from app.database import Base
import enum

class AdminRole(enum.Enum):
    SUPERADMIN = "superadmin"  # Full access, can create other admins
    ADMIN = "admin"            # Most operations, cannot create admins
    SUPPORT = "support"        # View-only, can approve deposits/withdrawals

class AdminUser(Base):
    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(Enum(AdminRole), nullable=False, default=AdminRole.SUPPORT)
    is_active = Column(Boolean, default=True, nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<AdminUser(email={self.email}, role={self.role})>"
```

Create `app/models/admin_action_log.py`:

```python
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from app.database import Base

class AdminActionLog(Base):
    __tablename__ = "admin_action_logs"

    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, ForeignKey("admin_users.id"), nullable=False, index=True)
    action_type = Column(String, nullable=False, index=True)  # "approve_deposit", "reject_withdrawal", etc.
    entity_type = Column(String, nullable=False)  # "deposit", "withdrawal", "user", "bet", "match"
    entity_id = Column(Integer, nullable=False)
    details = Column(Text, nullable=True)  # JSON string with additional context
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self):
        return f"<AdminActionLog(admin_id={self.admin_id}, action={self.action_type})>"
```

Run migration:
```bash
# Create migration
alembic revision --autogenerate -m "Add admin user and action log models"

# Apply migration
alembic upgrade head
```

#### Step 2: Create Admin Schemas (30 minutes)

Create `app/schemas/admin.py`:

```python
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional
from app.models.admin_user import AdminRole

class AdminUserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=2)
    role: AdminRole = AdminRole.SUPPORT

class AdminUserLogin(BaseModel):
    email: EmailStr
    password: str

class AdminUserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    role: AdminRole
    is_active: bool
    last_login: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 86400  # 24 hours in seconds

class AdminActionLogCreate(BaseModel):
    action_type: str
    entity_type: str
    entity_id: int
    details: Optional[str] = None
```

#### Step 3: Implement Admin Service (2 hours)

Create `app/services/admin_service.py`:

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from app.models.admin_user import AdminUser, AdminRole
from app.models.admin_action_log import AdminActionLog
from app.schemas.admin import AdminUserCreate, AdminUserLogin
import os

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

class AdminService:

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt."""
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    async def create_admin_user(db: AsyncSession, admin_data: AdminUserCreate) -> AdminUser:
        """Create a new admin user."""
        hashed_password = AdminService.hash_password(admin_data.password)

        admin_user = AdminUser(
            email=admin_data.email,
            hashed_password=hashed_password,
            full_name=admin_data.full_name,
            role=admin_data.role,
            is_active=True
        )

        db.add(admin_user)
        await db.commit()
        await db.refresh(admin_user)

        return admin_user

    @staticmethod
    async def authenticate_admin(db: AsyncSession, login_data: AdminUserLogin) -> Optional[AdminUser]:
        """Authenticate an admin user."""
        result = await db.execute(
            select(AdminUser).where(AdminUser.email == login_data.email)
        )
        admin_user = result.scalar_one_or_none()

        if not admin_user:
            return None

        if not AdminService.verify_password(login_data.password, admin_user.hashed_password):
            return None

        if not admin_user.is_active:
            return None

        # Update last login
        admin_user.last_login = datetime.utcnow()
        await db.commit()

        return admin_user

    @staticmethod
    async def get_admin_by_id(db: AsyncSession, admin_id: int) -> Optional[AdminUser]:
        """Get admin user by ID."""
        result = await db.execute(
            select(AdminUser).where(AdminUser.id == admin_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def log_admin_action(
        db: AsyncSession,
        admin_id: int,
        action_type: str,
        entity_type: str,
        entity_id: int,
        details: Optional[str] = None
    ):
        """Log an admin action for audit trail."""
        log_entry = AdminActionLog(
            admin_id=admin_id,
            action_type=action_type,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details
        )

        db.add(log_entry)
        await db.commit()
```

#### Step 4: Create Admin API Endpoints (2 hours)

Create `app/api/admin_auth.py`:

```python
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt
from typing import Optional
from app.database import get_db
from app.services.admin_service import AdminService, SECRET_KEY, ALGORITHM
from app.schemas.admin import (
    AdminUserCreate, AdminUserLogin, AdminUserResponse, TokenResponse
)
from app.models.admin_user import AdminUser, AdminRole

router = APIRouter(prefix="/api/admin/auth", tags=["Admin Auth"])
security = HTTPBearer()

# Dependency to get current admin user from JWT token
async def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> AdminUser:
    """Get current admin user from JWT token."""
    token = credentials.credentials

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        admin_id: int = payload.get("sub")
        if admin_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    admin_user = await AdminService.get_admin_by_id(db, admin_id=int(admin_id))
    if admin_user is None:
        raise credentials_exception

    if not admin_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive admin user")

    return admin_user

# Dependency to check if admin has specific role
def require_role(required_role: AdminRole):
    async def role_checker(current_admin: AdminUser = Depends(get_current_admin)) -> AdminUser:
        if current_admin.role != required_role and current_admin.role != AdminRole.SUPERADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_admin
    return role_checker

@router.post("/register", response_model=AdminUserResponse, status_code=status.HTTP_201_CREATED)
async def register_admin(
    admin_data: AdminUserCreate,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(require_role(AdminRole.SUPERADMIN))
):
    """Register a new admin user (Superadmin only)."""
    # Check if email already exists
    from sqlalchemy import select
    result = await db.execute(
        select(AdminUser).where(AdminUser.email == admin_data.email)
    )
    existing_admin = result.scalar_one_or_none()

    if existing_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    admin_user = await AdminService.create_admin_user(db, admin_data)

    # Log the action
    await AdminService.log_admin_action(
        db, current_admin.id, "create_admin", "admin_user", admin_user.id,
        f"Created admin: {admin_user.email} with role {admin_user.role.value}"
    )

    return admin_user

@router.post("/login", response_model=TokenResponse)
async def login_admin(
    login_data: AdminUserLogin,
    db: AsyncSession = Depends(get_db)
):
    """Admin user login."""
    admin_user = await AdminService.authenticate_admin(db, login_data)

    if not admin_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    # Create access token
    access_token = AdminService.create_access_token(
        data={"sub": str(admin_user.id), "email": admin_user.email, "role": admin_user.role.value}
    )

    return TokenResponse(access_token=access_token)

@router.get("/me", response_model=AdminUserResponse)
async def get_current_admin_user(current_admin: AdminUser = Depends(get_current_admin)):
    """Get current admin user details."""
    return current_admin
```

Update `app/main.py` to include admin auth router:

```python
from app.api import admin_auth

app.include_router(admin_auth.router)
```

#### Step 5: Create Initial Superadmin (1 hour)

Create management script `scripts/create_superadmin.py`:

```python
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import async_session_maker
from app.services.admin_service import AdminService
from app.schemas.admin import AdminUserCreate
from app.models.admin_user import AdminRole

async def create_superadmin():
    """Create initial superadmin user."""
    async with async_session_maker() as db:
        email = input("Enter superadmin email: ")
        password = input("Enter password (min 8 characters): ")
        full_name = input("Enter full name: ")

        admin_data = AdminUserCreate(
            email=email,
            password=password,
            full_name=full_name,
            role=AdminRole.SUPERADMIN
        )

        try:
            admin_user = await AdminService.create_admin_user(db, admin_data)
            print(f"✅ Superadmin created: {admin_user.email}")
            print(f"   Role: {admin_user.role.value}")
            print(f"   ID: {admin_user.id}")
        except Exception as e:
            print(f"❌ Error creating superadmin: {e}")

if __name__ == "__main__":
    asyncio.run(create_superadmin())
```

Run the script:
```bash
python scripts/create_superadmin.py
```

#### Step 6: Test Admin Authentication (30 minutes)

Create test file `tests/test_admin_auth.py`:

```python
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_admin_login_success():
    """Test successful admin login."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/admin/auth/login",
            json={
                "email": "admin@test.com",
                "password": "testpassword123"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_admin_login_invalid_credentials():
    """Test admin login with invalid credentials."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/admin/auth/login",
            json={
                "email": "admin@test.com",
                "password": "wrongpassword"
            }
        )

        assert response.status_code == 401

@pytest.mark.asyncio
async def test_get_current_admin():
    """Test getting current admin user details."""
    # First login to get token
    async with AsyncClient(app=app, base_url="http://test") as client:
        login_response = await client.post(
            "/api/admin/auth/login",
            json={
                "email": "admin@test.com",
                "password": "testpassword123"
            }
        )
        token = login_response.json()["access_token"]

        # Get current admin details
        response = await client.get(
            "/api/admin/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "admin@test.com"
```

Run tests:
```bash
pytest tests/test_admin_auth.py -v
```

**Day 1 Deliverables:**
- [ ] Admin user model created
- [ ] Admin action log model created
- [ ] Database migrations applied
- [ ] Admin service with authentication implemented
- [ ] JWT token creation and validation working
- [ ] Admin auth API endpoints created
- [ ] Superadmin user created
- [ ] Authentication tests passing

---

### **DAY 2: Admin API - User & Deposit Management (6-8 hours)**

**Goal:** Create admin API endpoints for user management and deposit approval.

#### Step 1: User Management API (2 hours)

Create `app/api/admin_users.py`:

```python
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from typing import List, Optional
from app.database import get_db
from app.models.user import User
from app.models.wallet import Wallet
from app.models.transaction import Transaction
from app.models.bet import Bet
from app.services.admin_service import AdminService
from app.api.admin_auth import get_current_admin
from app.models.admin_user import AdminUser
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/api/admin/users", tags=["Admin - Users"])

# Schemas
class UserDetailResponse(BaseModel):
    id: int
    phone_number: str
    is_active: bool
    is_blocked: bool
    created_at: datetime
    wallet_balance: float
    total_deposits: float
    total_withdrawals: float
    total_bets: int
    total_wagered: float
    total_winnings: float

    class Config:
        from_attributes = True

class UserListResponse(BaseModel):
    id: int
    phone_number: str
    is_active: bool
    is_blocked: bool
    created_at: datetime
    wallet_balance: float

    class Config:
        from_attributes = True

class PaginatedUsersResponse(BaseModel):
    users: List[UserListResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

class BlockUserRequest(BaseModel):
    reason: str

@router.get("/", response_model=PaginatedUsersResponse)
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    search: Optional[str] = None,
    is_blocked: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """List all users with pagination and filtering."""

    # Base query
    query = select(User).join(Wallet, User.id == Wallet.user_id)

    # Apply filters
    if search:
        query = query.where(User.phone_number.contains(search))

    if is_blocked is not None:
        query = query.where(User.is_blocked == is_blocked)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size).order_by(User.created_at.desc())

    # Execute query
    result = await db.execute(query)
    users = result.scalars().all()

    # Build response
    user_list = []
    for user in users:
        wallet_result = await db.execute(
            select(Wallet).where(Wallet.user_id == user.id)
        )
        wallet = wallet_result.scalar_one()

        user_list.append(UserListResponse(
            id=user.id,
            phone_number=user.phone_number,
            is_active=user.is_active,
            is_blocked=user.is_blocked,
            created_at=user.created_at,
            wallet_balance=float(wallet.balance)
        ))

    return PaginatedUsersResponse(
        users=user_list,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )

@router.get("/{user_id}", response_model=UserDetailResponse)
async def get_user_details(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Get detailed information about a specific user."""

    # Get user
    user_result = await db.execute(select(User).where(User.id == user_id))
    user = user_result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get wallet
    wallet_result = await db.execute(select(Wallet).where(Wallet.user_id == user_id))
    wallet = wallet_result.scalar_one()

    # Get deposit total
    from app.models.deposit import Deposit, DepositStatus
    deposit_result = await db.execute(
        select(func.sum(Deposit.amount)).where(
            Deposit.user_id == user_id,
            Deposit.status == DepositStatus.APPROVED
        )
    )
    total_deposits = deposit_result.scalar_one() or 0

    # Get withdrawal total
    from app.models.withdrawal import Withdrawal, WithdrawalStatus
    withdrawal_result = await db.execute(
        select(func.sum(Withdrawal.amount)).where(
            Withdrawal.user_id == user_id,
            Withdrawal.status == WithdrawalStatus.APPROVED
        )
    )
    total_withdrawals = withdrawal_result.scalar_one() or 0

    # Get bet statistics
    bet_count_result = await db.execute(
        select(func.count()).where(Bet.user_id == user_id)
    )
    total_bets = bet_count_result.scalar_one()

    bet_wagered_result = await db.execute(
        select(func.sum(Bet.stake)).where(Bet.user_id == user_id)
    )
    total_wagered = bet_wagered_result.scalar_one() or 0

    from app.models.bet import BetStatus
    bet_winnings_result = await db.execute(
        select(func.sum(Bet.payout)).where(
            Bet.user_id == user_id,
            Bet.status == BetStatus.WON
        )
    )
    total_winnings = bet_winnings_result.scalar_one() or 0

    return UserDetailResponse(
        id=user.id,
        phone_number=user.phone_number,
        is_active=user.is_active,
        is_blocked=user.is_blocked,
        created_at=user.created_at,
        wallet_balance=float(wallet.balance),
        total_deposits=float(total_deposits),
        total_withdrawals=float(total_withdrawals),
        total_bets=total_bets,
        total_wagered=float(total_wagered),
        total_winnings=float(total_winnings)
    )

@router.post("/{user_id}/block")
async def block_user(
    user_id: int,
    request: BlockUserRequest,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Block a user from placing bets."""

    user_result = await db.execute(select(User).where(User.id == user_id))
    user = user_result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.is_blocked:
        raise HTTPException(status_code=400, detail="User is already blocked")

    user.is_blocked = True
    await db.commit()

    # Log admin action
    await AdminService.log_admin_action(
        db, current_admin.id, "block_user", "user", user_id,
        f"Blocked user {user.phone_number}. Reason: {request.reason}"
    )

    # TODO: Send WhatsApp notification to user

    return {"message": "User blocked successfully"}

@router.post("/{user_id}/unblock")
async def unblock_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Unblock a user."""

    user_result = await db.execute(select(User).where(User.id == user_id))
    user = user_result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not user.is_blocked:
        raise HTTPException(status_code=400, detail="User is not blocked")

    user.is_blocked = False
    await db.commit()

    # Log admin action
    await AdminService.log_admin_action(
        db, current_admin.id, "unblock_user", "user", user_id,
        f"Unblocked user {user.phone_number}"
    )

    # TODO: Send WhatsApp notification to user

    return {"message": "User unblocked successfully"}
```

#### Step 2: Deposit Management API (2 hours)

Create `app/api/admin_deposits.py`:

```python
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from app.database import get_db
from app.models.deposit import Deposit, DepositStatus
from app.models.user import User
from app.services.admin_service import AdminService
from app.services.deposit_service import DepositService
from app.api.admin_auth import get_current_admin
from app.models.admin_user import AdminUser
from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal

router = APIRouter(prefix="/api/admin/deposits", tags=["Admin - Deposits"])

# Schemas
class DepositResponse(BaseModel):
    id: int
    user_id: int
    user_phone: str
    amount: Decimal
    payment_method: str
    payment_metadata: Optional[dict]
    status: DepositStatus
    created_at: datetime
    processed_at: Optional[datetime]
    processed_by_admin_id: Optional[int]
    admin_notes: Optional[str]

    class Config:
        from_attributes = True

class PaginatedDepositsResponse(BaseModel):
    deposits: List[DepositResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

class ApproveDepositRequest(BaseModel):
    notes: Optional[str] = None

class RejectDepositRequest(BaseModel):
    reason: str
    notes: Optional[str] = None

@router.get("/", response_model=PaginatedDepositsResponse)
async def list_deposits(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    status: Optional[DepositStatus] = None,
    payment_method: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """List all deposits with filtering."""

    # Base query
    query = select(Deposit).join(User, Deposit.user_id == User.id)

    # Apply filters
    if status:
        query = query.where(Deposit.status == status)

    if payment_method:
        query = query.where(Deposit.payment_method == payment_method)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size).order_by(Deposit.created_at.desc())

    # Execute query
    result = await db.execute(query)
    deposits = result.scalars().all()

    # Build response with user phone numbers
    deposit_list = []
    for deposit in deposits:
        user_result = await db.execute(select(User).where(User.id == deposit.user_id))
        user = user_result.scalar_one()

        deposit_list.append(DepositResponse(
            id=deposit.id,
            user_id=deposit.user_id,
            user_phone=user.phone_number,
            amount=deposit.amount,
            payment_method=deposit.payment_method,
            payment_metadata=deposit.payment_metadata,
            status=deposit.status,
            created_at=deposit.created_at,
            processed_at=deposit.processed_at,
            processed_by_admin_id=deposit.processed_by_admin_id,
            admin_notes=deposit.admin_notes
        ))

    return PaginatedDepositsResponse(
        deposits=deposit_list,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )

@router.get("/pending", response_model=List[DepositResponse])
async def list_pending_deposits(
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Get all pending deposits for quick approval."""

    result = await db.execute(
        select(Deposit)
        .where(Deposit.status == DepositStatus.PENDING)
        .order_by(Deposit.created_at.asc())
    )
    deposits = result.scalars().all()

    # Build response
    deposit_list = []
    for deposit in deposits:
        user_result = await db.execute(select(User).where(User.id == deposit.user_id))
        user = user_result.scalar_one()

        deposit_list.append(DepositResponse(
            id=deposit.id,
            user_id=deposit.user_id,
            user_phone=user.phone_number,
            amount=deposit.amount,
            payment_method=deposit.payment_method,
            payment_metadata=deposit.payment_metadata,
            status=deposit.status,
            created_at=deposit.created_at,
            processed_at=deposit.processed_at,
            processed_by_admin_id=deposit.processed_by_admin_id,
            admin_notes=deposit.admin_notes
        ))

    return deposit_list

@router.post("/{deposit_id}/approve")
async def approve_deposit(
    deposit_id: int,
    request: ApproveDepositRequest,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Approve a deposit and credit user wallet."""

    try:
        await DepositService.approve_deposit(
            db, deposit_id, current_admin.id, request.notes
        )

        # Log admin action
        await AdminService.log_admin_action(
            db, current_admin.id, "approve_deposit", "deposit", deposit_id,
            f"Approved deposit. Notes: {request.notes}"
        )

        return {"message": "Deposit approved and wallet credited"}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error approving deposit: {str(e)}")

@router.post("/{deposit_id}/reject")
async def reject_deposit(
    deposit_id: int,
    request: RejectDepositRequest,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Reject a deposit request."""

    try:
        await DepositService.reject_deposit(
            db, deposit_id, current_admin.id, request.reason, request.notes
        )

        # Log admin action
        await AdminService.log_admin_action(
            db, current_admin.id, "reject_deposit", "deposit", deposit_id,
            f"Rejected deposit. Reason: {request.reason}. Notes: {request.notes}"
        )

        return {"message": "Deposit rejected"}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error rejecting deposit: {str(e)}")
```

Update `app/services/deposit_service.py` to add admin approval methods:

```python
@staticmethod
async def approve_deposit(
    db: AsyncSession,
    deposit_id: int,
    admin_id: int,
    notes: Optional[str] = None
):
    """Approve a deposit and credit wallet."""
    from app.services.wallet_service import WalletService
    from app.services.whatsapp import WhatsAppService

    # Get deposit
    result = await db.execute(select(Deposit).where(Deposit.id == deposit_id))
    deposit = result.scalar_one_or_none()

    if not deposit:
        raise ValueError("Deposit not found")

    if deposit.status != DepositStatus.PENDING:
        raise ValueError(f"Deposit is already {deposit.status.value}")

    # Update deposit status
    deposit.status = DepositStatus.APPROVED
    deposit.processed_at = datetime.utcnow()
    deposit.processed_by_admin_id = admin_id
    deposit.admin_notes = notes

    # Credit wallet
    await WalletService.credit(
        db, deposit.user_id, deposit.amount,
        "deposit", f"Deposit approved (ID: {deposit_id})"
    )

    await db.commit()

    # Send WhatsApp notification
    user_result = await db.execute(select(User).where(User.id == deposit.user_id))
    user = user_result.scalar_one()

    message = f"✅ Your deposit of R{deposit.amount} has been approved and credited to your wallet!"
    await WhatsAppService.send_message(user.phone_number, message)

@staticmethod
async def reject_deposit(
    db: AsyncSession,
    deposit_id: int,
    admin_id: int,
    reason: str,
    notes: Optional[str] = None
):
    """Reject a deposit request."""
    from app.services.whatsapp import WhatsAppService

    # Get deposit
    result = await db.execute(select(Deposit).where(Deposit.id == deposit_id))
    deposit = result.scalar_one_or_none()

    if not deposit:
        raise ValueError("Deposit not found")

    if deposit.status != DepositStatus.PENDING:
        raise ValueError(f"Deposit is already {deposit.status.value}")

    # Update deposit status
    deposit.status = DepositStatus.REJECTED
    deposit.processed_at = datetime.utcnow()
    deposit.processed_by_admin_id = admin_id
    deposit.admin_notes = notes

    await db.commit()

    # Send WhatsApp notification
    user_result = await db.execute(select(User).where(User.id == deposit.user_id))
    user = user_result.scalar_one()

    message = f"❌ Your deposit of R{deposit.amount} has been rejected.\n\nReason: {reason}\n\nPlease contact support if you have questions."
    await WhatsAppService.send_message(user.phone_number, message)
```

#### Step 3: Update Main App (15 minutes)

Update `app/main.py`:

```python
from app.api import admin_auth, admin_users, admin_deposits

app.include_router(admin_auth.router)
app.include_router(admin_users.router)
app.include_router(admin_deposits.router)
```

#### Step 4: Test Admin APIs (1.5 hours)

Create comprehensive test file `tests/test_admin_apis.py`:

```python
import pytest
from httpx import AsyncClient
from app.main import app

# Helper to get admin token
async def get_admin_token(client: AsyncClient) -> str:
    response = await client.post(
        "/api/admin/auth/login",
        json={"email": "admin@test.com", "password": "testpassword123"}
    )
    return response.json()["access_token"]

@pytest.mark.asyncio
async def test_list_users():
    """Test listing users with pagination."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        token = await get_admin_token(client)

        response = await client.get(
            "/api/admin/users/?page=1&page_size=20",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "users" in data
        assert "total" in data
        assert data["page"] == 1

@pytest.mark.asyncio
async def test_block_user():
    """Test blocking a user."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        token = await get_admin_token(client)

        response = await client.post(
            "/api/admin/users/1/block",
            headers={"Authorization": f"Bearer {token}"},
            json={"reason": "Suspicious activity"}
        )

        assert response.status_code == 200

@pytest.mark.asyncio
async def test_list_pending_deposits():
    """Test getting pending deposits."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        token = await get_admin_token(client)

        response = await client.get(
            "/api/admin/deposits/pending",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_approve_deposit():
    """Test approving a deposit."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        token = await get_admin_token(client)

        response = await client.post(
            "/api/admin/deposits/1/approve",
            headers={"Authorization": f"Bearer {token}"},
            json={"notes": "Verified payment proof"}
        )

        assert response.status_code == 200
```

**Day 2 Deliverables:**
- [ ] User management API endpoints created
- [ ] User listing with pagination working
- [ ] User details endpoint with statistics
- [ ] Block/unblock user functionality
- [ ] Deposit listing API created
- [ ] Pending deposits endpoint
- [ ] Approve/reject deposit endpoints
- [ ] Admin action logging working
- [ ] WhatsApp notifications on approval/rejection
- [ ] API tests passing

---

### **DAY 3: Admin API - Withdrawal & Bet Management (6-8 hours)**

**Goal:** Create admin API endpoints for withdrawal approval and bet monitoring.

#### Step 1: Withdrawal Management API (2 hours)

Create `app/api/admin_withdrawals.py`:

```python
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from app.database import get_db
from app.models.withdrawal import Withdrawal, WithdrawalStatus
from app.models.user import User
from app.services.admin_service import AdminService
from app.services.withdrawal_service import WithdrawalService
from app.api.admin_auth import get_current_admin
from app.models.admin_user import AdminUser
from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal

router = APIRouter(prefix="/api/admin/withdrawals", tags=["Admin - Withdrawals"])

# Schemas
class WithdrawalResponse(BaseModel):
    id: int
    user_id: int
    user_phone: str
    amount: Decimal
    bank_name: Optional[str]
    account_number: Optional[str]
    account_holder: Optional[str]
    status: WithdrawalStatus
    created_at: datetime
    processed_at: Optional[datetime]
    processed_by_admin_id: Optional[int]
    admin_notes: Optional[str]
    rejection_reason: Optional[str]

    class Config:
        from_attributes = True

class PaginatedWithdrawalsResponse(BaseModel):
    withdrawals: List[WithdrawalResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

class ApproveWithdrawalRequest(BaseModel):
    notes: Optional[str] = None

class RejectWithdrawalRequest(BaseModel):
    reason: str
    notes: Optional[str] = None

@router.get("/", response_model=PaginatedWithdrawalsResponse)
async def list_withdrawals(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    status: Optional[WithdrawalStatus] = None,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """List all withdrawals with filtering."""

    # Base query
    query = select(Withdrawal).join(User, Withdrawal.user_id == User.id)

    # Apply filters
    if status:
        query = query.where(Withdrawal.status == status)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size).order_by(Withdrawal.created_at.desc())

    # Execute query
    result = await db.execute(query)
    withdrawals = result.scalars().all()

    # Build response
    withdrawal_list = []
    for withdrawal in withdrawals:
        user_result = await db.execute(select(User).where(User.id == withdrawal.user_id))
        user = user_result.scalar_one()

        withdrawal_list.append(WithdrawalResponse(
            id=withdrawal.id,
            user_id=withdrawal.user_id,
            user_phone=user.phone_number,
            amount=withdrawal.amount,
            bank_name=withdrawal.bank_name,
            account_number=withdrawal.account_number,
            account_holder=withdrawal.account_holder,
            status=withdrawal.status,
            created_at=withdrawal.created_at,
            processed_at=withdrawal.processed_at,
            processed_by_admin_id=withdrawal.processed_by_admin_id,
            admin_notes=withdrawal.admin_notes,
            rejection_reason=withdrawal.rejection_reason
        ))

    return PaginatedWithdrawalsResponse(
        withdrawals=withdrawal_list,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )

@router.get("/pending", response_model=List[WithdrawalResponse])
async def list_pending_withdrawals(
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Get all pending withdrawals for quick approval."""

    result = await db.execute(
        select(Withdrawal)
        .where(Withdrawal.status == WithdrawalStatus.PENDING)
        .order_by(Withdrawal.created_at.asc())
    )
    withdrawals = result.scalars().all()

    # Build response
    withdrawal_list = []
    for withdrawal in withdrawals:
        user_result = await db.execute(select(User).where(User.id == withdrawal.user_id))
        user = user_result.scalar_one()

        withdrawal_list.append(WithdrawalResponse(
            id=withdrawal.id,
            user_id=withdrawal.user_id,
            user_phone=user.phone_number,
            amount=withdrawal.amount,
            bank_name=withdrawal.bank_name,
            account_number=withdrawal.account_number,
            account_holder=withdrawal.account_holder,
            status=withdrawal.status,
            created_at=withdrawal.created_at,
            processed_at=withdrawal.processed_at,
            processed_by_admin_id=withdrawal.processed_by_admin_id,
            admin_notes=withdrawal.admin_notes,
            rejection_reason=withdrawal.rejection_reason
        ))

    return withdrawal_list

@router.post("/{withdrawal_id}/approve")
async def approve_withdrawal(
    withdrawal_id: int,
    request: ApproveWithdrawalRequest,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Approve a withdrawal request."""

    try:
        await WithdrawalService.approve_withdrawal(
            db, withdrawal_id, current_admin.id, request.notes
        )

        # Log admin action
        await AdminService.log_admin_action(
            db, current_admin.id, "approve_withdrawal", "withdrawal", withdrawal_id,
            f"Approved withdrawal. Notes: {request.notes}"
        )

        return {"message": "Withdrawal approved"}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error approving withdrawal: {str(e)}")

@router.post("/{withdrawal_id}/reject")
async def reject_withdrawal(
    withdrawal_id: int,
    request: RejectWithdrawalRequest,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Reject a withdrawal request and refund balance."""

    try:
        await WithdrawalService.reject_withdrawal(
            db, withdrawal_id, current_admin.id, request.reason, request.notes
        )

        # Log admin action
        await AdminService.log_admin_action(
            db, current_admin.id, "reject_withdrawal", "withdrawal", withdrawal_id,
            f"Rejected withdrawal. Reason: {request.reason}. Notes: {request.notes}"
        )

        return {"message": "Withdrawal rejected and balance refunded"}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error rejecting withdrawal: {str(e)}")
```

Update `app/services/withdrawal_service.py`:

```python
@staticmethod
async def approve_withdrawal(
    db: AsyncSession,
    withdrawal_id: int,
    admin_id: int,
    notes: Optional[str] = None
):
    """Approve a withdrawal (admin marks as paid)."""
    from app.services.whatsapp import WhatsAppService

    # Get withdrawal
    result = await db.execute(select(Withdrawal).where(Withdrawal.id == withdrawal_id))
    withdrawal = result.scalar_one_or_none()

    if not withdrawal:
        raise ValueError("Withdrawal not found")

    if withdrawal.status != WithdrawalStatus.PENDING:
        raise ValueError(f"Withdrawal is already {withdrawal.status.value}")

    # Update withdrawal status
    withdrawal.status = WithdrawalStatus.APPROVED
    withdrawal.processed_at = datetime.utcnow()
    withdrawal.processed_by_admin_id = admin_id
    withdrawal.admin_notes = notes

    await db.commit()

    # Send WhatsApp notification
    user_result = await db.execute(select(User).where(User.id == withdrawal.user_id))
    user = user_result.scalar_one()

    message = f"✅ Your withdrawal of R{withdrawal.amount} has been approved and processed!\n\nFunds should reflect in your account within 24-48 hours."
    await WhatsAppService.send_message(user.phone_number, message)

@staticmethod
async def reject_withdrawal(
    db: AsyncSession,
    withdrawal_id: int,
    admin_id: int,
    reason: str,
    notes: Optional[str] = None
):
    """Reject a withdrawal and refund balance."""
    from app.services.wallet_service import WalletService
    from app.services.whatsapp import WhatsAppService

    # Get withdrawal
    result = await db.execute(select(Withdrawal).where(Withdrawal.id == withdrawal_id))
    withdrawal = result.scalar_one_or_none()

    if not withdrawal:
        raise ValueError("Withdrawal not found")

    if withdrawal.status != WithdrawalStatus.PENDING:
        raise ValueError(f"Withdrawal is already {withdrawal.status.value}")

    # Refund the amount to wallet
    await WalletService.credit(
        db, withdrawal.user_id, withdrawal.amount,
        "withdrawal_refund", f"Withdrawal rejected and refunded (ID: {withdrawal_id})"
    )

    # Update withdrawal status
    withdrawal.status = WithdrawalStatus.REJECTED
    withdrawal.processed_at = datetime.utcnow()
    withdrawal.processed_by_admin_id = admin_id
    withdrawal.rejection_reason = reason
    withdrawal.admin_notes = notes

    await db.commit()

    # Send WhatsApp notification
    user_result = await db.execute(select(User).where(User.id == withdrawal.user_id))
    user = user_result.scalar_one()

    message = f"❌ Your withdrawal of R{withdrawal.amount} has been rejected and the amount has been refunded to your wallet.\n\nReason: {reason}\n\nPlease contact support if you have questions."
    await WhatsAppService.send_message(user.phone_number, message)
```

#### Step 2: Bet Monitoring API (2.5 hours)

Create `app/api/admin_bets.py`:

```python
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from app.database import get_db
from app.models.bet import Bet, BetStatus, GameType
from app.models.user import User
from app.api.admin_auth import get_current_admin
from app.models.admin_user import AdminUser
from pydantic import BaseModel
from datetime import datetime, date
from decimal import Decimal

router = APIRouter(prefix="/api/admin/bets", tags=["Admin - Bets"])

# Schemas
class BetResponse(BaseModel):
    id: int
    user_id: int
    user_phone: str
    game_type: GameType
    stake: Decimal
    selection: dict
    status: BetStatus
    result: Optional[dict]
    payout: Decimal
    created_at: datetime
    settled_at: Optional[datetime]

    class Config:
        from_attributes = True

class PaginatedBetsResponse(BaseModel):
    bets: List[BetResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

class BetStatistics(BaseModel):
    total_bets: int
    active_bets: int
    settled_bets: int
    won_bets: int
    lost_bets: int
    total_wagered: Decimal
    total_payouts: Decimal
    net_revenue: Decimal

@router.get("/", response_model=PaginatedBetsResponse)
async def list_bets(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    game_type: Optional[GameType] = None,
    status: Optional[BetStatus] = None,
    user_id: Optional[int] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """List all bets with filtering."""

    # Base query
    query = select(Bet).join(User, Bet.user_id == User.id)

    # Apply filters
    if game_type:
        query = query.where(Bet.game_type == game_type)

    if status:
        query = query.where(Bet.status == status)

    if user_id:
        query = query.where(Bet.user_id == user_id)

    if date_from:
        query = query.where(Bet.created_at >= date_from)

    if date_to:
        from datetime import timedelta
        query = query.where(Bet.created_at < date_to + timedelta(days=1))

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size).order_by(Bet.created_at.desc())

    # Execute query
    result = await db.execute(query)
    bets = result.scalars().all()

    # Build response
    bet_list = []
    for bet in bets:
        user_result = await db.execute(select(User).where(User.id == bet.user_id))
        user = user_result.scalar_one()

        bet_list.append(BetResponse(
            id=bet.id,
            user_id=bet.user_id,
            user_phone=user.phone_number,
            game_type=bet.game_type,
            stake=bet.stake,
            selection=bet.selection,
            status=bet.status,
            result=bet.result,
            payout=bet.payout,
            created_at=bet.created_at,
            settled_at=bet.settled_at
        ))

    return PaginatedBetsResponse(
        bets=bet_list,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )

@router.get("/statistics", response_model=BetStatistics)
async def get_bet_statistics(
    game_type: Optional[GameType] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Get betting statistics."""

    # Base query
    query = select(Bet)

    # Apply filters
    if game_type:
        query = query.where(Bet.game_type == game_type)

    if date_from:
        query = query.where(Bet.created_at >= date_from)

    if date_to:
        from datetime import timedelta
        query = query.where(Bet.created_at < date_to + timedelta(days=1))

    # Total bets
    total_bets_result = await db.execute(
        select(func.count()).select_from(query.subquery())
    )
    total_bets = total_bets_result.scalar_one()

    # Active bets
    active_query = query.where(Bet.status == BetStatus.ACTIVE)
    active_result = await db.execute(
        select(func.count()).select_from(active_query.subquery())
    )
    active_bets = active_result.scalar_one()

    # Settled bets
    settled_bets = total_bets - active_bets

    # Won bets
    won_query = query.where(Bet.status == BetStatus.WON)
    won_result = await db.execute(
        select(func.count()).select_from(won_query.subquery())
    )
    won_bets = won_result.scalar_one()

    # Lost bets
    lost_query = query.where(Bet.status == BetStatus.LOST)
    lost_result = await db.execute(
        select(func.count()).select_from(lost_query.subquery())
    )
    lost_bets = lost_result.scalar_one()

    # Total wagered
    wagered_result = await db.execute(
        select(func.sum(Bet.stake)).select_from(query.subquery())
    )
    total_wagered = wagered_result.scalar_one() or Decimal("0")

    # Total payouts
    payout_query = query.where(Bet.status == BetStatus.WON)
    payout_result = await db.execute(
        select(func.sum(Bet.payout)).select_from(payout_query.subquery())
    )
    total_payouts = payout_result.scalar_one() or Decimal("0")

    # Net revenue (stakes - payouts)
    net_revenue = total_wagered - total_payouts

    return BetStatistics(
        total_bets=total_bets,
        active_bets=active_bets,
        settled_bets=settled_bets,
        won_bets=won_bets,
        lost_bets=lost_bets,
        total_wagered=total_wagered,
        total_payouts=total_payouts,
        net_revenue=net_revenue
    )

@router.get("/active", response_model=List[BetResponse])
async def list_active_bets(
    db: AsyncSession = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_admin)
):
    """Get all active (unsettled) bets."""

    result = await db.execute(
        select(Bet)
        .where(Bet.status == BetStatus.ACTIVE)
        .order_by(Bet.created_at.desc())
    )
    bets = result.scalars().all()

    # Build response
    bet_list = []
    for bet in bets:
        user_result = await db.execute(select(User).where(User.id == bet.user_id))
        user = user_result.scalar_one()

        bet_list.append(BetResponse(
            id=bet.id,
            user_id=bet.user_id,
            user_phone=user.phone_number,
            game_type=bet.game_type,
            stake=bet.stake,
            selection=bet.selection,
            status=bet.status,
            result=bet.result,
            payout=bet.payout,
            created_at=bet.created_at,
            settled_at=bet.settled_at
        ))

    return bet_list
```

#### Step 3: Update Main App (15 minutes)

Update `app/main.py`:

```python
from app.api import admin_auth, admin_users, admin_deposits, admin_withdrawals, admin_bets

app.include_router(admin_auth.router)
app.include_router(admin_users.router)
app.include_router(admin_deposits.router)
app.include_router(admin_withdrawals.router)
app.include_router(admin_bets.router)
```

#### Step 4: Test APIs (1.5 hours)

Add tests to `tests/test_admin_apis.py`:

```python
@pytest.mark.asyncio
async def test_list_pending_withdrawals():
    """Test getting pending withdrawals."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        token = await get_admin_token(client)

        response = await client.get(
            "/api/admin/withdrawals/pending",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_approve_withdrawal():
    """Test approving a withdrawal."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        token = await get_admin_token(client)

        response = await client.post(
            "/api/admin/withdrawals/1/approve",
            headers={"Authorization": f"Bearer {token}"},
            json={"notes": "Payment processed"}
        )

        assert response.status_code == 200

@pytest.mark.asyncio
async def test_get_bet_statistics():
    """Test getting bet statistics."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        token = await get_admin_token(client)

        response = await client.get(
            "/api/admin/bets/statistics",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "total_bets" in data
        assert "net_revenue" in data
```

**Day 3 Deliverables:**
- [ ] Withdrawal management API endpoints created
- [ ] Withdrawal listing with pagination
- [ ] Pending withdrawals endpoint
- [ ] Approve/reject withdrawal functionality
- [ ] Balance refund on rejection
- [ ] Bet monitoring API created
- [ ] Bet statistics endpoint
- [ ] Active bets listing
- [ ] API tests passing

---

### **DAY 4-5: React Dashboard Setup & Authentication (12-14 hours)**

**Goal:** Set up React application with Vite, implement authentication flow, and create base UI structure.

#### Step 1: Initialize React Project (1 hour)

```bash
# Create React app with Vite
cd /path/to/project
mkdir admin-dashboard
cd admin-dashboard

npm create vite@latest . -- --template react
npm install

# Install dependencies
npm install react-router-dom axios react-hook-form tailwindcss postcss autoprefixer
npm install -D @types/react @types/react-dom

# Initialize Tailwind
npx tailwindcss init -p
```

Configure `tailwind.config.js`:

```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

Update `src/index.css`:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

#### Step 2: Create Project Structure (30 minutes)

```bash
mkdir -p src/components
mkdir -p src/pages
mkdir -p src/services
mkdir -p src/hooks
mkdir -p src/context
mkdir -p src/utils
```

Create API service `src/services/api.js`:

```javascript
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('admin_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid, redirect to login
      localStorage.removeItem('admin_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
```

#### Step 3: Authentication Context (1.5 hours)

Create `src/context/AuthContext.jsx`:

```javascript
import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../services/api';

const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [admin, setAdmin] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is already logged in
    const token = localStorage.getItem('admin_token');
    if (token) {
      fetchCurrentAdmin();
    } else {
      setLoading(false);
    }
  }, []);

  const fetchCurrentAdmin = async () => {
    try {
      const response = await api.get('/api/admin/auth/me');
      setAdmin(response.data);
    } catch (error) {
      console.error('Failed to fetch current admin:', error);
      localStorage.removeItem('admin_token');
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    const response = await api.post('/api/admin/auth/login', {
      email,
      password,
    });

    const { access_token } = response.data;
    localStorage.setItem('admin_token', access_token);

    await fetchCurrentAdmin();

    return response.data;
  };

  const logout = () => {
    localStorage.removeItem('admin_token');
    setAdmin(null);
  };

  const value = {
    admin,
    login,
    logout,
    loading,
    isAuthenticated: !!admin,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
```

#### Step 4: Protected Route Component (30 minutes)

Create `src/components/ProtectedRoute.jsx`:

```javascript
import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-xl">Loading...</div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
};

export default ProtectedRoute;
```

#### Step 5: Login Page (2 hours)

Create `src/pages/Login.jsx`:

```javascript
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useForm } from 'react-hook-form';

const Login = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm();

  const onSubmit = async (data) => {
    setLoading(true);
    setError('');

    try {
      await login(data.email, data.password);
      navigate('/');
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center px-4">
      <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">MyKasiBets</h1>
          <p className="text-gray-600 mt-2">Admin Dashboard</p>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700">
              Email Address
            </label>
            <input
              type="email"
              id="email"
              {...register('email', {
                required: 'Email is required',
                pattern: {
                  value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                  message: 'Invalid email address'
                }
              })}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            />
            {errors.email && (
              <p className="mt-1 text-sm text-red-600">{errors.email.message}</p>
            )}
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700">
              Password
            </label>
            <input
              type="password"
              id="password"
              {...register('password', {
                required: 'Password is required',
                minLength: {
                  value: 8,
                  message: 'Password must be at least 8 characters'
                }
              })}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            />
            {errors.password && (
              <p className="mt-1 text-sm text-red-600">{errors.password.message}</p>
            )}
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Logging in...' : 'Log In'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default Login;
```

#### Step 6: Dashboard Layout (2 hours)

Create `src/components/Layout.jsx`:

```javascript
import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Layout = ({ children }) => {
  const { admin, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const navigation = [
    { name: 'Dashboard', href: '/', icon: '📊' },
    { name: 'Users', href: '/users', icon: '👥' },
    { name: 'Deposits', href: '/deposits', icon: '💰' },
    { name: 'Withdrawals', href: '/withdrawals', icon: '💸' },
    { name: 'Bets', href: '/bets', icon: '🎲' },
    { name: 'Matches', href: '/matches', icon: '⚽' },
    { name: 'Reports', href: '/reports', icon: '📈' },
  ];

  const isActive = (path) => location.pathname === path;

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Sidebar */}
      <div
        className={`fixed inset-y-0 left-0 z-50 w-64 bg-gray-900 text-white transform ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        } transition-transform duration-300 ease-in-out`}
      >
        <div className="flex items-center justify-between h-16 px-6 bg-gray-800">
          <h1 className="text-xl font-bold">MyKasiBets</h1>
          <button
            onClick={() => setSidebarOpen(false)}
            className="lg:hidden"
          >
            ✕
          </button>
        </div>

        <nav className="mt-6">
          {navigation.map((item) => (
            <Link
              key={item.name}
              to={item.href}
              className={`flex items-center px-6 py-3 text-sm font-medium ${
                isActive(item.href)
                  ? 'bg-gray-800 border-l-4 border-blue-500'
                  : 'hover:bg-gray-800'
              }`}
            >
              <span className="mr-3">{item.icon}</span>
              {item.name}
            </Link>
          ))}
        </nav>

        <div className="absolute bottom-0 w-full p-6 bg-gray-800">
          <div className="mb-2">
            <p className="text-sm font-medium">{admin?.full_name}</p>
            <p className="text-xs text-gray-400">{admin?.email}</p>
            <p className="text-xs text-gray-400 capitalize">{admin?.role}</p>
          </div>
          <button
            onClick={handleLogout}
            className="w-full px-4 py-2 text-sm font-medium text-white bg-red-600 rounded hover:bg-red-700"
          >
            Logout
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className={`${sidebarOpen ? 'lg:ml-64' : ''} transition-all duration-300`}>
        {/* Top Bar */}
        <div className="bg-white shadow">
          <div className="flex items-center justify-between h-16 px-6">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="text-gray-600 hover:text-gray-900"
            >
              ☰
            </button>
            <div className="text-sm text-gray-600">
              Welcome, {admin?.full_name}
            </div>
          </div>
        </div>

        {/* Page Content */}
        <main className="p-6">{children}</main>
      </div>
    </div>
  );
};

export default Layout;
```

#### Step 7: App Router Setup (1 hour)

Create `src/App.jsx`:

```javascript
import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import Layout from './components/Layout';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Users from './pages/Users';
import Deposits from './pages/Deposits';
import Withdrawals from './pages/Withdrawals';
import Bets from './pages/Bets';
import Matches from './pages/Matches';
import Reports from './pages/Reports';

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<Login />} />

          <Route
            path="/*"
            element={
              <ProtectedRoute>
                <Layout>
                  <Routes>
                    <Route path="/" element={<Dashboard />} />
                    <Route path="/users" element={<Users />} />
                    <Route path="/deposits" element={<Deposits />} />
                    <Route path="/withdrawals" element={<Withdrawals />} />
                    <Route path="/bets" element={<Bets />} />
                    <Route path="/matches" element={<Matches />} />
                    <Route path="/reports" element={<Reports />} />
                  </Routes>
                </Layout>
              </ProtectedRoute>
            }
          />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
```

#### Step 8: Create Placeholder Pages (1 hour)

Create `src/pages/Dashboard.jsx`:

```javascript
import React from 'react';

const Dashboard = () => {
  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-sm font-medium text-gray-600">Total Users</h3>
          <p className="text-3xl font-bold text-gray-900 mt-2">-</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-sm font-medium text-gray-600">Active Bets</h3>
          <p className="text-3xl font-bold text-gray-900 mt-2">-</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-sm font-medium text-gray-600">Pending Deposits</h3>
          <p className="text-3xl font-bold text-gray-900 mt-2">-</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-sm font-medium text-gray-600">Pending Withdrawals</h3>
          <p className="text-3xl font-bold text-gray-900 mt-2">-</p>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
```

Create placeholder files for other pages (Users, Deposits, Withdrawals, Bets, Matches, Reports) with similar structure.

#### Step 9: Environment Configuration (15 minutes)

Create `.env`:

```
VITE_API_BASE_URL=http://localhost:8000
```

Update `package.json` scripts:

```json
{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  }
}
```

#### Step 10: Test React App (1.5 hours)

```bash
# Start development server
npm run dev

# Open browser to http://localhost:5173
# Test login flow
# Test protected routes
# Test logout
```

**Day 4-5 Deliverables:**
- [ ] React app initialized with Vite
- [ ] Tailwind CSS configured
- [ ] Project structure created
- [ ] API service with interceptors
- [ ] Authentication context implemented
- [ ] Protected route component
- [ ] Login page with form validation
- [ ] Dashboard layout with sidebar
- [ ] Router setup with all routes
- [ ] Placeholder pages created
- [ ] Environment configuration
- [ ] Login/logout flow working

---

---

### **DAY 6: User Management Interface (6-8 hours)**

**Goal:** Build the user management interface with listing, search, filtering, and block/unblock functionality.

#### Step 1: User API Service (1 hour)

Create `src/services/userService.js`:

```javascript
import api from './api';

export const userService = {
  // Get paginated users list
  getUsers: async (page = 1, pageSize = 50, filters = {}) => {
    const params = new URLSearchParams({
      page,
      page_size: pageSize,
      ...filters,
    });

    const response = await api.get(`/api/admin/users/?${params}`);
    return response.data;
  },

  // Get user details
  getUserDetails: async (userId) => {
    const response = await api.get(`/api/admin/users/${userId}`);
    return response.data;
  },

  // Block user
  blockUser: async (userId, reason) => {
    const response = await api.post(`/api/admin/users/${userId}/block`, {
      reason,
    });
    return response.data;
  },

  // Unblock user
  unblockUser: async (userId) => {
    const response = await api.post(`/api/admin/users/${userId}/unblock`);
    return response.data;
  },
};
```

#### Step 2: Users Page Component (3 hours)

Update `src/pages/Users.jsx`:

```javascript
import React, { useState, useEffect } from 'react';
import { userService } from '../services/userService';

const Users = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [pagination, setPagination] = useState({
    page: 1,
    pageSize: 50,
    total: 0,
    totalPages: 0,
  });
  const [filters, setFilters] = useState({
    search: '',
    is_blocked: null,
  });
  const [selectedUser, setSelectedUser] = useState(null);
  const [showBlockModal, setShowBlockModal] = useState(false);
  const [blockReason, setBlockReason] = useState('');

  useEffect(() => {
    loadUsers();
  }, [pagination.page, filters]);

  const loadUsers = async () => {
    setLoading(true);
    try {
      const data = await userService.getUsers(
        pagination.page,
        pagination.pageSize,
        filters
      );

      setUsers(data.users);
      setPagination({
        ...pagination,
        total: data.total,
        totalPages: data.total_pages,
      });
    } catch (error) {
      console.error('Failed to load users:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleBlockUser = async () => {
    if (!selectedUser || !blockReason.trim()) return;

    try {
      await userService.blockUser(selectedUser.id, blockReason);
      setShowBlockModal(false);
      setBlockReason('');
      setSelectedUser(null);
      loadUsers();
    } catch (error) {
      console.error('Failed to block user:', error);
    }
  };

  const handleUnblockUser = async (user) => {
    if (!confirm(`Are you sure you want to unblock ${user.phone_number}?`)) {
      return;
    }

    try {
      await userService.unblockUser(user.id);
      loadUsers();
    } catch (error) {
      console.error('Failed to unblock user:', error);
    }
  };

  const handleSearch = (e) => {
    setFilters({ ...filters, search: e.target.value });
    setPagination({ ...pagination, page: 1 });
  };

  const handleFilterChange = (filterName, value) => {
    setFilters({ ...filters, [filterName]: value });
    setPagination({ ...pagination, page: 1 });
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Users</h1>
      </div>

      {/* Filters */}
      <div className="bg-white p-4 rounded-lg shadow mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Search by Phone
            </label>
            <input
              type="text"
              value={filters.search}
              onChange={handleSearch}
              placeholder="Search phone number..."
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Status
            </label>
            <select
              value={filters.is_blocked === null ? '' : filters.is_blocked}
              onChange={(e) =>
                handleFilterChange(
                  'is_blocked',
                  e.target.value === '' ? null : e.target.value === 'true'
                )
              }
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
            >
              <option value="">All Users</option>
              <option value="false">Active</option>
              <option value="true">Blocked</option>
            </select>
          </div>
        </div>
      </div>

      {/* Users Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        {loading ? (
          <div className="p-8 text-center">Loading...</div>
        ) : (
          <>
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Phone Number
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Wallet Balance
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Joined
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {users.map((user) => (
                  <tr key={user.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {user.phone_number}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      R {user.wallet_balance.toFixed(2)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {user.is_blocked ? (
                        <span className="px-2 py-1 text-xs font-semibold rounded-full bg-red-100 text-red-800">
                          Blocked
                        </span>
                      ) : (
                        <span className="px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">
                          Active
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(user.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      {user.is_blocked ? (
                        <button
                          onClick={() => handleUnblockUser(user)}
                          className="text-green-600 hover:text-green-900 mr-3"
                        >
                          Unblock
                        </button>
                      ) : (
                        <button
                          onClick={() => {
                            setSelectedUser(user);
                            setShowBlockModal(true);
                          }}
                          className="text-red-600 hover:text-red-900 mr-3"
                        >
                          Block
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {/* Pagination */}
            <div className="bg-gray-50 px-6 py-3 flex items-center justify-between">
              <div className="text-sm text-gray-700">
                Showing page {pagination.page} of {pagination.totalPages} (
                {pagination.total} total users)
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() =>
                    setPagination({ ...pagination, page: pagination.page - 1 })
                  }
                  disabled={pagination.page === 1}
                  className="px-3 py-1 border rounded hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Previous
                </button>
                <button
                  onClick={() =>
                    setPagination({ ...pagination, page: pagination.page + 1 })
                  }
                  disabled={pagination.page >= pagination.totalPages}
                  className="px-3 py-1 border rounded hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Next
                </button>
              </div>
            </div>
          </>
        )}
      </div>

      {/* Block User Modal */}
      {showBlockModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h2 className="text-xl font-bold mb-4">Block User</h2>
            <p className="text-sm text-gray-600 mb-4">
              Block user: {selectedUser?.phone_number}
            </p>
            <textarea
              value={blockReason}
              onChange={(e) => setBlockReason(e.target.value)}
              placeholder="Enter reason for blocking..."
              className="w-full px-3 py-2 border border-gray-300 rounded-md mb-4"
              rows="3"
            />
            <div className="flex gap-3 justify-end">
              <button
                onClick={() => {
                  setShowBlockModal(false);
                  setBlockReason('');
                  setSelectedUser(null);
                }}
                className="px-4 py-2 border border-gray-300 rounded hover:bg-gray-100"
              >
                Cancel
              </button>
              <button
                onClick={handleBlockUser}
                disabled={!blockReason.trim()}
                className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 disabled:opacity-50"
              >
                Block User
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Users;
```

#### Step 3: Test User Management (1 hour)

**Testing Checklist:**
- [ ] User list loads with pagination
- [ ] Search by phone number works
- [ ] Filter by status (active/blocked) works
- [ ] Block user modal opens
- [ ] Block user with reason works
- [ ] Unblock user works
- [ ] Pagination navigation works
- [ ] Responsive design on mobile

**Day 6 Deliverables:**
- [ ] User service API client created
- [ ] Users page with table and pagination
- [ ] Search and filter functionality
- [ ] Block user modal with reason
- [ ] Unblock user functionality
- [ ] Responsive design
- [ ] Error handling
- [ ] Loading states

---

### **DAY 7: Deposit & Withdrawal Management UI (6-8 hours)**

**Goal:** Build deposit and withdrawal approval interfaces.

#### Step 1: Deposit/Withdrawal Service (1 hour)

Create `src/services/depositService.js`:

```javascript
import api from './api';

export const depositService = {
  getDeposits: async (page = 1, pageSize = 50, filters = {}) => {
    const params = new URLSearchParams({
      page,
      page_size: pageSize,
      ...filters,
    });
    const response = await api.get(`/api/admin/deposits/?${params}`);
    return response.data;
  },

  getPendingDeposits: async () => {
    const response = await api.get('/api/admin/deposits/pending');
    return response.data;
  },

  approveDeposit: async (depositId, notes) => {
    const response = await api.post(`/api/admin/deposits/${depositId}/approve`, {
      notes,
    });
    return response.data;
  },

  rejectDeposit: async (depositId, reason, notes) => {
    const response = await api.post(`/api/admin/deposits/${depositId}/reject`, {
      reason,
      notes,
    });
    return response.data;
  },
};
```

Create `src/services/withdrawalService.js`:

```javascript
import api from './api';

export const withdrawalService = {
  getWithdrawals: async (page = 1, pageSize = 50, filters = {}) => {
    const params = new URLSearchParams({
      page,
      page_size: pageSize,
      ...filters,
    });
    const response = await api.get(`/api/admin/withdrawals/?${params}`);
    return response.data;
  },

  getPendingWithdrawals: async () => {
    const response = await api.get('/api/admin/withdrawals/pending');
    return response.data;
  },

  approveWithdrawal: async (withdrawalId, notes) => {
    const response = await api.post(
      `/api/admin/withdrawals/${withdrawalId}/approve`,
      { notes }
    );
    return response.data;
  },

  rejectWithdrawal: async (withdrawalId, reason, notes) => {
    const response = await api.post(
      `/api/admin/withdrawals/${withdrawalId}/reject`,
      { reason, notes }
    );
    return response.data;
  },
};
```

#### Step 2: Deposits Page (2.5 hours)

Update `src/pages/Deposits.jsx`:

```javascript
import React, { useState, useEffect } from 'react';
import { depositService } from '../services/depositService';

const Deposits = () => {
  const [deposits, setDeposits] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('pending'); // 'pending' or 'all'
  const [selectedDeposit, setSelectedDeposit] = useState(null);
  const [showApproveModal, setShowApproveModal] = useState(false);
  const [showRejectModal, setShowRejectModal] = useState(false);
  const [notes, setNotes] = useState('');
  const [rejectReason, setRejectReason] = useState('');

  useEffect(() => {
    loadDeposits();
  }, [activeTab]);

  const loadDeposits = async () => {
    setLoading(true);
    try {
      if (activeTab === 'pending') {
        const data = await depositService.getPendingDeposits();
        setDeposits(data);
      } else {
        const data = await depositService.getDeposits(1, 100);
        setDeposits(data.deposits);
      }
    } catch (error) {
      console.error('Failed to load deposits:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async () => {
    if (!selectedDeposit) return;

    try {
      await depositService.approveDeposit(selectedDeposit.id, notes);
      setShowApproveModal(false);
      setNotes('');
      setSelectedDeposit(null);
      loadDeposits();
    } catch (error) {
      console.error('Failed to approve deposit:', error);
      alert('Failed to approve deposit');
    }
  };

  const handleReject = async () => {
    if (!selectedDeposit || !rejectReason.trim()) return;

    try {
      await depositService.rejectDeposit(
        selectedDeposit.id,
        rejectReason,
        notes
      );
      setShowRejectModal(false);
      setRejectReason('');
      setNotes('');
      setSelectedDeposit(null);
      loadDeposits();
    } catch (error) {
      console.error('Failed to reject deposit:', error);
      alert('Failed to reject deposit');
    }
  };

  const getStatusBadge = (status) => {
    const colors = {
      pending: 'bg-yellow-100 text-yellow-800',
      approved: 'bg-green-100 text-green-800',
      rejected: 'bg-red-100 text-red-800',
    };

    return (
      <span
        className={`px-2 py-1 text-xs font-semibold rounded-full ${
          colors[status] || 'bg-gray-100 text-gray-800'
        }`}
      >
        {status.toUpperCase()}
      </span>
    );
  };

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Deposits</h1>

      {/* Tabs */}
      <div className="mb-6 border-b border-gray-200">
        <nav className="-mb-px flex gap-6">
          <button
            onClick={() => setActiveTab('pending')}
            className={`pb-2 border-b-2 ${
              activeTab === 'pending'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            Pending
          </button>
          <button
            onClick={() => setActiveTab('all')}
            className={`pb-2 border-b-2 ${
              activeTab === 'all'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            All Deposits
          </button>
        </nav>
      </div>

      {/* Deposits Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        {loading ? (
          <div className="p-8 text-center">Loading...</div>
        ) : deposits.length === 0 ? (
          <div className="p-8 text-center text-gray-500">No deposits found</div>
        ) : (
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  User
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Amount
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Payment Method
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Date
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {deposits.map((deposit) => (
                <tr key={deposit.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    {deposit.user_phone}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    R {parseFloat(deposit.amount).toFixed(2)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    {deposit.payment_method}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {getStatusBadge(deposit.status)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(deposit.created_at).toLocaleString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    {deposit.status === 'pending' && (
                      <div className="flex gap-2">
                        <button
                          onClick={() => {
                            setSelectedDeposit(deposit);
                            setShowApproveModal(true);
                          }}
                          className="text-green-600 hover:text-green-900"
                        >
                          Approve
                        </button>
                        <button
                          onClick={() => {
                            setSelectedDeposit(deposit);
                            setShowRejectModal(true);
                          }}
                          className="text-red-600 hover:text-red-900"
                        >
                          Reject
                        </button>
                      </div>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Approve Modal */}
      {showApproveModal && selectedDeposit && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h2 className="text-xl font-bold mb-4">Approve Deposit</h2>
            <div className="mb-4 p-3 bg-gray-100 rounded">
              <p className="text-sm">
                <strong>User:</strong> {selectedDeposit.user_phone}
              </p>
              <p className="text-sm">
                <strong>Amount:</strong> R {parseFloat(selectedDeposit.amount).toFixed(2)}
              </p>
              <p className="text-sm">
                <strong>Method:</strong> {selectedDeposit.payment_method}
              </p>
            </div>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Optional notes..."
              className="w-full px-3 py-2 border border-gray-300 rounded-md mb-4"
              rows="2"
            />
            <div className="flex gap-3 justify-end">
              <button
                onClick={() => {
                  setShowApproveModal(false);
                  setNotes('');
                  setSelectedDeposit(null);
                }}
                className="px-4 py-2 border border-gray-300 rounded hover:bg-gray-100"
              >
                Cancel
              </button>
              <button
                onClick={handleApprove}
                className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
              >
                Approve & Credit Wallet
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Reject Modal */}
      {showRejectModal && selectedDeposit && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h2 className="text-xl font-bold mb-4">Reject Deposit</h2>
            <div className="mb-4 p-3 bg-gray-100 rounded">
              <p className="text-sm">
                <strong>User:</strong> {selectedDeposit.user_phone}
              </p>
              <p className="text-sm">
                <strong>Amount:</strong> R {parseFloat(selectedDeposit.amount).toFixed(2)}
              </p>
            </div>
            <textarea
              value={rejectReason}
              onChange={(e) => setRejectReason(e.target.value)}
              placeholder="Reason for rejection (required)..."
              className="w-full px-3 py-2 border border-gray-300 rounded-md mb-2"
              rows="2"
            />
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Additional notes (optional)..."
              className="w-full px-3 py-2 border border-gray-300 rounded-md mb-4"
              rows="2"
            />
            <div className="flex gap-3 justify-end">
              <button
                onClick={() => {
                  setShowRejectModal(false);
                  setRejectReason('');
                  setNotes('');
                  setSelectedDeposit(null);
                }}
                className="px-4 py-2 border border-gray-300 rounded hover:bg-gray-100"
              >
                Cancel
              </button>
              <button
                onClick={handleReject}
                disabled={!rejectReason.trim()}
                className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 disabled:opacity-50"
              >
                Reject Deposit
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Deposits;
```

#### Step 3: Withdrawals Page (2.5 hours)

Update `src/pages/Withdrawals.jsx` with similar structure to Deposits page, but showing bank details and refund functionality.

**Day 7 Deliverables:**
- [ ] Deposit service API client
- [ ] Withdrawal service API client
- [ ] Deposits page with pending/all tabs
- [ ] Approve deposit modal
- [ ] Reject deposit modal
- [ ] Withdrawals page with similar structure
- [ ] Display bank account details
- [ ] All CRUD operations working

---

### **DAY 8-9: Bet Monitoring, Match Management & Dashboard (12-14 hours)**

**Goal:** Build bet monitoring interface, match management system, and populate the dashboard with real-time statistics.

#### Day 8 Part 1: Bet Monitoring (4 hours)

Create `src/services/betService.js` and `src/pages/Bets.jsx` with:
- Bet listing with filters (game type, status, date range)
- Statistics cards (total bets, active bets, win/loss ratio)
- Export to CSV functionality
- Game-specific filtering
- User bet history view

#### Day 8 Part 2: Match Management (4 hours)

Create `src/api/admin_matches.py` on backend:

```python
from fastapi import APIRouter, Depends
from app.models.football_match import FootballMatch, MatchStatus

router = APIRouter(prefix="/api/admin/matches", tags=["Admin - Matches"])

@router.post("/")
async def create_match(match_data: MatchCreate, ...):
    """Create a new football match."""
    pass

@router.post("/{match_id}/settle")
async def settle_match(match_id: int, result: str, ...):
    """Settle a match and calculate all bet payouts."""
    pass
```

Create `src/pages/Matches.jsx` with:
- Create match form (teams, odds)
- Active matches list
- Settle match interface
- Match betting statistics

#### Day 9: Dashboard with Real-time Stats (6 hours)

Update `src/pages/Dashboard.jsx` with:

```javascript
import React, { useState, useEffect } from 'react';
import { depositService } from '../services/depositService';
import { withdrawalService } from '../services/withdrawalService';
import { betService } from '../services/betService';
import { userService } from '../services/userService';

const Dashboard = () => {
  const [stats, setStats] = useState({
    totalUsers: 0,
    activeBets: 0,
    pendingDeposits: 0,
    pendingWithdrawals: 0,
    todayRevenue: 0,
    totalRevenue: 0,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardStats();
    // Refresh every 30 seconds
    const interval = setInterval(loadDashboardStats, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadDashboardStats = async () => {
    try {
      const [users, deposits, withdrawals, betStats] = await Promise.all([
        userService.getUsers(1, 1),
        depositService.getPendingDeposits(),
        withdrawalService.getPendingWithdrawals(),
        betService.getStatistics(),
      ]);

      setStats({
        totalUsers: users.total,
        activeBets: betStats.active_bets,
        pendingDeposits: deposits.length,
        pendingWithdrawals: withdrawals.length,
        todayRevenue: parseFloat(betStats.net_revenue),
        totalRevenue: parseFloat(betStats.net_revenue),
      });
    } catch (error) {
      console.error('Failed to load dashboard stats:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Dashboard</h1>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
        <StatCard
          title="Total Users"
          value={stats.totalUsers}
          icon="👥"
          color="blue"
        />
        <StatCard
          title="Active Bets"
          value={stats.activeBets}
          icon="🎲"
          color="green"
        />
        <StatCard
          title="Pending Deposits"
          value={stats.pendingDeposits}
          icon="💰"
          color="yellow"
        />
        <StatCard
          title="Pending Withdrawals"
          value={stats.pendingWithdrawals}
          icon="💸"
          color="red"
        />
      </div>

      {/* Revenue Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-sm font-medium text-gray-600">Today's Revenue</h3>
          <p className="text-3xl font-bold text-green-600 mt-2">
            R {stats.todayRevenue.toFixed(2)}
          </p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-sm font-medium text-gray-600">Total Revenue</h3>
          <p className="text-3xl font-bold text-blue-600 mt-2">
            R {stats.totalRevenue.toFixed(2)}
          </p>
        </div>
      </div>
    </div>
  );
};

const StatCard = ({ title, value, icon, color }) => {
  const colors = {
    blue: 'text-blue-600',
    green: 'text-green-600',
    yellow: 'text-yellow-600',
    red: 'text-red-600',
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-sm font-medium text-gray-600">{title}</h3>
          <p className={`text-3xl font-bold mt-2 ${colors[color]}`}>{value}</p>
        </div>
        <div className="text-4xl">{icon}</div>
      </div>
    </div>
  );
};

export default Dashboard;
```

**Day 8-9 Deliverables:**
- [ ] Bet monitoring page with filters
- [ ] Bet statistics display
- [ ] Match creation form
- [ ] Match settlement interface
- [ ] Dashboard with real-time statistics
- [ ] Auto-refresh functionality
- [ ] Revenue tracking
- [ ] All pages responsive

---

### **DAY 10: Testing, Polish & Deployment (6-8 hours)**

**Goal:** Comprehensive testing, bug fixes, UI polish, and deployment preparation.

#### Step 1: Backend Testing (2 hours)

Run comprehensive backend tests:

```bash
# Run all tests
pytest tests/ -v

# Test specific admin endpoints
pytest tests/test_admin_apis.py -v

# Check test coverage
pytest --cov=app tests/
```

Fix any failing tests and ensure >80% code coverage.

#### Step 2: Frontend Testing (2 hours)

Manual testing checklist:

**Authentication:**
- [ ] Login with valid credentials
- [ ] Login with invalid credentials
- [ ] Token expiry handling
- [ ] Logout functionality
- [ ] Protected route redirects

**User Management:**
- [ ] List users loads correctly
- [ ] Search functionality works
- [ ] Filter by status works
- [ ] Block user with reason
- [ ] Unblock user
- [ ] Pagination works

**Deposit Management:**
- [ ] Pending deposits tab shows correct data
- [ ] Approve deposit credits wallet
- [ ] Reject deposit with reason
- [ ] Status updates correctly
- [ ] All deposits tab works

**Withdrawal Management:**
- [ ] Pending withdrawals visible
- [ ] Approve withdrawal works
- [ ] Reject withdrawal refunds balance
- [ ] Bank details displayed correctly

**Bet Monitoring:**
- [ ] Active bets shown
- [ ] Filters work (game type, status, date)
- [ ] Statistics accurate
- [ ] Export to CSV works

**Match Management:**
- [ ] Create match form works
- [ ] Matches list displayed
- [ ] Settle match works
- [ ] Bets settled correctly

**Dashboard:**
- [ ] Statistics load correctly
- [ ] Auto-refresh works
- [ ] All numbers accurate
- [ ] Responsive design

#### Step 3: UI Polish (2 hours)

**Polish Tasks:**
- [ ] Add loading spinners consistently
- [ ] Add success/error toast notifications
- [ ] Improve mobile responsiveness
- [ ] Add confirmation dialogs
- [ ] Improve error messages
- [ ] Add empty states
- [ ] Add tooltips where needed
- [ ] Consistent spacing and colors
- [ ] Fix any UI bugs

**Install toast notifications:**

```bash
npm install react-hot-toast
```

Add to `src/App.jsx`:

```javascript
import { Toaster } from 'react-hot-toast';

function App() {
  return (
    <>
      <Toaster position="top-right" />
      {/* Rest of app */}
    </>
  );
}
```

Use in components:

```javascript
import toast from 'react-hot-toast';

// Success
toast.success('Deposit approved successfully!');

// Error
toast.error('Failed to approve deposit');

// Loading
toast.loading('Processing...');
```

#### Step 4: Deployment Preparation (2 hours)

**Backend Deployment (Railway/Render):**

Update `.env` for production:

```bash
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
JWT_SECRET_KEY=<generate-secure-key>
ENVIRONMENT=production
```

**Frontend Deployment (Vercel/Netlify):**

Update `vite.config.js`:

```javascript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'dist',
    sourcemap: false,
  },
});
```

Build for production:

```bash
npm run build
```

Deploy to Vercel:

```bash
npm install -g vercel
vercel --prod
```

Set environment variables in Vercel dashboard:
- `VITE_API_BASE_URL=https://your-api.railway.app`

**Day 10 Deliverables:**
- [ ] All backend tests passing
- [ ] All frontend features tested manually
- [ ] UI polished and responsive
- [ ] Toast notifications added
- [ ] Error handling improved
- [ ] Backend deployed to Railway/Render
- [ ] Frontend deployed to Vercel/Netlify
- [ ] Environment variables configured
- [ ] Production testing complete

---

## DELIVERABLES CHECKLIST

### Backend Deliverables

**Authentication & Authorization:**
- [ ] Admin user model with roles (Superadmin, Admin, Support)
- [ ] Admin action log model for audit trail
- [ ] JWT authentication middleware
- [ ] Role-based permission decorators
- [ ] Login/register endpoints
- [ ] Token validation

**User Management API:**
- [ ] List users with pagination
- [ ] Search and filter users
- [ ] Get user details with statistics
- [ ] Block/unblock user endpoints
- [ ] Admin action logging

**Deposit Management API:**
- [ ] List deposits with filtering
- [ ] Get pending deposits
- [ ] Approve deposit (credit wallet)
- [ ] Reject deposit with reason
- [ ] WhatsApp notifications

**Withdrawal Management API:**
- [ ] List withdrawals with filtering
- [ ] Get pending withdrawals
- [ ] Approve withdrawal
- [ ] Reject withdrawal (refund balance)
- [ ] WhatsApp notifications

**Bet Monitoring API:**
- [ ] List bets with comprehensive filtering
- [ ] Get bet statistics
- [ ] Get active bets
- [ ] Export functionality

**Match Management API:**
- [ ] Create football match
- [ ] List matches
- [ ] Settle match
- [ ] Calculate bet payouts

**Analytics API:**
- [ ] Financial statistics
- [ ] User engagement metrics
- [ ] Game-specific stats
- [ ] Revenue calculations

### Frontend Deliverables

**Authentication:**
- [ ] Login page with validation
- [ ] JWT token management
- [ ] Protected routes
- [ ] Logout functionality
- [ ] Auto token refresh

**Layout & Navigation:**
- [ ] Responsive sidebar
- [ ] Top navigation bar
- [ ] User profile display
- [ ] Mobile menu

**Dashboard:**
- [ ] Statistics cards
- [ ] Real-time updates
- [ ] Revenue tracking
- [ ] Quick actions

**User Management:**
- [ ] User listing with pagination
- [ ] Search and filters
- [ ] User details view
- [ ] Block/unblock functionality

**Deposit Management:**
- [ ] Pending deposits view
- [ ] All deposits view
- [ ] Approve/reject modals
- [ ] Payment proof display

**Withdrawal Management:**
- [ ] Pending withdrawals view
- [ ] All withdrawals view
- [ ] Bank details display
- [ ] Approve/reject functionality

**Bet Monitoring:**
- [ ] Bet listing with filters
- [ ] Statistics dashboard
- [ ] Active bets view
- [ ] Export functionality

**Match Management:**
- [ ] Create match form
- [ ] Match listing
- [ ] Settle match interface
- [ ] Match statistics

**UI/UX:**
- [ ] Loading states
- [ ] Error handling
- [ ] Toast notifications
- [ ] Responsive design
- [ ] Empty states
- [ ] Confirmation dialogs

---

## TESTING STRATEGY

### Backend Testing

**Unit Tests (pytest):**

```python
# Test admin authentication
def test_admin_login_success()
def test_admin_login_invalid_credentials()
def test_jwt_token_validation()
def test_role_based_access()

# Test user management
def test_list_users_with_pagination()
def test_block_user()
def test_unblock_user()

# Test deposit management
def test_approve_deposit_credits_wallet()
def test_reject_deposit()

# Test withdrawal management
def test_approve_withdrawal()
def test_reject_withdrawal_refunds_balance()

# Test bet monitoring
def test_get_bet_statistics()
def test_filter_bets_by_game_type()
```

**Integration Tests:**

```python
# Test complete workflows
def test_deposit_approval_workflow()
def test_withdrawal_approval_workflow()
def test_user_blocking_prevents_bets()
def test_match_settlement_calculates_payouts()
```

**Run tests:**

```bash
pytest tests/ -v --cov=app
```

### Frontend Testing

**Manual Testing Checklist:**

```markdown
Authentication:
- [ ] Login with valid credentials
- [ ] Login with invalid credentials
- [ ] Token expiry redirects to login
- [ ] Logout clears session
- [ ] Protected routes redirect if not authenticated

User Management:
- [ ] User list loads with correct data
- [ ] Search filters users correctly
- [ ] Pagination works
- [ ] Block user shows confirmation
- [ ] Unblock user works
- [ ] User details load correctly

Deposit Management:
- [ ] Pending deposits load
- [ ] Approve deposit works and shows success
- [ ] Reject deposit requires reason
- [ ] Status updates after action
- [ ] All deposits tab shows history

Withdrawal Management:
- [ ] Pending withdrawals load
- [ ] Approve withdrawal works
- [ ] Reject refunds balance
- [ ] Bank details visible

Bet Monitoring:
- [ ] Bets load with correct data
- [ ] Filters work (game type, status, date)
- [ ] Statistics are accurate
- [ ] Export to CSV works

Dashboard:
- [ ] Statistics load correctly
- [ ] Auto-refresh works every 30s
- [ ] All numbers match backend data
- [ ] Responsive on mobile/tablet

General:
- [ ] All pages responsive
- [ ] Loading states show
- [ ] Errors handled gracefully
- [ ] Toast notifications work
- [ ] Navigation works
```

### End-to-End Testing

**Critical User Flows:**

1. **Deposit Approval Flow:**
   - User submits deposit via WhatsApp
   - Admin sees pending deposit in dashboard
   - Admin approves deposit
   - User wallet credited
   - User receives WhatsApp notification

2. **Withdrawal Approval Flow:**
   - User requests withdrawal via WhatsApp
   - Admin sees pending withdrawal
   - Admin approves withdrawal
   - User receives notification

3. **User Blocking Flow:**
   - Admin blocks user
   - User cannot place new bets
   - User receives notification
   - Admin can unblock user

4. **Match Settlement Flow:**
   - Admin creates football match
   - Users place bets
   - Admin settles match with result
   - All bets calculated and settled
   - Winners receive payouts

---

## TROUBLESHOOTING GUIDE

### Common Backend Issues

**Issue: JWT token not being recognized**

```python
# Check SECRET_KEY is set in environment
SECRET_KEY = os.getenv("JWT_SECRET_KEY")

# Verify token format in Authorization header
# Should be: "Bearer <token>"

# Check token expiry
payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
```

**Issue: CORS errors from frontend**

```python
# Add CORS middleware in main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://your-frontend.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Issue: Database connection errors**

```bash
# Check PostgreSQL is running
pg_isready

# Verify DATABASE_URL is correct
echo $DATABASE_URL

# Test connection
psql $DATABASE_URL
```

**Issue: Admin action logging fails**

```python
# Ensure admin_action_logs table exists
alembic upgrade head

# Check foreign key constraints
# admin_id must reference existing admin_users.id
```

### Common Frontend Issues

**Issue: Login not working**

```javascript
// Check API base URL
console.log(import.meta.env.VITE_API_BASE_URL);

// Verify credentials
// Check browser console for errors
// Check Network tab for request/response

// Ensure token is saved
localStorage.getItem('admin_token');
```

**Issue: Protected routes redirecting unexpectedly**

```javascript
// Check AuthContext state
console.log(admin, isAuthenticated, loading);

// Verify token in localStorage
const token = localStorage.getItem('admin_token');

// Check token is being sent in requests
// Open Network tab > Headers > Authorization
```

**Issue: API calls failing with 401**

```javascript
// Token might be expired
// Clear localStorage and re-login
localStorage.removeItem('admin_token');

// Check interceptor is adding token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('admin_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

**Issue: Data not refreshing**

```javascript
// Check useEffect dependencies
useEffect(() => {
  loadData();
}, [page, filters]); // Add all dependencies

// Force refresh
const [refreshKey, setRefreshKey] = useState(0);
useEffect(() => {
  loadData();
}, [refreshKey]);

// Trigger refresh
setRefreshKey(prev => prev + 1);
```

**Issue: Mobile UI breaking**

```javascript
// Use responsive Tailwind classes
className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4"

// Test at different breakpoints
// sm: 640px, md: 768px, lg: 1024px, xl: 1280px

// Use mobile-first approach
className="text-sm md:text-base lg:text-lg"
```

### Performance Issues

**Backend:**

```python
# Add database indexes
from sqlalchemy import Index

Index('idx_deposit_status', Deposit.status)
Index('idx_bet_user_id', Bet.user_id)
Index('idx_bet_status', Bet.status)

# Use query optimization
from sqlalchemy.orm import selectinload

query = select(Bet).options(selectinload(Bet.user))

# Cache analytics queries
from functools import lru_cache

@lru_cache(maxsize=128)
def get_statistics(date_from, date_to):
    # Heavy calculation
    pass
```

**Frontend:**

```javascript
// Debounce search inputs
import { useState, useEffect } from 'react';

const [searchTerm, setSearchTerm] = useState('');
const [debouncedTerm, setDebouncedTerm] = useState('');

useEffect(() => {
  const timer = setTimeout(() => {
    setDebouncedTerm(searchTerm);
  }, 500);

  return () => clearTimeout(timer);
}, [searchTerm]);

// Lazy load components
const Bets = React.lazy(() => import('./pages/Bets'));

// Use React.memo for expensive components
const StatCard = React.memo(({ title, value }) => {
  // Component code
});
```

---

## NEXT STEPS

### After Phase 4 Completion

1. **Phase 5: Testing & Beta Launch**
   - Comprehensive system testing
   - Load testing with 50-300 concurrent users
   - Security audit
   - Beta user onboarding
   - Bug fixes and optimizations
   - Performance monitoring setup

2. **Production Readiness:**
   - [ ] Database backups configured
   - [ ] Monitoring and alerting (Sentry, DataDog)
   - [ ] Rate limiting on all endpoints
   - [ ] SSL certificates configured
   - [ ] Environment variables secured
   - [ ] Logging infrastructure
   - [ ] Error tracking
   - [ ] Performance monitoring

3. **Documentation:**
   - [ ] API documentation (Swagger/OpenAPI)
   - [ ] Admin user guide
   - [ ] Deployment guide
   - [ ] Troubleshooting guide
   - [ ] Code comments

4. **Future Enhancements:**
   - Real-time updates with WebSockets
   - Advanced analytics and reporting
   - Multi-currency support
   - Additional payment providers
   - Mobile admin app
   - Two-factor authentication (2FA)
   - Automated bet settlement for matches
   - Push notifications
   - Advanced user segmentation
   - A/B testing framework

---

## APPENDIX

### A. Technology Stack Summary

**Backend:**
- Python 3.10+
- FastAPI (async web framework)
- SQLAlchemy 2.0 (ORM)
- PostgreSQL 14+ (database)
- Redis (caching)
- JWT (authentication)
- bcrypt (password hashing)
- Alembic (migrations)

**Frontend:**
- React 18
- Vite (build tool)
- Tailwind CSS (styling)
- React Router (navigation)
- Axios (HTTP client)
- react-hook-form (forms)
- react-hot-toast (notifications)

**Deployment:**
- Railway/Render (backend)
- Vercel/Netlify (frontend)
- PostgreSQL (managed database)
- Redis (managed cache)

### B. API Endpoints Reference

**Authentication:**
- POST `/api/admin/auth/register` - Create admin (Superadmin only)
- POST `/api/admin/auth/login` - Admin login
- GET `/api/admin/auth/me` - Get current admin

**Users:**
- GET `/api/admin/users/` - List users
- GET `/api/admin/users/{id}` - Get user details
- POST `/api/admin/users/{id}/block` - Block user
- POST `/api/admin/users/{id}/unblock` - Unblock user

**Deposits:**
- GET `/api/admin/deposits/` - List deposits
- GET `/api/admin/deposits/pending` - Get pending deposits
- POST `/api/admin/deposits/{id}/approve` - Approve deposit
- POST `/api/admin/deposits/{id}/reject` - Reject deposit

**Withdrawals:**
- GET `/api/admin/withdrawals/` - List withdrawals
- GET `/api/admin/withdrawals/pending` - Get pending withdrawals
- POST `/api/admin/withdrawals/{id}/approve` - Approve withdrawal
- POST `/api/admin/withdrawals/{id}/reject` - Reject withdrawal

**Bets:**
- GET `/api/admin/bets/` - List bets
- GET `/api/admin/bets/statistics` - Get bet statistics
- GET `/api/admin/bets/active` - Get active bets

**Matches:**
- GET `/api/admin/matches/` - List matches
- POST `/api/admin/matches/` - Create match
- POST `/api/admin/matches/{id}/settle` - Settle match

### C. Database Schema Reference

**admin_users:**
- id, email, hashed_password, full_name, role, is_active, last_login, created_at, updated_at

**admin_action_logs:**
- id, admin_id, action_type, entity_type, entity_id, details, created_at

### D. Environment Variables

**Backend (.env):**
```bash
DATABASE_URL=postgresql://user:pass@host:port/dbname
REDIS_URL=redis://host:port
JWT_SECRET_KEY=your-secret-key
WHATSAPP_API_TOKEN=your-token
WHATSAPP_PHONE_NUMBER_ID=your-id
ENVIRONMENT=development
```

**Frontend (.env):**
```bash
VITE_API_BASE_URL=http://localhost:8000
```

---

## CONCLUSION

Phase 4 delivers a complete, production-ready admin dashboard for the MyKasiBets platform. By the end of this phase, administrators will have:

✅ Secure web interface to manage all platform operations
✅ Real-time visibility into user activity, deposits, withdrawals, and bets
✅ Efficient workflow for approving financial transactions
✅ Complete audit trail of all administrative actions
✅ Analytics and reporting for business insights
✅ Mobile-responsive interface for management on the go

**Estimated Total Time:** 10 days (60-70 hours)

**Key Success Factors:**
- Follow the day-by-day plan systematically
- Test each component thoroughly before moving forward
- Maintain code quality and documentation
- Ensure security best practices throughout
- Keep UI/UX simple and intuitive
- Monitor performance and optimize queries

**Ready for Phase 5:** After completing Phase 4, the platform will be ready for comprehensive testing, beta user onboarding, and eventual production launch.

---

**Document Version:** 1.0
**Last Updated:** 2026-01-01
**Author:** MyKasiBets Development Team
**Status:** Ready for Implementation