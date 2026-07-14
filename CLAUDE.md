# MyKasiBets — Agent & IDE Instructions

MyKasiBets is a CM Solutions project: a Telegram betting platform MVP for South Africa (Python/FastAPI, PostgreSQL, Redis, React admin dashboard). The WhatsApp channel was removed during Phase 5 — Telegram is now the sole channel (users are identified by `telegram_chat_id`).

## Obsidian Handoff Protocol (REQUIRED)

The Obsidian vault folder `projects/my-kasi-bet/` is the single source of truth for cross-session continuity. Every agent and IDE session MUST follow this protocol.

### Before starting any work

1. **Read the handoff note** via the `obsidian` MCP tool:
   ```
   mcp__obsidian__read_note("projects/my-kasi-bet/agent-handoff.md")
   ```
   This tells you what was just done and what needs to happen next. Do not skip this step.

2. **Read the orientation note** for architecture, stack, and locations:
   ```
   mcp__obsidian__read_note("projects/my-kasi-bet/overview.md")
   ```

3. **Search Memento** for prior decisions on the component you are touching:
   ```
   mcp__memento__memento_search("my-kasi-bet <component>")
   ```

### After completing work (before ending the session)

Append a session entry to `projects/my-kasi-bet/agent-handoff.md` using the `obsidian` MCP tool:

```
mcp__obsidian__append_note(
  path = "projects/my-kasi-bet/agent-handoff.md",
  content = """
## Session YYYY-MM-DD — <branch> — <agent/IDE>

### Done
- <bullet per meaningful change>

### Left uncommitted / in progress
- <list any modified/untracked files not yet committed>

### Blockers
- <anything that would block the next session>
"""
)
```

Then update the "Open items / next steps" table in the same note (✅ Done / 🔄 In progress / ❌ Blocked / ❓ Not started).

Also store durable facts in Memento (architecture decisions, bug root causes, verified fixes, conventions) via `mcp__memento__memento_remember`, tagged with project `my-kasi-bet`.

---

## Project context

- **Repository:** `/home/coach/cursor/python/my-kasi-bet` (branch `main`)
- **Canonical requirements & plans:** repo `documentation/` folder — the vault mirrors orientation only; **repo wins on conflict**
  - `documentation/requirements/` — business & implementation guides (SA online gambling, MVP execution plan)
  - `documentation/mvp/implementation/phase-1..5/` — phased implementation plans
  - `documentation/telegram/` — Telegram payments research
- **Current stage:** Phase 5 — Telegram-only. The WhatsApp app and Telegram variant were consolidated into one FastAPI deployment and WhatsApp was then removed (single channel, shared game engine, one admin dashboard). The next build target is the Telegram Mini App game front-end — see `documentation/mvp/implementation/phase-5/PHASE_5_TELEGRAM_MINIAPP.md`.

## Architecture conventions

- FastAPI app in `app/` — routers in `app/api/`, SQLAlchemy models in `app/models/`, Pydantic schemas in `app/schemas/`, business logic in `app/services/`.
- Incoming Telegram messages flow through `app/services/message_router.py`; `telegram_service.py` is the channel adapter — keep game/business logic channel-agnostic so a future channel (or the Mini App HTTP surface) can reuse the same engine.
- Games live in `app/services/games/` (`color_game`, `football_yesno`, `lucky_wheel`, `pick_3`); the shared game engine is channel-agnostic.
- Money movements go through `wallet_service` / `transaction` records — never mutate wallet balances directly.
- Schema changes via Alembic migrations (`alembic/`), never ad-hoc DDL.
- Admin dashboard is React (Vite + Tailwind) in `admin-dashboard/`, served behind nginx; admin auth is JWT (Phase 4).

## Runtime

- Docker Compose stack: `kasi-postgres` (Postgres 15), `kasi-redis` (Redis 7), `kasi-backend`, `kasi-db-init`, `kasi-admin-dashboard`, `kasi-nginx`, `kasi-certbot` (Let's Encrypt).
- Tests: `pytest` (async supported) in `tests/`.
