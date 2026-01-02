# MyKasiBets WhatsApp Betting Platform MVP

A WhatsApp-based betting platform MVP built with Python, FastAPI, and PostgreSQL.

## Overview

This is Phase 1 of the WhatsApp Betting Platform MVP, focusing on foundation infrastructure including:
- FastAPI backend server
- PostgreSQL database with User and Wallet models
- WhatsApp Business API integration
- Message routing and user registration
- Webhook endpoints for receiving messages

## Technology Stack

- **Backend**: Python 3.10+ with FastAPI
- **Database**: PostgreSQL 14+ with SQLAlchemy ORM
- **WhatsApp**: WhatsApp Business API (Meta)
- **Authentication**: JWT (PyJWT)
- **Testing**: pytest with async support

## Prerequisites

Before starting, ensure you have:
- Python 3.10+ installed
- PostgreSQL 14+ installed and running
- WhatsApp Business API account with credentials
- Git installed

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/kumbirai/my-kasi-bet.git
cd my-kasi-bet
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

Edit `.env` with your actual values:
- WhatsApp Business API credentials
- Database connection string
- Secret keys

### 5. Create Database

```bash
# Connect to PostgreSQL
PGPASSWORD=secret psql -h localhost -p 5432 -U postgres -d postgres

# Create database
CREATE DATABASE betting_db;

# Exit
\q
```

### 6. Run Database Migrations

```bash
alembic upgrade head
```

### 7. Start the Server

```bash
uvicorn app.main:app --reload --port 8000
```

The server will start on `http://localhost:8000`

## Docker Compose

### Build and Start All Services

```bash
docker compose build --no-cache
docker compose up -d
```

### Build and Start Specific Service

```bash
docker compose build --no-cache admin-dashboard
docker compose up -d admin-dashboard
```

## API Documentation

Once the server is running, access:
- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## Project Structure

```
my-kasi-bet/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app entry point
│   ├── config.py               # Configuration management
│   ├── database.py             # Database connection
│   ├── models/                 # SQLAlchemy models
│   ├── schemas/                 # Pydantic schemas
│   ├── services/               # Business logic services
│   ├── api/                    # API routes
│   └── utils/                   # Utility functions
├── alembic/                    # Database migrations
├── tests/                      # Test files
├── logs/                       # Application logs
└── requirements.txt           # Python dependencies
```

## Development

### Running Tests

```bash
pytest
```

With coverage:

```bash
pytest --cov=app --cov-report=html
```

### Code Quality

This project follows:
- Clean Code principles
- Domain-Driven Design (DDD)
- Hexagonal Architecture
- Full type hints
- Comprehensive error handling

## Environment Variables

See `.env.example` for all required environment variables.

## License

Proprietary - All rights reserved

## Support

For issues or questions, please contact the development team.
