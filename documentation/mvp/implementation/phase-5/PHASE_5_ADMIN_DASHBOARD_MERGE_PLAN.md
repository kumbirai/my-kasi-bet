# Phase 5: Admin Dashboard Merge Plan

**MyKasiBets — Unified admin API and React UI**  
**Version:** 1.0  

**Prerequisites:** Backend schema and `User` model support both `phone_number` and `telegram_chat_id` per [PHASE_5_BACKEND_MERGE_PLAN.md](./PHASE_5_BACKEND_MERGE_PLAN.md) and [PHASE_5_OPTIONS_AND_DECISIONS.md](./PHASE_5_OPTIONS_AND_DECISIONS.md).

This phase runs **after** the backend exposes unified user fields and stable identifiers.

---

## 1. Objectives

1. One **admin API** contract for user list/detail that includes **both** optional identifiers.
2. **Search** that works for operators regardless of channel (user id, phone substring, telegram chat id).
3. **React Users page** that displays and confirms actions without assuming phone is always present.
4. **Bets and analytics** surfaces show a **best-available** user label (phone or `telegram_chat_id`).

---

## 2. Affected backend files (canonical repo)

| File | Purpose |
|------|---------|
| `app/api/admin_users.py` | List/detail schemas, search filters, block/unblock payloads |
| `app/api/admin_bets.py` | User display fields on bet rows |
| `app/api/admin_analytics.py` | Any user-facing aggregates (if applicable) |
| `app/schemas/` | Shared Pydantic models if extracted |

**Reference:** `my-kasi-bet-telegram/app/api/admin_users.py` (Telegram-oriented fields and search).

---

## 3. API contract changes

### 3.1 User list and detail

**Unify** response models to include:

- `id: int`
- `telegram_chat_id: Optional[str]`
- `phone_number: Optional[str]`
- `is_active`, `is_blocked`, `created_at`, wallet balance, aggregates as today

**Rules:**

- Never require both identifiers; either may be `null` depending on channel.
- **Display name for logs** (optional follow-up): derive from `phone_number` or `telegram_chat_id` or `"user:{id}"`.

### 3.2 Search behavior

Merge behaviors from both repos:

| Source repo | Prior behavior |
|-------------|----------------|
| WhatsApp | `phone_number` substring search |
| Telegram | Numeric `search` → exact user `id`; non-numeric → no match |

**Target behavior (Phase 5):**

1. If `search` is **numeric** (all digits): match `User.id` **or** exact `telegram_chat_id` string **or** phone containing digits (product decision: prefer exact id first).
2. If `search` is **non-numeric**: match `phone_number` **contains** (case-insensitive if applicable) **or** `telegram_chat_id` **contains**.

Document exact SQL/ORM filters in the PR; add tests for edge cases (leading zeros, partial phone).

**Owner:** Backend + product confirmation on “numeric only” vs “substring” for Telegram ids.

---

## 4. Block / unblock and audit

1. **Block user** and **unblock** endpoints: keep existing auth and audit logging.
2. **Audit `details`**: include both `phone_number` and `telegram_chat_id` when present (merge telegram repo’s richer `details` where applicable).
3. **Confirm dialogs** in UI must not reference only `phone_number` (see frontend section).

---

## 5. Admin bets and analytics

1. **`admin_bets.py`:** Replace or supplement `user_phone` with **display label** logic:
   - Prefer `phone_number` if set; else `telegram_chat_id`; else `"Unknown"` or `"User {id}"`.
2. **Analytics:** Any breakdown by “channel” is **out of scope** unless trivial (e.g. derived from `phone_number` IS NOT NULL vs `telegram_chat_id` IS NOT NULL); otherwise backlog.

---

## 6. Frontend (`admin-dashboard/`)

### 6.1 Files

| File | Changes |
|------|---------|
| `src/pages/Users.jsx` | Columns: `phone_number`, `telegram_chat_id`; search placeholder; confirm copy |
| `src/services/userService.js` | No breaking change if API stays backward-compatible; adjust if field names changed |
| `src/context/AuthContext.jsx` | No change unless API base path changes |

### 6.2 Users table

- Add column **Telegram chat ID** (show `—` when null).
- Keep **Phone** column (show `—` when null).
- Optional: badge **Channel** derived from which field is set (WA / TG / both—only “both” if linking exists later).

### 6.3 Search and copy

- Placeholder: e.g. “Search by user ID, phone, or Telegram chat ID…”
- Block/unblock confirmations: use **user id** plus best-available identifier, e.g. `User #123 (phone: …)` or `User #123 (Telegram: …)`.

### 6.4 CORS (optional)

If remote admin testing via ngrok is required, port `allow_origin_regex` from `my-kasi-bet-telegram/app/main.py` into canonical `main.py` (see backend plan). Coordinate with DevOps.

---

## 7. Regression checklist (manual QA)

| # | Check | Pass criteria |
|---|--------|----------------|
| 1 | Login | Admin JWT works unchanged |
| 2 | User list pagination | Loads; no console errors |
| 3 | Search by phone (WA user) | Finds user |
| 4 | Search by Telegram id (TG user) | Finds user |
| 5 | Search by internal id | Finds user |
| 6 | Block TG-only user | Confirm dialog sensible; blocked flag updates |
| 7 | Bets list | User column shows label for WA and TG users |

---

## 8. Definition of done (admin slice)

- [ ] Admin API returns both fields on list/detail.
- [ ] Search documented and tested for at least three cases (id, phone, telegram id).
- [ ] Users page shows both columns and safe copy.
- [ ] Bets (and any user-linked report) use best-available label.

---

**Next document:** [PHASE_5_EDGE_CASES_AND_RUNBOOKS.md](./PHASE_5_EDGE_CASES_AND_RUNBOOKS.md)
