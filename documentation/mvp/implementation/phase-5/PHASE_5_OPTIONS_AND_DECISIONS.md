# Phase 5: Options, Trade-offs, and Recorded Decisions

**MyKasiBets — Multi-channel merge**  
**Version:** 1.0  

This document captures **alternatives considered**, **trade-offs**, and **decisions locked for execution**. Implementation must align with these unless formally revised.

---

## 1. Webhook URL strategy

### Option A — Separate URL paths (chosen)

**Description:** Expose distinct routes, e.g. `/webhook/whatsapp` and `/webhook/telegram`, each with handlers appropriate to Meta vs Telegram.

| Pros | Cons |
|------|------|
| Clear routing and logging; no ambiguous JSON parsing | Requires updating Meta callback URL and Telegram `setWebhook` after deploy |
| WhatsApp GET verification stays isolated from Telegram GET health | Nginx must proxy both paths (two `location` blocks or prefix match) |

### Option B — Single `/webhook` POST with payload detection

**Description:** One POST handler branches on payload shape (`whatsapp_business_account` vs Telegram `update_id` / `message`).

| Pros | Cons |
|------|------|
| One public POST URL | Misclassification risk; mixed security headers (Meta signature vs Telegram secret token) |
| | GET cannot serve both Meta verification and Telegram health on one path without extra branching |

**Decision:** **Option A.** Use separate paths; exact strings MUST be documented in deployment runbooks and match nginx configuration.

---

## 2. Message router refactor depth

### C1 — Thin channel adapters + shared orchestration (target)

**Description:** Introduce a channel context (identifiers + outbound messaging port) and a single shared module for conversation/game flows (`_handle_state_flow`, `_handle_main_menu`, game calls).

| Pros | Cons |
|------|------|
| Aligns with ports/adapters; easier testing | Higher upfront extraction effort from ~3.4k-line file |

### C2 — Two router classes + shared mixin

**Description:** `WhatsAppMessageRouter` and `TelegramMessageRouter` share a mixin or base class for duplicated logic.

| Pros | Cons |
|------|------|
| Faster partial merge | Risk of duplicated game rules over time |

### C3 — Single router with `if channel:`

**Description:** One class with channel conditionals throughout.

| Pros | Cons |
|------|------|
| Minimal structural change | Unmaintainable at current file size |

**Decision:** **C1 is the target end-state.** The team MAY land C2 incrementally in the first merge milestone, with a tracked follow-up to extract shared orchestration (no permanent fork of game logic).

---

## 3. Cross-channel identity and wallets

**Options:**

- **Separate users per channel (chosen):** A WhatsApp user and a Telegram user are **distinct** rows with distinct wallets unless a future “account linking” feature is built. No automatic merge in Phase 5.

- **Single wallet when both identifiers exist:** Would require explicit linking rules, UX, and data migration strategy (out of scope for Phase 5).

**Decision:** **Separate users per channel by default.** Document “account linking” as future work.

---

## 4. Unified user schema (constraints)

**Decision:**

- Add `telegram_chat_id` (nullable, unique index) to `users`.
- Make `phone_number` nullable where required for Telegram-only rows.
- Enforce **invariant:** at least one of `phone_number` or `telegram_chat_id` is non-null (database check constraint **or** application-level validation with documented test coverage—team chooses based on migration risk).

---

## 5. Canonical repository

**Decision:** **`my-kasi-bet` is the canonical repository** unless the organization directs otherwise. Changes from `my-kasi-bet-telegram` are merged **into** this tree (not the reverse), preserving Alembic history from the WhatsApp baseline and appending new revisions.

---

## 6. Summary table

| Topic | Decision |
|-------|----------|
| Webhook paths | Separate paths (Option A); exact paths in nginx + provider consoles |
| Router structure | Target C1; allow incremental C2 |
| Identity | Separate users per channel; no auto-merge |
| User table | `telegram_chat_id` + nullable `phone_number` + at-least-one-identifier rule |
| Codebase | `my-kasi-bet` as primary merge target |

---

**Next document:** [PHASE_5_BACKEND_MERGE_PLAN.md](./PHASE_5_BACKEND_MERGE_PLAN.md)
