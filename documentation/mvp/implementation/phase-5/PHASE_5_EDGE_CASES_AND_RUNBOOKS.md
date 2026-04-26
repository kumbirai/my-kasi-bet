# Phase 5: Edge Cases, Runbooks, and Operations

**MyKasiBets — Webhooks, migrations, provider configuration**  
**Version:** 1.0  

Companion to [PHASE_5_BACKEND_MERGE_PLAN.md](./PHASE_5_BACKEND_MERGE_PLAN.md) and [PHASE_5_OPTIONS_AND_DECISIONS.md](./PHASE_5_OPTIONS_AND_DECISIONS.md).

---

## 1. Webhook behavior matrix

| Channel | Event | Expected HTTP | Notes |
|---------|--------|----------------|-------|
| WhatsApp | GET verify, correct token | 200, plain-text challenge | Meta subscription setup |
| WhatsApp | GET verify, wrong token | 403 | Log warning |
| WhatsApp | POST, valid text message | 200, process | May return body with `status: error` on internal failure to limit retries (follow existing `webhook.py` pattern) |
| WhatsApp | POST, non-text | 200, ignore | Document product limitation |
| Telegram | GET | 200, `{ "status": "ok" }` | Health / URL existence |
| Telegram | POST, no `message` | 200, ignore | Callback queries, edits, etc. out of scope |
| Telegram | POST, no `text` | 200, ignore | Stickers, photos |
| Telegram | POST, valid text | 200, process | |
| Telegram | POST, invalid JSON | 200 + error body (if existing pattern) | Avoid retry storms |

**Logging:** Include path prefix (`/webhook/whatsapp` vs `/webhook/telegram`) in structured logs for correlation.

---

## 2. Identity and data edge cases

| Case | Behavior |
|------|----------|
| WhatsApp user | `phone_number` set; `telegram_chat_id` null |
| Telegram user | `telegram_chat_id` set; `phone_number` null |
| Same human on both apps | **Two rows, two wallets** in Phase 5 (per decisions doc); support must not assume one account |
| Unique constraint on phone | Empty string must be rejected or normalized to NULL (team decision) |
| Duplicate webhook delivery | Idempotency not guaranteed; rely on message id + business rules where implemented |

---

## 3. Game engine and state

| Case | Mitigation |
|------|------------|
| `message_router` merge leaves drift | File-by-file diff in `app/services/games/`; sign-off list |
| In-memory `user_states` lost on restart | Document existing limitation; users type `menu` to recover; Redis backlog optional |
| Non-text commands | Ignored at webhook; no change unless product expands |

---

## 4. Database migration runbook

### 4.1 Pre-migration

1. **Backup:** Full PostgreSQL dump + verify restore on staging.
2. **Freeze:** Avoid schema migrations during backup window.
3. **Review:** Alembic revision chain: `001` → new `002` (or next id).

### 4.2 Execute

1. Deploy backend image that includes new revision **before** running upgrade (or run upgrade with migration container as in existing docker-compose pattern).
2. Run `alembic upgrade head`.
3. Smoke: existing WhatsApp users still have non-null `phone_number` and null `telegram_chat_id`.

### 4.3 Rollback

1. **Application rollback:** Deploy previous backend image if new code fails.
2. **Schema rollback:** `alembic downgrade -1` **only** if downgrade path is tested and safe; dropping columns may lose Telegram data if already written.
3. **Production rule:** If Telegram traffic has created users, **do not** downgrade without data export.

**Document:** Actual revision ids and commands in deployment ticket.

---

## 5. Provider URL and webhook updates

### 5.1 Meta (WhatsApp)

1. Open Meta Developer / WhatsApp configuration.
2. Set **Callback URL** to `https://<host>/webhook/whatsapp` (exact path per deployment).
3. Set **Verify token** to match `WHATSAPP_VERIFY_TOKEN`.
4. Re-subscribe webhooks if required.
5. Verify: Meta sends GET; logs show 200 + challenge.

### 5.2 Telegram

1. Call `setWebhook` with `https://<host>/webhook/telegram` (or chosen path).
2. Recommended in production: set `secret_token` in `setWebhook` and set the same value in `TELEGRAM_WEBHOOK_SECRET`; the backend validates `X-Telegram-Bot-Api-Secret-Token` on POST when secret is configured.
3. Verify: `getWebhookInfo` shows correct URL and last error empty.

### 5.3 DNS and TLS

- Certificate must cover public hostname; Telegram requires HTTPS for webhooks in production.

---

## 6. Monitoring and alerts

| Signal | Action |
|--------|--------|
| Spike in 403 on WA GET | Verify token mismatch or attack |
| Spike in 5xx on webhooks | Rollback candidate; check DB connectivity |
| Telegram “chat not found” logs | User blocked bot or invalid chat id; expected occasionally |

---

## 7. Security (fast-follow)

| Item | Phase 5 scope |
|------|----------------|
| Telegram webhook secret header | Optional; document in backlog if not implemented |
| Meta signature validation | Follow existing codebase; enhance if missing |

---

## 8. Incident checklist (webhooks down)

1. Confirm nginx routes to backend for **both** paths.
2. Confirm env vars: `WHATSAPP_*`, `TELEGRAM_BOT_TOKEN`.
3. Check provider dashboards for delivery errors.
4. Tail `logs/app.log` (or container logs) filtered by webhook path.

---

**Index:** [README.md](./README.md)
