# MyKasiBets

MyKasiBets is a Telegram-first betting platform built with FastAPI, PostgreSQL,
Redis, React, and TypeScript. Users can interact through the Telegram bot or the
Telegram Mini App, while operators manage the platform through a separate admin
dashboard.

The repository is in active development. There are no legacy users or databases
to preserve. Alembic currently contains one rebased migration that creates the
complete Telegram-only schema from an empty PostgreSQL database.

## Current capabilities

- Telegram webhook with optional secret-token verification
- Telegram-only user registration and wallet ownership
- Chat flows for games, deposits, withdrawals, help, and account information
- Telegram Mini App served at `/app/`
- Signed Telegram `initData` validation on every authenticated Mini App request
- Server-authoritative Color Game outcomes and wallet settlement
- Persistent, user-scoped idempotency for safe result recovery after network loss
- Redis-backed play rate limiting and duplicate-request coordination
- Administrative recovery for stale, unsettled Mini App bets
- Admin authentication, user management, bet management, finance workflows,
  analytics, reports, and audit logs
- Fail-fast database migrations before the backend starts
- HTTPS termination and routing through Nginx

The Mini App currently exposes Color Game play. Its public configuration also
describes the other game engines, which remain available to the Telegram chat
flow until their Mini App interfaces are implemented.

## Architecture

```text
Telegram Bot API ──> /webhook/telegram ──> message router ──> game services
                                                               │
Telegram Mini App ──> /api/miniapp ──────> Color Game ──────────┤
                                                               ▼
                                                    BetService / WalletService
                                                               │
                                                    PostgreSQL + Redis guards

Admin browser ──────> / ─────────────────> admin API ───────────┘
```

All balance changes go through `WalletService` and `BetService`. Game outcomes
are generated and settled on the server. The browser only displays the result.

## Technology stack

- Python 3.11 and FastAPI 0.139
- PostgreSQL 15 and SQLAlchemy 2
- Redis 7
- Alembic migrations
- React 19, TypeScript, Vite, and Vitest for the Mini App
- React 19, Vite, and Tailwind CSS for the admin dashboard
- PyJWT and bcrypt for admin authentication
- Docker Compose, Nginx, and Certbot for deployment

## Repository layout

```text
my-kasi-bet/
├── app/                         # FastAPI application and domain services
│   ├── api/                     # Telegram, Mini App, and admin endpoints
│   ├── models/                  # SQLAlchemy models
│   ├── schemas/                 # API contracts
│   ├── services/                # Games, betting, wallets, and recovery
│   └── utils/                   # Telegram auth and security helpers
├── alembic/                     # Rebased Telegram-only database migration
├── admin-dashboard/             # Operator web application
├── miniapp/                     # Telegram Mini App
├── nginx/                       # HTTPS and service routing
├── scripts/                     # Database and administrator bootstrap scripts
├── tests/                       # Backend test suite
├── documentation/               # Product, implementation, and runbook material
├── requirements.txt             # Production Python dependencies
└── requirements-dev.txt         # Development and test dependencies
```

## Prerequisites

- Python 3.11+
- Node.js 20+
- PostgreSQL 15+
- Redis 7+
- Docker with the Compose plugin for the containerized workflow
- A Telegram bot created through BotFather
- A public HTTPS URL for Telegram webhooks and the Mini App

## Configuration

Copy the environment template and replace every production secret and public
URL:

```bash
cp .env.example .env
python -c "import secrets; print(secrets.token_hex(32))"
```

The main settings are:

| Variable | Purpose |
| --- | --- |
| `TELEGRAM_BOT_TOKEN` | Bot API token and Mini App signature secret |
| `TELEGRAM_WEBHOOK_SECRET` | Optional secret checked on Telegram webhook requests |
| `MINIAPP_URL` | Public HTTPS URL ending in `/app/` |
| `MINIAPP_INITDATA_MAX_AGE_SECONDS` | Maximum accepted age of signed Telegram data |
| `MINIAPP_RATE_LIMIT_PER_MIN` | Per-user limit for money-moving play requests |
| `MINIAPP_PENDING_BET_MAX_AGE_SECONDS` | Age at which an unsettled instant bet may be refunded |
| `DATABASE_URL` | SQLAlchemy PostgreSQL connection URL |
| `REDIS_URL` | Redis connection URL |
| `SECRET_KEY` | Admin JWT signing secret |
| `CORS_ORIGINS` | Comma-separated trusted browser origins |
| `INITIAL_ADMIN_EMAIL` | Optional administrator created during database initialization |
| `INITIAL_ADMIN_PASSWORD` | Matching bootstrap password, at least 12 characters |

`INITIAL_ADMIN_EMAIL` and `INITIAL_ADMIN_PASSWORD` must be configured together.
If both are empty, database initialization skips administrator creation safely.

## Docker Compose setup

Docker Compose is the preferred way to run the complete stack:

```bash
docker compose build
docker compose up -d
docker compose ps
```

Services start in dependency order. PostgreSQL must become healthy, `db-init`
must apply the Alembic migration successfully, and only then can the backend and
frontends start. A migration or administrator-bootstrap failure stops startup.

The Nginx routes are:

| Route | Service |
| --- | --- |
| `/` | Admin dashboard |
| `/app/` | Telegram Mini App |
| `/api/` | Backend API |
| `/webhook/telegram` | Telegram webhook |
| `/health` | Nginx health check |
| `/health/backend` | Backend health check |

The checked-in Nginx configuration expects valid Let's Encrypt certificates for
the configured production hostname. Update `nginx/nginx.conf` and provision its
certificate before deploying another hostname.

Useful commands:

```bash
docker compose logs -f kasi-backend
docker compose run --rm db-init
docker compose down
```

To discard all development data and replay the rebased migration from scratch:

```bash
docker compose down -v
docker compose up -d --build
```

## Local backend setup

Create an environment and install both production and test dependencies:

```bash
python -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
```

For processes running outside Docker, use host-accessible PostgreSQL and Redis
URLs in `.env`, for example:

```dotenv
DATABASE_URL=postgresql://postgres:secret@localhost:15432/postgres
REDIS_URL=redis://localhost:6379/0
```

Apply the schema and run the API:

```bash
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

API documentation is available at `http://localhost:8000/docs` and
`http://localhost:8000/redoc`.

## Frontend development

Run the Mini App:

```bash
cd miniapp
npm ci
npm run dev
```

Run the admin dashboard in another terminal:

```bash
cd admin-dashboard
npm ci
npm run dev
```

Set `VITE_API_BASE_URL=http://localhost:8000` when a frontend should call a
locally running backend directly.

## Telegram setup

Point Telegram at the public webhook after the HTTPS endpoint is available:

```bash
curl --request POST \
  "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/setWebhook" \
  --data-urlencode "url=https://your-domain.example/webhook/telegram" \
  --data-urlencode "secret_token=${TELEGRAM_WEBHOOK_SECRET}"
```

Configure the bot's menu button or Mini App through BotFather with the same
public URL assigned to `MINIAPP_URL`, such as
`https://your-domain.example/app/`.

## Database migrations

`alembic/versions/001_initial_migration.py` is the only migration head. It
creates the current Telegram-only schema, including required Telegram user IDs
and per-user bet idempotency keys.

Verify migration state with:

```bash
alembic heads
alembic current
alembic check
```

Do not use `Base.metadata.create_all()` or stamp over migration failures.
Alembic is the authoritative schema lifecycle.

## Verification

Backend:

```bash
pytest -q
python -m compileall -q app scripts alembic tests
```

Mini App:

```bash
cd miniapp
npm test -- --run
npm run lint
npm run build
npm audit --audit-level=high
```

Admin dashboard:

```bash
cd admin-dashboard
npm run lint
npm run build
npm audit --audit-level=high
```

Deployment configuration:

```bash
bash -n scripts/docker-init-db.sh
docker compose config --quiet
docker compose build kasi-backend miniapp admin-dashboard nginx
```

The current verified baseline is 163 passing backend tests with 3 explicitly
skipped tests, 5 passing Mini App tests, clean frontend lint and builds, zero npm
audit findings, and no known vulnerabilities in the production backend image.

## Further documentation

- `PRODUCT.md` describes the product model and constraints.
- `DESIGN.md` describes the visual system.
- `documentation/mvp/implementation/phase-5/PHASE_5_TELEGRAM_MINIAPP.md`
  contains the Mini App implementation handoff.
- `documentation/mvp/implementation/phase-5/PHASE_5_EDGE_CASES_AND_RUNBOOKS.md`
  covers recovery and operational behavior.
- `documentation/telegram/` contains Telegram platform references used during
  implementation.

## License

Proprietary. All rights reserved.
