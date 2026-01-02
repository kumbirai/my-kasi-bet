# WhatsApp Betting Platform - Python Quick Start Guide

## Technology Stack Overview

- **Backend**: Python 3.10+ with FastAPI
- **Database**: PostgreSQL 14+ with SQLAlchemy ORM
- **Caching**: Redis
- **WhatsApp**: WhatsApp Business API (Meta)
- **Admin Dashboard**: React + Tailwind CSS
- **Deployment**: Railway.app or Render
- **Authentication**: JWT (PyJWT)

## Prerequisites

Before starting, ensure you have:

- **Python 3.10+** installed (`python --version`)
- **PostgreSQL 14+** installed and running
- **Redis** installed (optional for MVP)
- **WhatsApp Business API** account with:
  - Phone Number ID
  - Access Token
  - Verify Token (you choose this)
- **Git** for version control
- **Code editor** (VS Code recommended with Python extension)

---

## Step 1: WhatsApp Business API Setup (30 minutes)

### 1.1 Create Meta Developer Account

1. Go to https://developers.facebook.com/
2. Create/login to your account
3. Click "My Apps" → "Create App"
4. Select "Business" type
5. Fill in app details

### 1.2 Add WhatsApp Product

1. In your app dashboard, click "Add Product"
2. Find "WhatsApp" and click "Set Up"
3. Select a Business Portfolio or create new one
4. Add a phone number (Meta provides test number)

### 1.3 Get Your Credentials

From the WhatsApp setup page, note these down:

```
Phone Number ID: 123456789012345
Access Token: EAAxxxxxxxxxxxxxxxxx (temporary - 24 hours)
```

### 1.4 Generate Permanent Access Token

1. Go to App Settings → Basic
2. Note your App ID and App Secret
3. Generate System User Access Token:
   - Go to Business Settings → System Users
   - Create system user or use existing
   - Generate token with `whatsapp_business_messaging` and `whatsapp_business_management` permissions
4. Save this token securely (this won't expire)

### 1.5 Configure Webhook

We'll do this after deploying the server in Step 6.

---

## Step 2: Project Setup (10 minutes)

### 2.1 Create Project Directory

```bash
mkdir betting-platform
cd betting-platform
```

### 2.2 Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate
```

You should see `(venv)` in your terminal prompt.

### 2.3 Create Project Structure

```bash
mkdir -p app/{models,schemas,services/games,api,utils}
mkdir tests
touch app/__init__.py
touch app/{models,schemas,services,api,utils}/__init__.py
touch app/services/games/__init__.py
```

### 2.4 Create requirements.txt

Create `requirements.txt` with this content:

```txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlalchemy==2.0.25
psycopg2-binary==2.9.9
alembic==1.13.1
pydantic==2.5.3
pydantic-settings==2.1.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
httpx==0.26.0
redis==5.0.1
celery==5.3.4
python-dotenv==1.0.0
pytest==7.4.4
pytest-asyncio==0.23.3
```

### 2.5 Install Dependencies

```bash
pip install -r requirements.txt
```

This will take 2-3 minutes.

---

## Step 3: Database Setup (15 minutes)

### 3.1 Create PostgreSQL Database

```bash
# Connect to PostgreSQL
psql postgres

# Create database
CREATE DATABASE betting_db;

# Create user (optional, for security)
CREATE USER betting_user WITH PASSWORD 'secure_password_here';

# Grant privileges
GRANT ALL PRIVILEGES ON DATABASE betting_db TO betting_user;

# Exit
\q
```

### 3.2 Create Database Schema

Create `database/schema.sql`:

```sql
-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    phone_number VARCHAR(20) UNIQUE NOT NULL,
    username VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    is_blocked BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_active TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Wallets table
CREATE TABLE wallets (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    balance NUMERIC(10, 2) DEFAULT 0.00 NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Transactions table
CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    type VARCHAR(20) NOT NULL,
    amount NUMERIC(10, 2) NOT NULL,
    balance_before NUMERIC(10, 2) NOT NULL,
    balance_after NUMERIC(10, 2) NOT NULL,
    reference_id INTEGER,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Bets table
CREATE TABLE bets (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    game_type VARCHAR(50) NOT NULL,
    stake_amount NUMERIC(10, 2) NOT NULL,
    user_selection VARCHAR(100),
    game_result VARCHAR(100),
    status VARCHAR(20) DEFAULT 'pending',
    potential_win NUMERIC(10, 2),
    actual_win NUMERIC(10, 2) DEFAULT 0.00,
    odds NUMERIC(10, 2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    settled_at TIMESTAMP WITH TIME ZONE
);

-- Deposits table
CREATE TABLE deposits (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    amount NUMERIC(10, 2) NOT NULL,
    method VARCHAR(50),
    reference VARCHAR(200),
    status VARCHAR(20) DEFAULT 'pending',
    approved_by INTEGER REFERENCES admin_users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    approved_at TIMESTAMP WITH TIME ZONE
);

-- Withdrawals table
CREATE TABLE withdrawals (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    amount NUMERIC(10, 2) NOT NULL,
    method VARCHAR(50),
    account_details TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    processed_by INTEGER REFERENCES admin_users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP WITH TIME ZONE
);

-- Admin users table
CREATE TABLE admin_users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100),
    role VARCHAR(20) DEFAULT 'admin',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Game rounds table (optional - for audit)
CREATE TABLE game_rounds (
    id SERIAL PRIMARY KEY,
    game_type VARCHAR(50) NOT NULL,
    result VARCHAR(100),
    seed VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_users_phone ON users(phone_number);
CREATE INDEX idx_transactions_user_id ON transactions(user_id);
CREATE INDEX idx_transactions_created_at ON transactions(created_at);
CREATE INDEX idx_bets_user_id ON bets(user_id);
CREATE INDEX idx_bets_status ON bets(status);
CREATE INDEX idx_bets_created_at ON bets(created_at);
```

### 3.3 Load Schema

```bash
psql -d betting_db -f database/schema.sql
```

### 3.4 Verify Tables Created

```bash
psql -d betting_db -c "\dt"
```

You should see all 8 tables listed.

---

## Step 4: Environment Configuration (5 minutes)

Create `.env` file in project root:

```env
# WhatsApp Business API
WHATSAPP_API_URL=https://graph.facebook.com/v18.0
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id_here
WHATSAPP_ACCESS_TOKEN=your_permanent_access_token_here
WHATSAPP_VERIFY_TOKEN=choose_a_random_string_min_20_chars

# Database
DATABASE_URL=postgresql://betting_user:secure_password_here@localhost:5432/betting_db

# Redis (optional for MVP)
REDIS_URL=redis://localhost:6379/0

# JWT Security
SECRET_KEY=generate_random_32_char_string_use_secrets_token_hex
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Server
PORT=8000
```

### Generate Secret Key

```python
# Run in Python to generate secret key
import secrets
print(secrets.token_hex(32))
```

Copy the output to `SECRET_KEY` in `.env`.

### Create .gitignore

```
# Virtual Environment
venv/
env/
ENV/

# Environment Variables
.env
.env.local

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python

# IDEs
.vscode/
.idea/
*.swp
*.swo

# Logs
*.log

# Database
*.db
*.sqlite3

# OS
.DS_Store
Thumbs.db
```

---

## Step 5: Create Core Application Files (20 minutes)

### 5.1 config.py

Create `app/config.py`:

```python
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    WHATSAPP_API_URL: str
    WHATSAPP_PHONE_NUMBER_ID: str
    WHATSAPP_ACCESS_TOKEN: str
    WHATSAPP_VERIFY_TOKEN: str
    
    DATABASE_URL: str
    REDIS_URL: str = "redis://localhost:6379/0"
    
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
```

### 5.2 database.py

Create `app/database.py`:

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### 5.3 main.py

Create `app/main.py`:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="MyKasiBets Betting Platform", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "MyKasiBets API", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

## Step 6: Test Your Setup (10 minutes)

### 6.1 Start the Server

```bash
uvicorn app.main:app --reload --port 8000
```

You should see:

```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### 6.2 Test API

Open browser and go to:
- http://localhost:8000 - Should show welcome message
- http://localhost:8000/docs - Should show FastAPI auto-generated docs
- http://localhost:8000/health - Should return `{"status": "healthy"}`

### 6.3 Test Database Connection

Create `test_db.py` in project root:

```python
from app.database import SessionLocal
from sqlalchemy import text

def test_db_connection():
    db = SessionLocal()
    try:
        result = db.execute(text("SELECT 1"))
        print("✅ Database connection successful!")
        print(f"Result: {result.scalar()}")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_db_connection()
```

Run it:

```bash
python test_db.py
```

Should output: `✅ Database connection successful!`

---

## Step 7: Deploy to Railway (20 minutes)

### 7.1 Install Railway CLI

```bash
npm install -g @railway/cli
```

### 7.2 Login to Railway

```bash
railway login
```

This opens browser for authentication.

### 7.3 Initialize Project

```bash
railway init
```

Choose "Create new project" and give it a name.

### 7.4 Add PostgreSQL Database

```bash
railway add postgresql
```

This provisions a PostgreSQL database.

### 7.5 Get Database URL

```bash
railway variables
```

Copy the `DATABASE_URL` value.

### 7.6 Set Environment Variables

```bash
railway variables set WHATSAPP_API_URL=https://graph.facebook.com/v18.0
railway variables set WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
railway variables set WHATSAPP_ACCESS_TOKEN=your_access_token
railway variables set WHATSAPP_VERIFY_TOKEN=your_verify_token
railway variables set SECRET_KEY=your_secret_key
```

### 7.7 Create Procfile

Create `Procfile` in project root:

```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### 7.8 Deploy

```bash
railway up
```

Wait 2-3 minutes for deployment.

### 7.9 Get Your Public URL

```bash
railway domain
```

Your app is now live at `https://your-app.railway.app`

---

## Step 8: Configure WhatsApp Webhook (10 minutes)

### 8.1 Go to WhatsApp Configuration

In Meta Developer dashboard:
1. Go to WhatsApp → Configuration
2. Find "Webhook" section
3. Click "Edit"

### 8.2 Enter Webhook Details

- **Callback URL**: `https://your-app.railway.app/api/webhook`
- **Verify Token**: Same as `WHATSAPP_VERIFY_TOKEN` in your .env

Click "Verify and Save"

### 8.3 Subscribe to Webhook Fields

Check these boxes:
- ☑️ messages

Click "Save"

### 8.4 Test Webhook

1. In WhatsApp Configuration, find "Phone numbers"
2. Send test message from your WhatsApp to test number
3. Check Railway logs:

```bash
railway logs
```

You should see incoming webhook logged.

---

## Step 9: Test WhatsApp Bot (5 minutes)

1. Open WhatsApp on your phone
2. Send message to your test number: `Hi`
3. Bot should respond with welcome message

If not working:
- Check Railway logs for errors
- Verify webhook URL is correct
- Ensure all environment variables are set

---

## Common Issues & Solutions

### Issue: "Module not found" error

**Solution**: Ensure you're in virtual environment

```bash
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### Issue: "Database connection refused"

**Solution**: Check PostgreSQL is running

```bash
# Check status
pg_isready

# Start PostgreSQL
# Mac: brew services start postgresql
# Linux: sudo service postgresql start
```

### Issue: "Port 8000 already in use"

**Solution**: Kill process or use different port

```bash
# Find process
lsof -ti:8000

# Kill it
kill -9 <PID>

# Or use different port
uvicorn app.main:app --port 8001
```

### Issue: WhatsApp webhook not receiving messages

**Solution**: 
1. Ensure Railway app is deployed and running
2. Check webhook URL is correct (must be HTTPS)
3. Verify `WHATSAPP_VERIFY_TOKEN` matches in both places
4. Check Railway logs for errors

---

## Next Steps

Now that your foundation is working:

1. **Add Models**: Copy models from Python_Implementation_Guide.md
2. **Add WhatsApp Service**: Implement WhatsApp message sending
3. **Add Message Router**: Handle incoming messages
4. **Add Wallet System**: Implement credit/debit operations
5. **Add Games**: Implement Lucky Wheel, Color Game, etc.

Refer to the detailed Python_Implementation_Guide.md for complete code.

---

## Development Workflow

### Daily Workflow

```bash
# Start day
cd betting-platform
source venv/bin/activate

# Pull latest changes (if team)
git pull

# Start server
uvicorn app.main:app --reload

# Run tests
pytest

# End day - commit changes
git add .
git commit -m "Description of changes"
git push
```

### Testing Workflow

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_wallet.py

# Run with coverage
pytest --cov=app tests/

# Run with verbose output
pytest -v
```

### Database Workflow

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# Check current version
alembic current
```

---

## Project Milestones

- ✅ **Week 1**: Foundation (WhatsApp + Database + User Registration)
- 🔄 **Week 2**: Wallet System (Credit/Debit + Transactions)
- 📅 **Week 3-4**: Games (4 games + Betting Engine)
- 📅 **Week 4-5**: Admin Dashboard (React + API)
- 📅 **Week 5-6**: Testing & Beta (50-300 users)

---

## Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **SQLAlchemy Tutorial**: https://docs.sqlalchemy.org/en/20/tutorial/
- **WhatsApp Business API**: https://developers.facebook.com/docs/whatsapp
- **Railway Docs**: https://docs.railway.app/
- **Python Best Practices**: https://docs.python-guide.org/

---

## Support & Troubleshooting

If you encounter issues:

1. Check the logs: `railway logs` or local terminal output
2. Verify environment variables: `railway variables`
3. Test database connection: `python test_db.py`
4. Review FastAPI docs: http://localhost:8000/docs

---

**You're now ready to start building! Proceed with Phase 1 implementation from the detailed guide.**

Good luck! 🚀
