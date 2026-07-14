# Telegram payments from South Africa — complete options guide

**Research date:** May 2026
**Scope:** Making and receiving payments via Telegram, with South African context — feasibility, implementation complexity, prerequisites, and fees.

---

## The lay of the land

Telegram has three distinct payment layers and they don't all work the same way. Before picking an option, it helps to know which layer you're working in:

- **Layer 1 — Telegram Stars (native in-app currency):** Telegram's own virtual currency, backed by TON blockchain, used for digital goods and content monetization. Global. No ZAR, no bank account required.
- **Layer 2 — Telegram Bot Payments API:** Connects a custom bot to external payment gateways (Paystack, Flutterwave, etc.) that process real fiat. South Africa has direct gateway support here.
- **Layer 3 — Telegram Wallet (TON/crypto):** Built-in crypto wallet supporting TON, BTC, USDT. Available in South Africa. Off-ramp is via exchange, not directly to ZAR bank account.

The right option depends on what you're selling, who's paying, and how you need to receive the money.

---

## Option 1 — Telegram Stars + Fragment withdrawal

### What it is
Stars are Telegram's native in-app currency. Users buy Stars via Apple Pay, Google Pay, or Fragment.com (using TON). You receive Stars when users pay for digital content, subscriptions, or tip you. You then convert Stars → TON → ZAR via a crypto exchange.

### What you can use it for
- Digital goods and services (not physical products)
- Gated channel/group access
- Paid reactions and tips on posts
- Digital downloads, courses, bot features

### How it works in practice
1. Enable paid reactions on your channel, or integrate `sendInvoice` in your bot with `currency: XTR`
2. Users pay in Stars; you accumulate a balance
3. Once you hit 1,000 Stars minimum (and they're 21+ days old), withdraw via Fragment
4. Fragment converts Stars → TON into your connected TON wallet
5. Send TON to a ZAR-friendly exchange (VALR, Luno, or Bybit) and sell for ZAR
6. Withdraw ZAR to your South African bank account

### Implementation complexity: Low to Medium
- Zero code needed if using InviteMember or channel reactions
- Custom bot integration requires Telegram Bot API + `sendInvoice` call — a few hours for an experienced developer
- The off-ramp (TON → ZAR) adds operational steps but is straightforward

### Prerequisites
- Telegram channel or bot
- TON wallet (built into Telegram under Settings > Wallet, or a non-custodial wallet like TON Keeper)
- Fragment.com account (login with Telegram account)
- Exchange account with ZAR support (VALR and Luno both support TON/ZAR or TON→BTC→ZAR paths)
- KYC on the exchange

### Fees
- Telegram takes 0% commission from creator earnings (100% of Stars received go to you)
- Apple/Google take 30% from the buyer's purchase of Stars — you don't pay this, but the buyer pays more if buying via app stores vs Fragment
- Fragment exchange rate applies on Stars → TON conversion
- Exchange trading fees typically 0.1–0.5%
- SARB exchange control: amounts under R1,000,000/year can flow without additional SARB approval; individual annual crypto allowance is R1M (part of the single discretionary allowance or foreign capital allowance)

### ZA-specific notes
Telegram Wallet and Fragment are accessible in South Africa. TON is listed on VALR and Luno. There are no regulatory restrictions on receiving TON and converting to ZAR, though SARS expects crypto gains to be declared.

---

## Option 2 — Paystack + InviteMember (fastest to ZAR)

### What it is
InviteMember is a no-code subscription bot platform for Telegram. Connect Paystack (which has full South Africa support) and you can accept card payments, EFT, USSD, and bank transfers directly in ZAR. Payouts land in your South African bank account.

### What you can use it for
- Paid Telegram channel/group access
- Recurring subscriptions
- One-time access fees
- Mixed payment methods (card + bank transfer + USSD for customers)

### How it works in practice
1. Create a Paystack account at paystack.com (free, requires SA business or personal account, FICA docs)
2. Create an InviteMember project at @InviteMemberBot
3. Connect Paystack by pasting your API keys
4. Set up your pricing plans in ZAR (or USD, NGN, GHS, KES)
5. InviteMember generates a membership bot; users pay through it and get auto-access

### Implementation complexity: Very Low
- No code at all
- Full setup takes under an hour
- Paystack approval takes 1–3 business days
- Plans must be priced in ZAR, USD, NGN, GHS, or KES — other currencies won't trigger the Paystack option

### Prerequisites
- Paystack business or personal account (SA ID/passport + bank account)
- InviteMember account ($49/month flat fee, no per-transaction fee on their side — Paystack charges 2.9% + R2 per transaction for local cards, slightly higher for international)
- A Telegram channel or group you own/admin

### Fees
- InviteMember: $49/month (~R900/month at current rates). There is a 10% transaction fee on the starter tier — check current pricing on invitemember.com as this varies by plan
- Paystack: 1.5% for local transactions (capped at R1,000 per transaction); 3.9% for international cards
- No additional Telegram fee

### ZA-specific notes
This is the most direct path to ZAR in a South African bank account. Paystack was acquired by Stripe in 2020 but operates independently in Africa. Paystack payouts settle to SA bank accounts in ZAR, typically T+1 to T+2 business days.

---

## Option 3 — Flutterwave + Telegram Bot Payments API

### What it is
Flutterwave is a direct partner on Telegram's official Bot Payments API and has supported South Africa since 2017. Unlike InviteMember, this is a code-level integration — you build a bot that uses Flutterwave as the payment provider token via BotFather.

### What you can use it for
- Physical and digital goods in a custom bot
- In-chat checkout flows (invoice with Pay button)
- One-time and recurring charge patterns
- Any custom e-commerce or service workflow

### How it works in practice
1. Create a Flutterwave merchant account (flutterwave.com)
2. Create your Telegram bot via @BotFather
3. In BotFather: `/mybots` → your bot → Bot Settings → Payments → choose Flutterwave (or another supported provider)
4. Get your `provider_token` from BotFather
5. In your bot code, use `sendInvoice` with the provider_token to generate payment requests
6. Flutterwave handles card/bank transfer/mobile money checkout
7. Payouts settle to your SA bank account

### Implementation complexity: Medium
- Requires bot development (Python, Node.js, or any language with a Telegram Bot API wrapper)
- `sendInvoice` implementation is well-documented; a basic payment flow takes a few days to build
- Flutterwave approval and KYC: 1–5 business days
- No-code path: use Pipedream or Zapier to connect Flutterwave webhooks to Telegram messages without a full custom bot

### Prerequisites
- Flutterwave merchant account (SA company registration docs or individual with FICA)
- Telegram bot token from @BotFather
- A server or serverless function to run the bot (AWS Lambda, Railway, Render — free tiers work for low volume)
- Basic coding ability or a developer

### Fees
- Flutterwave: 1.4% for local SA cards + R7 fixed; 3.8% for international cards
- Telegram: no fee
- Hosting: free–$5/month depending on volume

### ZA-specific notes
Flutterwave supports Visa, Mastercard, and local bank transfer in South Africa. USSD and mobile money are not as mature in SA via Flutterwave as they are in Nigeria/Kenya, but card and EFT work reliably.

---

## Option 4 — Custom bot + Paystack API directly

### What it is
Skip the middleware platforms. Build a Telegram bot that calls Paystack's API directly — not via Telegram's Bot Payments API, but by generating Paystack payment links, sending them via the bot, and using Paystack webhooks to confirm payment and trigger actions.

### What you can use it for
- Full custom e-commerce flows
- WMS/B2B invoicing via Telegram
- Subscription management with full control
- Any workflow requiring deep integration with your own systems (e.g., WMSHub order confirmations, AIautom8ed WhatsApp-style payment triggers)

### How it works in practice
1. User sends a command to your Telegram bot
2. Bot calls `paystack.com/api/transaction/initialize` and gets a payment URL
3. Bot sends the URL to the user in chat
4. User pays on the Paystack checkout page (hosted, no redirect issues)
5. Paystack calls your webhook on successful payment
6. Webhook triggers bot to send confirmation, grant access, update DB, etc.

### Implementation complexity: Medium to High
- Requires a full bot + backend (REST API + webhook listener)
- Paystack's API docs are excellent; integration is clean and well-supported
- Zapier/Pipedream can bridge some of the webhook logic without a full backend

### Prerequisites
- Paystack account (same as Option 2)
- Telegram bot token
- Backend server (Node.js/Python/Java — or serverless)
- Developer time: 1–3 days for a functional prototype; 1–2 weeks for production-grade

### Fees
- Paystack: same as Option 2 (1.5% local, 3.9% international)
- No third-party platform fee (you own the stack)
- Hosting costs apply

### ZA-specific notes
This is the most powerful option for a developer-led business. Paystack's API is production-tested at scale. Settlement to SA bank accounts works. SARB reporting requirements apply for transactions above R50,000.

---

## Option 5 — Telegram Wallet (TON) peer-to-peer

### What it is
Telegram has a built-in crypto wallet (Settings > Wallet) supporting TON, Bitcoin, and USDT. Users can send TON or USDT directly to any Telegram username, in-chat. By May 2026, 100M+ wallets have been activated globally.

### What you can use it for
- Peer-to-peer payments between individuals
- Paying a supplier or contractor in crypto via Telegram
- Receiving international payments without bank wires
- Small business informal sales where crypto is acceptable

### How it works in practice
1. Both parties open Telegram Wallet (Settings > Wallet)
2. Sender taps the wallet, selects Send, enters your Telegram username or wallet address
3. Transfer is confirmed on the TON blockchain in seconds
4. Recipient converts TON → ZAR via VALR, Luno, or Bybit
5. Withdraw ZAR to bank

### Implementation complexity: Zero (for users)
- No code, no API, no accounts beyond Telegram
- KYC applies when withdrawing to exchange/bank
- Fragment requires KYC for withdrawals above certain thresholds

### Prerequisites
- Both parties must have Telegram Wallet activated
- Exchange account for fiat off-ramp (VALR is the best-established SA crypto exchange with ZAR on/off-ramps)

### Fees
- TON transfers within Telegram: 0 fee between users
- TON blockchain transaction fee: negligible (~$0.01)
- Exchange trading fee for TON → ZAR: 0.1–0.5%
- Bank withdrawal fee from exchange: varies (VALR: R8.50 for instant EFT, free for normal EFT)

### ZA-specific notes
Fully legal. SARS treats crypto as an asset; gains are taxable. The SARB's crypto guidance (2014 position statement, updated 2023) says crypto is not legal tender but transactions are not prohibited. Reporting obligations apply to exchanges, not to users, unless transacting amounts above FICA thresholds.

---

## Option 6 — No-code subscription tools (BotSubscription, TGmembership)

### What it is
Alternatives to InviteMember that also support Flutterwave (Africa including SA) for Telegram subscription management. BotSubscription explicitly lists Flutterwave for Africa.

### Implementation complexity: Very Low
- Same no-code approach as InviteMember
- Different pricing structures — some charge revenue share instead of flat fee

### Prerequisites
- Flutterwave or Stripe account (Stripe requires a UK/US entity — see the Stripe note below)
- Telegram bot/channel

---

## The Stripe question

Stripe is not directly available to SA-registered businesses. Stripe's official page lists South Africa as part of its "extended network" via Paystack, but you cannot create a native Stripe merchant account with South African entity documents. The workaround — incorporating a UK company and using a UK bank account (Wise, Tide) — is legal, used by thousands of SA founders, but adds administrative overhead (company registration costs, annual filings, cross-border accounting). For most SA businesses doing Telegram payments domestically, Paystack or Flutterwave is the cleaner path.

---

## Side-by-side comparison

| Option | Path to ZAR | Code required | Setup time | Best for |
|---|---|---|---|---|
| Telegram Stars → TON → exchange | ZAR via exchange | None to low | 1–3 days | Content creators, digital goods |
| Paystack + InviteMember | Direct ZAR bank | None | <1 hour | Subscription communities |
| Flutterwave + Bot Payments API | Direct ZAR bank | Medium | 2–5 days | Custom bots, physical goods |
| Custom bot + Paystack API | Direct ZAR bank | High | 3–14 days | Full-stack custom integrations |
| Telegram Wallet (TON) P2P | ZAR via exchange | None | Minutes | P2P payments, informal sales |
| BotSubscription + Flutterwave | Direct ZAR bank | None | <2 hours | No-code alternative to InviteMember |

---

## Recommended paths by use case

**"I want to sell access to a Telegram group or channel and get paid in ZAR with zero code"**
→ Paystack + InviteMember. Done in under an hour. Paystack settles to your SA bank.

**"I'm building a custom bot (e.g., for WMSHub customer notifications + payment collection)"**
→ Custom bot + Paystack API directly. Full control, no platform fee, best for B2B.

**"I want to monetize content on a public channel (posts, courses, digital files)"**
→ Telegram Stars for the simplest setup. TON → VALR → ZAR off-ramp adds 1–2 extra steps but the Star system is native and frictionless for buyers.

**"I need to receive international payments from customers outside SA"**
→ Telegram Stars (global, no ZAR barriers for the buyer) or Flutterwave (accepts international cards + settles in ZAR).

**"I want to pay a contractor or supplier instantly via Telegram"**
→ Telegram Wallet TON transfer. Zero fees, instant, no setup beyond both parties activating the wallet.

---

## Compliance notes for South Africa

- **SARS:** Crypto income is taxable — as revenue (if trading) or CGT (if investing). Stars → TON → ZAR creates a taxable event at the point of conversion. Keep records.
- **SARB exchange control:** The single discretionary allowance (R1M/year) covers crypto purchases and inflows. Large volumes may require SARB approval.
- **FICA:** Exchanges operating in SA (VALR, Luno) apply KYC/AML checks. You'll need ID and proof of address for the off-ramp.
- **VAT:** If your Telegram business is VAT-registered (turnover above R1M/year), you may need to account for VAT on digital service sales.

---

*Sources: Telegram Bot Payments documentation, Telegram Stars ToS, InviteMember blog (August 2025), BotSubscription docs (April 2026), Paystack developer docs, Flutterwave Medium (2017, confirmed active), Stripe global availability (December 2025/May 2026), Fragment.com withdrawal documentation, Traders Union Telegram Wallet review (March 2026), VALR.com.*
