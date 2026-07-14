# Phase 5 — Telegram Mini App (game front-end)

**Status:** Implementation in progress — milestones 1–4 complete; milestone 5
implemented and awaiting a real Telegram client rehearsal (2026-07-14)
**Owner:** _unassigned_
**Prereqs:** Phase 5 backend merge (shared DB + shared game engine) in place.

This document is a self-contained handoff. A developer or agent should be able to
build the Telegram Mini App from here without re-deriving the architecture. It
assumes familiarity with the repo conventions in the root `CLAUDE.md`
(message router, channel adapters, `wallet_service` money rule, Alembic).

---

## 1. What we are building and why

A **Telegram Mini App** is an ordinary web page (HTML/JS/CSS served over HTTPS)
that Telegram loads in an in-app WebView when the user taps a button. Telegram
injects a bridge, `window.Telegram.WebApp`, exposing the user identity, theme,
native buttons, and haptics.

The Mini App is a **richer front-end for the existing games** — a real spinning
wheel, tappable colour tiles, animated reveals — instead of chat text. It is a
**second caller into the same game engine**, alongside the existing Telegram
webhook. It does **not** re-implement any game or money logic.

```
                         ┌──────────────────────────────┐
  Telegram webhook  ────▶ │   message_router.py (chat)   │
                         │                              │
  Mini App (HTTP+JSON) ─▶ │   app/api/miniapp.py  ◀──────┼── NEW (bypasses router,
                         │        │                     │    sends structured JSON,
                         └────────┼─────────────────────┘    not free text)
                                  ▼
                    app/services/games/*  (unchanged)
                                  ▼
              BetService  ──▶  WalletService / Transaction  (unchanged)
```

### Non-negotiable boundaries (do not cross)

- **Money movement only through `WalletService`/`BetService`.** The Mini App never
  touches balances directly. It calls the same `Game.play()` the Telegram webhook calls.
- **Server is authoritative for every outcome.** All RNG lives in
  `app/services/games/*` using `secrets`. The client only *animates* a result the
  server already decided. Never compute win/loss, drawn number, or payout in JS.
- **Deposits/withdrawals ride the existing compliant provider rails** (the
  Paystack/Flutterwave path used elsewhere in the product). The Mini App only
  changes the *UI* of payment — it opens a hosted checkout / invoice and the
  existing provider webhook credits the wallet via `deposit_service`. It does not
  introduce a new settlement rail.
- **Channel-agnostic engine stays channel-agnostic.** Nothing Telegram-specific
  leaks into `app/services/games/`.

---

## 2. Confirmed service interfaces (build against these exact signatures)

These were read from the current codebase — match them precisely.

```python
# app/services/user_service.py
UserService.get_or_create_user_by_telegram(telegram_chat_id: str,
                                           username: Optional[str],
                                           db: Session) -> User
UserService.get_user_by_telegram_chat_id(telegram_chat_id: str, db) -> Optional[User]

# app/services/wallet_service.py   (NOTE arg order: user_id first, then db)
WalletService.get_balance(user_id: int, db: Session) -> Decimal      # raises WalletNotFoundError

# app/services/bet_service.py      (static; NOT async)
BetService.place_bet(user_id, bet_type: BetType, stake_amount: Decimal,
                     bet_data: dict, db, ip_address=None, user_agent=None) -> Bet
BetService.BET_LIMITS   # {BetType.X: (min Decimal, max Decimal)}

# app/services/games/*  (async; return (Bet, result_dict))
await ColorGame.play(user_id, stake_amount: Decimal, bet_data: dict, db) -> (Bet, dict)
await LuckyWheelGame.play(user_id, stake_amount: Decimal, bet_data: dict, db) -> (Bet, dict)
await Pick3Game.play(...)         # confirm signature before wiring
await FootballYesNoGame.play(...) # confirm signature before wiring
```

Game result dicts already contain everything the UI needs, e.g. Color Game:
`{selected_color, drawn_color, is_win, stake, payout, multiplier}`; Lucky Wheel:
`{selected_number, drawn_number, is_win, stake, payout, multiplier}`.

User model facts: `User.telegram_chat_id` is `String(32)` (Telegram numeric id
stored as string), plus `is_active` and `is_blocked` flags that **must** be
enforced on every play (see edge cases).

---

## 3. Backend work

### 3.1 New config (`app/config.py`)

Add settings (all read from env, no secrets in code):

```python
MINIAPP_URL: Optional[str] = None            # public HTTPS URL of the Mini App SPA
MINIAPP_INITDATA_MAX_AGE_SECONDS: int = 3600 # reject initData older than this
MINIAPP_RATE_LIMIT_PER_MIN: int = 30         # per-user /play cap
```

`TELEGRAM_BOT_TOKEN` already exists and is the HMAC key for initData verification.

### 3.2 initData verification — `app/utils/telegram_auth.py` (NEW, security spine)

Telegram provides `WebApp.initData`: a URL-encoded string with `user`,
`auth_date`, `query_id`, `hash`, and (newer clients) `signature`. The
client-side `initDataUnsafe` object is **untrusted**; the raw `initData` string
must be verified server-side on **every** request.

```python
import hmac, hashlib, time, json
from urllib.parse import parse_qsl
from app.config import settings

class InitDataError(Exception):
    """initData failed signature or freshness verification."""

def verify_init_data(init_data: str, max_age_seconds: int | None = None) -> dict:
    if not init_data:
        raise InitDataError("empty initData")
    if max_age_seconds is None:
        max_age_seconds = settings.MINIAPP_INITDATA_MAX_AGE_SECONDS

    try:
        pairs = dict(parse_qsl(init_data, strict_parsing=True, keep_blank_values=True))
    except ValueError as e:
        raise InitDataError(f"malformed initData: {e}") from e

    received_hash = pairs.pop("hash", None)
    if not received_hash:
        raise InitDataError("missing hash")

    # data_check_string: remaining pairs sorted by key, joined key=value with \n
    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(pairs.items()))

    # secret_key = HMAC_SHA256(key="WebAppData", msg=bot_token)
    secret_key = hmac.new(b"WebAppData",
                          settings.TELEGRAM_BOT_TOKEN.encode(),
                          hashlib.sha256).digest()
    computed = hmac.new(secret_key, data_check_string.encode(),
                        hashlib.sha256).hexdigest()

    if not hmac.compare_digest(computed, received_hash):
        raise InitDataError("bad signature")

    auth_date = int(pairs.get("auth_date", "0"))
    if auth_date <= 0 or (time.time() - auth_date) > max_age_seconds:
        raise InitDataError("stale or missing auth_date")

    if "user" not in pairs:
        raise InitDataError("no user in initData")  # e.g. opened without user context
    pairs["user"] = json.loads(pairs["user"])
    return pairs
```

**Three things people get wrong here — do not skip:**

1. The secret is `HMAC(key="WebAppData", msg=bot_token)` — the literal string is
   the *key*, the bot token is the *message*. Reversing them silently rejects
   every request.
2. Use `hmac.compare_digest` (constant-time). A `==` comparison is a timing hole.
3. Enforce `auth_date` freshness (`MINIAPP_INITDATA_MAX_AGE_SECONDS`). Without it,
   a leaked initData string is a permanent forged session.

Telegram also ships an Ed25519 `signature` field for third parties that don't hold
the bot token. We hold the token, so the HMAC path above is canonical; Ed25519
validation is outside the v1 scope.

### 3.3 Auth dependency — add to `app/api/deps.py`

```python
from fastapi import Header, HTTPException, Depends
from app.utils.telegram_auth import verify_init_data, InitDataError
from app.services.user_service import UserService

async def current_tg_user(
    x_init_data: str = Header(..., alias="X-Init-Data"),
    db: Session = Depends(get_db),
) -> User:
    try:
        fields = verify_init_data(x_init_data)
    except InitDataError:
        raise HTTPException(status_code=401, detail="invalid Telegram auth")

    tg = fields["user"]
    user = UserService.get_or_create_user_by_telegram(
        telegram_chat_id=str(tg["id"]), username=tg.get("username"), db=db
    )
    if user.is_blocked or not user.is_active:
        raise HTTPException(status_code=403, detail="account unavailable")
    return user
```

Treat `initData` like a stateless signed token: verify it on **every** call, not
once at "login". There is no server session.

### 3.4 Router — `app/api/miniapp.py` (NEW)

Thin HTTP surface over the existing engine. Register under `/api/miniapp` and add
its CORS origin (`MINIAPP_URL`) to the CORS config. Endpoints:

| Method | Path                      | Purpose                                        |
|--------|---------------------------|------------------------------------------------|
| GET    | `/api/miniapp/config`     | Public game catalogue: games, limits, payouts  |
| GET    | `/api/miniapp/me`         | Verified user + wallet balance                 |
| POST   | `/api/miniapp/play`       | Place + settle one bet, return animatable result |
| GET    | `/api/miniapp/history`    | Paged bet history (reuse `BetService.get_bet_history`) |
| GET    | `/api/miniapp/deposit-url`| Hand back a hosted-checkout URL (compliant rail) |

`/play` sketch (Pydantic-validated body; Decimal-safe stake handling — see edge
cases §5.2):

```python
from decimal import Decimal, InvalidOperation
GAMES = {"color": ColorGame, "wheel": LuckyWheelGame,
         "pick3": Pick3Game, "football": FootballYesNoGame}

@router.post("/play")
async def play(body: PlayRequest, request: Request,
               user: User = Depends(current_tg_user),
               db: Session = Depends(get_db)):
    await enforce_rate_limit(user.id)                       # §5.5
    engine = GAMES.get(body.game)
    if engine is None:
        raise HTTPException(422, "unknown game")
    try:
        stake = Decimal(str(body.stake))                    # str() first — never Decimal(float)
    except (InvalidOperation, TypeError):
        raise HTTPException(422, "invalid stake")

    try:
        bet, result = await engine.play(
            user_id=user.id, stake_amount=stake,
            bet_data=body.data, db=db,
        )
    except InvalidBetAmountError as e:
        raise HTTPException(422, str(e))                    # min/max breach
    except InsufficientBalanceError:
        raise HTTPException(409, "insufficient balance")
    except (InvalidBetDataError, BettingError) as e:
        raise HTTPException(422, str(e))

    return {
        "result": result,
        "balance": str(WalletService.get_balance(user.id, db)),
        "bet_id": bet.id,
    }
```

Pass `ip_address` / `user_agent` from `request` into an optional audit path if you
extend `place_bet` calls — the columns already exist on `Bet`.

---

## 4. Frontend work

### 4.1 Stack & location

Mirror `admin-dashboard/` — **Vite + React + Tailwind**. New SPA directory
`miniapp/`, built to `miniapp/dist/`, served by nginx at its own path (e.g.
`/app/`). Add a Docker build stage / compose service alongside
`kasi-admin-dashboard`.

The single external script Telegram requires:
`<script src="https://telegram.org/js/telegram-web-app.js"></script>` — load it in
`index.html` (it must come from telegram.org, not be bundled).

### 4.2 Telegram SDK integration

```js
const tg = window.Telegram.WebApp;
tg.ready();
tg.expand();                 // full height
tg.disableVerticalSwipes?.(); // stop accidental swipe-to-close mid-game (newer API)

// initData for the backend — send raw string, never initDataUnsafe:
const initData = tg.initData;               // -> header "X-Init-Data"
// Theme -> CSS variables so the app matches the client automatically:
applyTheme(tg.themeParams);                 // --tg-theme-bg-color, -button-color, ...
tg.onEvent('themeChanged', () => applyTheme(tg.themeParams));
```

- **Primary action = `tg.MainButton`**, not an in-page button. Native, pinned,
  has a built-in loading state: `tg.MainButton.setText('Bet R10').show()`;
  `tg.MainButton.showProgress()` while `/play` is in flight.
- **`tg.BackButton`** for game → lobby navigation.
- **Haptics**: `tg.HapticFeedback.impactOccurred('medium')` on spin;
  `notificationOccurred('success'|'error')` on reveal. Cheap, large UX lift.
- **`start_param`**: read `tg.initDataUnsafe.start_param` to deep-link straight
  into a game (from `t.me/<bot>?startapp=wheel`).

### 4.3 Screens

- **Lobby**: game cards (colour, wheel, pick-3, football), live balance, deposit.
- **Colour Game**: 4 tappable tiles → MainButton "Bet R{stake}" → server returns
  `drawn_color` → reveal animation (drawn tile pulses) → haptic → balance counter
  animates.
- **Lucky Wheel**: SVG/canvas wheel with 12 segments. **The server decides the
  number; the client animates the wheel to land on the returned segment.** The
  wheel is pure presentation. This is the single most important fairness property
  of the whole UI — a reviewer should be able to confirm the client cannot
  influence the outcome.
- **Pick-3 / Football**: form-style selectors, same submit-through-MainButton flow.

### 4.4 Balance sync

For MVP, re-fetch `/api/miniapp/me` after each play and on focus. A WebSocket push
(FastAPI supports it natively; Redis already in the stack) is the better long-term
option for settlement/balance events but is not required for v1.

---

## 5. Edge cases — **treat this section as the spec, not a checklist**

Game feel lives or dies here. Every item below has broken a live betting UI
somewhere. Group by concern.

### 5.1 Auth / initData

- **Missing/blank `X-Init-Data`** → 401, friendly "Please reopen from Telegram"
  screen. Happens when the SPA is opened in a normal browser.
- **Stale `initData`** (app left open for hours, phone slept) → 401. Frontend must
  catch 401 and call `tg.close()` or prompt reopen, **not** silently retry a bad
  bet.
- **Forged/replayed initData** → rejected by HMAC + freshness. Log at WARN with
  the telegram id claimed; do not leak which check failed to the client.
- **Blocked / inactive user** (`is_blocked`, `is_active`) → 403 on `me` and
  `play`. The lobby must render a clear "account unavailable" state, not a broken
  game.
- **First-ever open** → `get_or_create_user_by_telegram` creates user + zero
  wallet. New user lands with balance 0 → deposit prompt, not an error.
- **User has no wallet row** (data anomaly) → `get_balance` raises
  `WalletNotFoundError`; catch and surface "wallet unavailable", alert ops.

### 5.2 Money & betting integrity

- **Decimal, never float.** Stake arrives as JSON number. Convert with
  `Decimal(str(value))`. `Decimal(0.1)` is `0.1000000000000000055…` and will drift
  balances. Quantize to 2 dp (`.quantize(Decimal("0.01"))`) and reject more than
  2 decimal places from the client.
- **Min/max stake** per game come from `BetService.BET_LIMITS`
  (e.g. Color R5–R500, Pick-3 R2–R100). Enforce server-side (already enforced in
  `place_bet` → `InvalidBetAmountError`) **and** in the UI so the user sees limits
  before submitting. Never trust the client value.
- **Insufficient balance** → `place_bet` raises `InsufficientBalanceError` →
  return 409. UI shows "top up" without consuming the tap as a loss.
- **Zero / negative / non-numeric / NaN / Infinity stake** → 422 before touching
  the engine.
- **Double-submit / rapid re-tap** (the classic double-debit). A WebView can fire
  two `/play` calls before the first returns. Mitigate with **both**:
  1. Client: disable MainButton + `showProgress()` on submit; ignore taps until
     the response resolves.
  2. Server: **idempotency key** — client sends a per-attempt UUID (or reuse
     Telegram `query_id`) in the body; cache `key -> bet_id` in Redis for ~60s and
     return the first result on replay instead of placing a second bet. This is the
     authoritative guard; the client disable is only cosmetic.
- **Orphaned PENDING bet (money-critical).** In each `Game.play()`, `place_bet`
  commits the stake **debit** first, then `settle_bet` commits separately. If the
  worker dies, the connection drops, or settle raises **between** those two
  commits, the user is debited with a bet stuck in `PENDING` and no result. You
  must:
  - Wrap the play call so a settle failure is logged with `bet_id` and surfaced as
    a retriable error, and
  - Provide a **sweep** (scheduled job or admin action) that finds
    `status=PENDING` bets older than N seconds and calls
    `BetService.refund_bet(bet_id, reason, db)` (already implemented, refunds stake
    and only touches PENDING bets). Document this in the runbook alongside
    `PHASE_5_EDGE_CASES_AND_RUNBOOKS.md`.
  - The Mini App must never show a win/loss for a bet whose settle did not confirm.
- **Result/response lost in transit** (bet settled server-side, response never
  reached client). Because settlement already happened, a client retry must be an
  idempotent replay (returns the same `bet_id`/result), **not** a new bet. Same
  Redis idempotency key covers this. On reconnect, the UI should reconcile via
  `/history` rather than assume.

### 5.3 Game UX / animation

- **Never let animation imply the outcome before the server responds.** Start the
  spin only after `/play` resolves, then animate *to* the returned segment. If you
  spin optimistically and the server says otherwise, you either lie to the user or
  snap the wheel — both feel broken.
- **Network loss mid-spin** → show a spinner/"settling…" state, not a frozen
  wheel. On timeout, query `/history` for the bet result before declaring
  anything. Give the user a "check result" affordance rather than a dead screen.
- **Animation interrupted** (user backgrounds the app, rotates, or the WebView is
  throttled while `document.hidden`). requestAnimationFrame pauses when hidden;
  on `visibilitychange` back to visible, **jump to final state** rather than
  resuming a stale tween. The recorded result is authoritative regardless of
  whether the animation finished.
- **Reload / re-open mid-game.** Mini Apps can be reloaded by the user. There is
  no in-memory game state to trust; always rehydrate from `/me` + `/history`.
- **Viewport changes**: `tg.viewportStableHeight` shifts when the keyboard opens
  or the app is expanded/collapsed. Lay out with the Telegram viewport vars, not
  `100vh` — the wheel must not be clipped behind the MainButton.
- **Back button / swipe-to-close mid-bet.** Once `/play` is in flight, the outcome
  is committed server-side even if the user leaves. Disable vertical swipe during
  a spin (`disableVerticalSwipes`) and reconcile on next open so a closed app never
  looks like a lost bet.
- **Balance counter races the settle.** Animate the balance from the value in the
  `/play` response (`result.payout`, new `balance`), not from a separate `/me`
  fetch that might land before or after settlement.
- **Rapid game switching** while a bet is in flight — cancel/ignore stale in-flight
  responses (track a request token; drop responses for a superseded game screen).

### 5.4 Client environment

- **Opened outside Telegram** (`window.Telegram?.WebApp` undefined) → render a
  "Open in Telegram" fallback, never crash.
- **Old Telegram clients**: feature-detect every WebApp API you use
  (`tg.MainButton`, `HapticFeedback`, `disableVerticalSwipes` are version-gated).
  Degrade gracefully; check `tg.version`.
- **iOS vs Android WebView differences**: momentum scroll, safe-area insets,
  autoplay/audio restrictions (game sounds need a user gesture on iOS).

### 5.5 Abuse / concurrency

- **Rate limit `/play`** per verified user (Redis token bucket,
  `MINIAPP_RATE_LIMIT_PER_MIN`). A WebView scripts far faster than a human tapping
  chat — protect the engine and the wallet lock.
- **Concurrent bets from two devices** (same Telegram account, two sessions). The
  wallet row uses `SELECT … FOR UPDATE` in `debit`/`credit`, so balance stays
  consistent; verify the two `/play` calls serialize correctly and neither
  double-spends. Add a test for it.
- **Clock skew**: `auth_date` freshness assumes reasonable server time. If
  containers drift, freshness checks misfire — pin NTP / document it.

---

## 6. Security checklist

- [ ] `initData` HMAC verified on every request; `compare_digest`; freshness
      enforced.
- [ ] Raw `initData` sent from client; `initDataUnsafe` used only for cosmetic
      hints, never for `user_id`.
- [ ] All outcomes/RNG server-side in `app/services/games/*` (`secrets`); client
      animates only.
- [ ] CORS: only `MINIAPP_URL` allowed for `/api/miniapp/*`.
- [ ] `Content-Security-Policy` with `frame-ancestors` limited to Telegram
      origins; strict HTTPS (certbot/nginx already terminates TLS).
- [ ] Per-user rate limit + idempotency key on `/play`.
- [ ] Blocked/inactive users rejected server-side.
- [ ] No bot token, provider keys, or secrets in the SPA bundle.
- [ ] Structured logs on auth failures (WARN) and orphaned-PENDING sweeps.

---

## 7. Testing plan

**Backend (pytest, async supported):**

- `verify_init_data`: valid payload passes; tampered field fails; reversed
  key/message fails; stale `auth_date` fails; missing `hash`/`user` fails;
  malformed query string fails.
- `current_tg_user`: creates user on first open; rejects blocked/inactive (403);
  rejects bad initData (401).
- `/play`: happy path debits+settles; below-min and above-max → 422; insufficient
  balance → 409; unknown game → 422; float-ish stake quantized correctly;
  idempotency key replay returns same `bet_id` (no second debit).
- Concurrency: two simultaneous `/play` calls for one user serialize; balance
  integrity holds (`WalletService.verify_balance_integrity`).
- Orphaned PENDING: simulate settle failure after debit; sweep refunds via
  `refund_bet`; balance restored.

**Frontend:** initData wiring; 401/403/409 handled without phantom bets; wheel
lands on server segment; visibility-change jumps to final state; offline-mid-spin
recovers via `/history`; opened-outside-Telegram fallback.

---

## 8. Deploy / ops

- **BotFather**: `/setmenubutton` → point to `MINIAPP_URL`; optionally configure a
  Main Mini App and `startapp` deep links.
- **nginx**: serve `miniapp/dist/` at its path; set CSP/`frame-ancestors`; ensure
  `telegram.org` script is reachable (it's loaded client-side, not proxied).
- **Compose**: add `kasi-miniapp` build/serve stage mirroring
  `kasi-admin-dashboard`; wire into `kasi-nginx`.
- **Env**: `MINIAPP_URL`, `MINIAPP_INITDATA_MAX_AGE_SECONDS`,
  `MINIAPP_RATE_LIMIT_PER_MIN` added to `.env` / deployment secrets.
- **Runbook**: add the orphaned-PENDING sweep and the "user reports missing win"
  reconciliation steps to `PHASE_5_EDGE_CASES_AND_RUNBOOKS.md`.

---

## 9. Suggested milestones (pickup order)

1. ✅ **`telegram_auth.py` + tests** — self-contained, everything depends on it.
   Ship first, in isolation.
2. ✅ **`current_tg_user` dep + `/me` + `/config`** — proves end-to-end auth with no
   money movement.
3. ✅ **`/play` for one game (Color) + idempotency + rate limit + tests** — the
   money path; get every §5.2 edge case green before adding games.
4. ✅ **Orphaned-PENDING sweep + runbook** — close the money-integrity gap before UI
   polish.
5. 🔄 **React SPA lobby + Color game** — implementation and automated verification
   are complete; end-to-end rehearsal in a real Telegram client remains.
6. **Lucky Wheel** (the animation-heavy one; validate §5.3 thoroughly).
7. **Pick-3 / Football**, then history + deposit-url screens.
8. **Deploy** (nginx path, compose, BotFather).

---

## 10. Open questions for the owner

- Deposit UX inside the Mini App: `WebApp.openInvoice` (Bot Payments API) vs
  `openLink` to a hosted checkout — confirm which compliant provider flow the
  product is standardising on.
- Real-time balance: polling for v1, or invest in the WebSocket push now?
- Do we expose bet history/statistics (`get_bet_statistics`) in the Mini App or
  keep it admin-only for v1?
- Confirm `Pick3Game.play` / `FootballYesNoGame.play` signatures before wiring
  (Football is materially larger — 14 KB — and may have match-selection state the
  others don't).
```
