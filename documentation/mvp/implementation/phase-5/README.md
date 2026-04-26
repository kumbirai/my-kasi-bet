# Phase 5: WhatsApp + Telegram Unified Codebase

This folder contains **execution plans** for merging the WhatsApp-focused application (`my-kasi-bet`) with the Telegram variant (`my-kasi-bet-telegram`) into a **single** FastAPI deployment: shared PostgreSQL database, shared game engine, distinct webhook entry points, and one admin dashboard.

## Document index

| Document | Audience | Purpose |
|----------|----------|---------|
| [PHASE_5_OPTIONS_AND_DECISIONS.md](./PHASE_5_OPTIONS_AND_DECISIONS.md) | Tech lead, architect | Recorded options, trade-offs, and locked decisions (webhook URLs, identity model, refactor depth) |
| [PHASE_5_BACKEND_MERGE_PLAN.md](./PHASE_5_BACKEND_MERGE_PLAN.md) | Backend engineers | Ordered tasks: schema, migrations, services, webhooks, message orchestration, games, tests, nginx |
| [PHASE_5_ADMIN_DASHBOARD_MERGE_PLAN.md](./PHASE_5_ADMIN_DASHBOARD_MERGE_PLAN.md) | Frontend + API engineers | Unified admin API contracts, React user management, regression checklist |
| [PHASE_5_EDGE_CASES_AND_RUNBOOKS.md](./PHASE_5_EDGE_CASES_AND_RUNBOOKS.md) | DevOps, QA, on-call | Webhook behavior, migration rollback, provider URL updates, monitoring |

Read **OPTIONS_AND_DECISIONS** first, then **BACKEND_MERGE**, then **ADMIN_DASHBOARD**, then **EDGE_CASES** for operational detail.

## Dependency on prior phases

Phase 5 assumes **Phase 4** is complete or stable: admin JWT, admin APIs, and React admin shell exist. The merge **extends** models and admin surfaces; it does not replace Phase 4 scope.

**Prerequisites (technical):**

- Primary codebase branch agreed (typically `my-kasi-bet` as canonical repository).
- Access to both repositories for diff and cherry-pick.
- WhatsApp Business API and Telegram Bot credentials available for staging.

## Roles and responsibilities

| Role | Responsibilities |
|------|------------------|
| **Tech lead / architect** | Approves decisions document, resolves merge conflicts in `message_router.py` strategy |
| **Backend** | Migrations, `User` model, `UserService`, webhook modules, orchestration merge, `telegram_service`, tests |
| **Frontend** | Users table columns, search UX, copy for dialogs when phone is absent |
| **DevOps** | Nginx paths, env vars, Telegram `setWebhook`, Meta callback URL, TLS, rollout |
| **QA** | Test matrix in backend plan, regression on admin flows, webhook contract tests |

The team assigns **owners and dates** in each sprint; these documents are the scope backbone.

## Definition of done (Phase 5)

Phase 5 is **complete** when all of the following are true:

1. **Single deployment** runs one backend process with **both** `/webhook/whatsapp` and `/webhook/telegram` (or the exact paths recorded in OPTIONS_AND_DECISIONS) reachable behind nginx.
2. **One PostgreSQL schema** supports WhatsApp users (phone present) and Telegram users (`telegram_chat_id` present) with **no automatic cross-channel wallet merge** (see decisions doc).
3. **Game engine** exists in one tree; drift between repos (e.g. `football_yesno.py`) is resolved and covered by tests or explicit sign-off.
4. **Admin dashboard** lists users with both identifiers where applicable; search works for at least user id, phone substring, and telegram chat id as specified in the admin merge plan.
5. **Automated tests** cover webhook verification (WhatsApp), Telegram POST happy path, and critical user-creation paths per channel.
6. **Runbooks** exist for migration rollback and provider webhook URL updates (see EDGE_CASES doc).

## Estimated effort (indicative)

Merge scope is **large** primarily due to `app/services/message_router.py` (~3.4k lines): schedule dedicated merge review time. Documentation does not prescribe calendar days; the team estimates sprints after backlog refinement.

## Related documentation

- [Phase 4 implementation plan](../phase-4/PHASE_4_IMPLEMENTATION_PLAN.md) — Admin dashboard and API baseline
- Repository roots: `my-kasi-bet` (WhatsApp), `my-kasi-bet-telegram` (Telegram reference)

---

**Start here:** [PHASE_5_OPTIONS_AND_DECISIONS.md](./PHASE_5_OPTIONS_AND_DECISIONS.md)
