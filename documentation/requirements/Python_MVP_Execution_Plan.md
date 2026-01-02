WhatsApp Betting Platform MVP

Technical Execution Plan - Python Edition

**6-Week Development Sprint**

Prepared for:

**Kumbirai Mundangepfupfu**

*Software Solutions Architect*

Executive Summary

This execution plan provides a day-by-day technical roadmap for building
a WhatsApp-based betting platform MVP over 6 weeks using Python/FastAPI
backend with WhatsApp Business API integration.

Project Goals

-   Build fully functional WhatsApp betting platform using Python

-   Support 4 simple games (Lucky Wheel, Color Game, Pick 3, Football
    Yes/No)

-   Implement wallet system with manual deposit/withdrawal

-   Create React admin dashboard for management

-   Test with 50-300 users in closed beta

Technology Stack & Architecture

Updated Technology Stack

  -----------------------------------------------------------------------
  **Component**           **Technology Choice**
  ----------------------- -----------------------------------------------
  Backend                 Python 3.10+ with FastAPI (high performance
                          async)

  Database                PostgreSQL 14+ (ACID transactions) + Redis
                          (caching)

  WhatsApp API            WhatsApp Business API (your existing account)

  ORM                     SQLAlchemy 2.0 (async support, transaction
                          management)

  Hosting                 Railway.app or Render (free tier for MVP)

  Admin Dashboard         React 18 + Tailwind CSS + Vite

  Authentication          JWT (JSON Web Tokens) via PyJWT

  Task Queue              Celery + Redis (async bet processing)
  -----------------------------------------------------------------------

System Architecture

**High-Level Architecture Overview:**

┌─────────────┐

│ WhatsApp │ ← User Interaction

└──────┬──────┘

│ HTTPS Webhook

▼

┌─────────────────────────────────────┐

│ Python FastAPI Backend Server │

│ ┌──────────────────────────────┐ │

│ │ Message Router & Parser │ │

│ └──────────┬───────────────────┘ │

│ │ │

│ ┌────────┼────────┬─────────┐ │

│ ▼ ▼ ▼ ▼ │

│ \[Auth\] \[Wallet\] \[Games\] \[Admin\] │

└─────────────┬───────────────────────┘

│

┌─────┴──────┐

▼ ▼

┌──────────┐ ┌────────┐

│PostgreSQL│ │ Redis │

└──────────┘ └────────┘

Why Python + FastAPI?

-   FastAPI: Modern, fast (high-performance) web framework with
    automatic API docs

-   Async Support: Native async/await for handling concurrent WhatsApp
    messages

-   SQLAlchemy: Powerful ORM with transaction management and connection
    pooling

-   Type Hints: Python type hints + Pydantic for data validation

-   Easy Deployment: Single requirements.txt, works great on
    Railway/Render

-   Rich Ecosystem: Excellent libraries for payments, crypto, data
    processing

Database Schema Design

Database schema remains identical - PostgreSQL with 8 core tables. Full
schema available in separate SQL file.

Core Tables Summary

1.  users - User accounts and authentication

2.  wallets - User balances with ACID guarantees

3.  transactions - Complete audit trail of all money movements

4.  bets - All betting activity and outcomes

5.  deposits - Deposit requests and approval workflow

6.  withdrawals - Withdrawal requests and processing

7.  admin_users - Admin accounts with role-based access

8.  game_rounds - Optional game outcome logging for audits

PHASE 1: Foundation (Week 1)

Goal: Set up Python FastAPI server, WhatsApp Business API integration,
PostgreSQL database, and basic user registration.

Day 1: Environment Setup & Project Structure

Project Initialization

**Create project structure:**

mkdir betting-platform

cd betting-platform

python -m venv venv

source venv/bin/activate \# On Windows: venv\\Scripts\\activate

**Create requirements.txt:**

fastapi==0.109.0

uvicorn\[standard\]==0.27.0

sqlalchemy==2.0.25

psycopg2-binary==2.9.9

pydantic==2.5.3

pydantic-settings==2.1.0

python-jose\[cryptography\]==3.3.0

passlib\[bcrypt\]==1.7.4

python-multipart==0.0.6

httpx==0.26.0

redis==5.0.1

celery==5.3.4

python-dotenv==1.0.0

**Install dependencies:**

pip install -r requirements.txt

Environment Configuration

**Create .env file:**

\# WhatsApp Business API

WHATSAPP_API_URL=https://graph.facebook.com/v18.0

WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id

WHATSAPP_ACCESS_TOKEN=your_access_token

WHATSAPP_VERIFY_TOKEN=your_verify_token_choose_random

\# Database

DATABASE_URL=postgresql://user:password@localhost:5432/betting_db

\# Redis

REDIS_URL=redis://localhost:6379/0

\# JWT Secret

SECRET_KEY=your-secret-key-min-32-characters-long-change-this

ALGORITHM=HS256

\# Server

PORT=8000

Complete 6-Week Timeline Overview

  -------------------------------------------------------------------------
  **Phase**      **Duration**       **Key Deliverables** **Success
                                                         Criteria**
  -------------- ------------------ -------------------- ------------------
  **Phase 1**    Week 1             Python FastAPI,      Bot receives and
                                    WhatsApp Business    responds to
                                    API, PostgreSQL,     WhatsApp messages
                                    User Registration    

  **Phase 2**    Week 2             Wallet System with   Users can
                                    SQLAlchemy,          add/withdraw
                                    Deposit/Withdrawal   money, all
                                    Flows                transactions
                                                         logged

  **Phase 3**    Week 3-4           4 Python Game        All games working,
                                    Engines + Betting    wins/losses
                                    Logic                calculated
                                                         accurately

  **Phase 4**    Week 4-5           React Admin          Admins manage
                                    Dashboard + FastAPI  users, approve
                                    Endpoints            deposits, settle
                                                         bets

  **Phase 5**    Week 5-6           Testing with pytest, 50-300 users, bugs
                                    Beta Testing         fixed, metrics
                                                         gathered

  **Phase 6**    End Week 6         Go/No-Go Decision    Decide: licensing,
                                                         partnerships, or
                                                         Phase 2 dev
  -------------------------------------------------------------------------

Python/FastAPI Advantages for This Project

1\. Rapid Development

Python\'s concise syntax and FastAPI\'s automatic API documentation
accelerate development. What takes 100 lines in Node.js takes 50 in
Python with type hints.

2\. Superior Data Handling

Python excels at numerical calculations (critical for betting odds,
wallet calculations). Decimal type prevents floating-point errors in
financial transactions.

3\. SQLAlchemy Power

Best-in-class ORM with transaction management, connection pooling, and
migration support. Prevents common database bugs.

4\. Future-Proof

Easy to add ML-based features later (fraud detection, recommendation
engine, odds optimization) using scikit-learn, pandas, numpy.

5\. Testing & Quality

pytest makes writing and running tests trivial. Type hints catch bugs
before runtime. FastAPI\'s dependency injection simplifies testing.

**Technical Execution Plan - Python Edition**

*Complete Python implementation code provided in separate detailed
guide.*

**Prepared for: Kumbirai Mundangepfupfu**

*Software Solutions Architect*

December 2025
