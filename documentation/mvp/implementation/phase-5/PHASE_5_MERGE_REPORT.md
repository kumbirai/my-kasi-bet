# Phase 5 merge report

## Canonical reference

Record at release time in your PR or deployment ticket:

- **Branch** and **commit SHA** from your git remote.

## Merged areas

| Area | Summary |
|------|---------|
| Schema | Alembic `002_telegram_mc`: `telegram_chat_id`, nullable `phone_number`, CHECK `ck_users_phone_or_telegram` |
| Webhooks | `app/api/whatsapp_webhook.py`, `app/api/telegram_webhook.py`; mounted at `/webhook/whatsapp`, `/webhook/telegram` |
| Router | `MessageRouter.route_message` (WhatsApp), `route_message_telegram` (Telegram); shared `_send_to_user`; `start` global command |
| Games | `football_yesno.py`: match settlement notifies WhatsApp or Telegram by user row |
| Admin | `admin_users` search + optional identifiers; `admin_bets` best-available user label; `Users.jsx` columns and copy |
| Security | Optional `TELEGRAM_WEBHOOK_SECRET` with `X-Telegram-Bot-Api-Secret-Token` validation (constant-time) on Telegram POST |
| CORS | Default `CORS_ORIGIN_REGEX` for ngrok HTTPS tunnels; override or clear via `CORS_ORIGIN_REGEX` env |

## Public webhook paths

- WhatsApp (Meta callback): `https://<host>/webhook/whatsapp`
- Telegram (`setWebhook`): `https://<host>/webhook/telegram`

## Environment variables

| Variable | Notes |
|----------|--------|
| `TELEGRAM_BOT_TOKEN` | Required for Telegram outbound API calls when handling Telegram users |
| `TELEGRAM_WEBHOOK_SECRET` | Optional in dev; in production set to match Telegram `setWebhook` `secret_token`; enforces header on POST |
| `CORS_ORIGIN_REGEX` | Optional; default allows `*.ngrok-free.app` / `*.ngrok.io`; set empty to disable extra regex |
| `WHATSAPP_*` | Unchanged |

## Nginx

`location /webhook` proxies to the backend with standard headers; URI prefix `/webhook` matches `/webhook/whatsapp` and `/webhook/telegram`.

## Provider configuration

| Provider | Action |
|----------|--------|
| Meta WhatsApp | Set callback URL to `https://<host>/webhook/whatsapp`; verify token matches `WHATSAPP_VERIFY_TOKEN` |
| Telegram | `setWebhook` URL `https://<host>/webhook/telegram`; if using `secret_token`, set `TELEGRAM_WEBHOOK_SECRET` to the same value |
| TLS | Certificate must cover the public hostname |

## Tests

```bash
.venv/bin/python -m pytest tests/test_webhook.py tests/test_user_service_channel.py -v
.venv/bin/python -m pytest tests/ -v
```

## Games merge log

- `football_yesno.py`: settlement notifications branch on `user.telegram_chat_id` vs `user.phone_number`; both channels supported.

## Architecture note (C1)

Shared game and menu logic lives in `MessageRouter` with two entry methods (`route_message` / `route_message_telegram`) and `_send_to_user` for outbound delivery. Further extraction to a dedicated outbound port type is optional if the codebase grows.
