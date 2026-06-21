# RateWatch NG

A Telegram bot for Nigerians to monitor USD/NGN, EUR/NGN, GBP/NGN, USDT/NGN, and BTC/NGN — with instant alerts when target conditions are met.

## Features

- **Real-time alerts** — Above/Below price conditions, instant or grouped delivery
- **5 assets** — USD, EUR, GBP, USDT, BTC vs Naira
- **Free plan** — 3 alerts, USD only, 30-min polling
- **Premium plan** — Unlimited alerts, all assets, instant monitoring, weekly reports (₦999/month)
- **Referral system** — Earn alert slots and free premium
- **Quiet hours** — Silence alerts at night
- **Daily & weekly summaries**

## Stack

| Layer | Tech |
|---|---|
| Language | Python 3.12 |
| Bot | python-telegram-bot 21.6 |
| Database | Appwrite Cloud |
| Hosting | Render Web Service |
| Rates | ExchangeRate-API + CoinGecko |

## Repository Structure

```
ratewatch-ng/
├── bot.py                  # Entry point, webhook + job scheduler
├── handlers/                # Telegram interaction logic
│   ├── start.py             # /start (registration) + main_menu (home button)
│   ├── alerts.py
│   ├── rates.py
│   ├── premium.py
│   ├── referrals.py
│   ├── settings.py
│   └── admin.py
├── ui/                       # All InlineKeyboardMarkup builders
│   ├── main_menu.py
│   ├── alert_menu.py
│   ├── rates_menu.py
│   ├── premium_menu.py
│   ├── referral_menu.py
│   └── settings_menu.py
├── services/                 # External API wrappers
│   ├── forex_service.py
│   ├── crypto_service.py     # Cached to avoid CoinGecko 429s
│   └── notification_service.py
├── database/                 # Appwrite CRUD operations
│   ├── client.py
│   ├── users_db.py
│   ├── alerts_db.py
│   ├── subscriptions_db.py
│   └── referrals_db.py
├── jobs/                      # Scheduled background tasks
│   ├── alert_checker.py       # Every 60s
│   ├── daily_summary.py       # 7AM WAT
│   └── weekly_summary.py     # 8AM WAT, Mondays, premium only
├── utils/
│   ├── config.py              # Environment variables
│   └── formatting.py          # Price/label helpers
├── requirements.txt
├── render.yaml
├── .python-version
├── .env.example
└── .gitignore
```

## /start vs Main Menu — why they're separate

Earlier versions of this bot wired the 🏠 **Main Menu** button to the same handler as `/start`. That meant every time a user pressed Main Menu, the bot re-ran the full registration check — harmless on its own, but risky under concurrent updates and wasteful on every button press.

Now the two are split:

| Trigger | Handler | What it does |
|---|---|---|
| `/start` command | `start_handler` | Checks Appwrite for an existing user by `telegram_id`. Creates one **only if missing**. Handles referral linking. Then shows the main menu. |
| 🏠 Main Menu button | `main_menu_handler` | Never touches the database for user creation. Just renders the menu. Can only be reached by an already-registered user. |

Both call a shared `_render_main_menu()` so the screen looks identical either way — the difference is purely in whether a registration check runs.

## Setup

### 1. Clone & install

```bash
git clone https://github.com/youruser/ratewatch-ng.git
cd ratewatch-ng
pip install -r requirements.txt
```

### 2. Configure environment

Copy `.env.example` to `.env` and fill in all values locally if testing outside Render.

### 3. Appwrite collections

Create a database (any name, e.g. `ratewatch_db`) and the following 4 collections. **Every attribute key must match exactly** — Appwrite rejects documents containing any field it doesn't recognize.

**`users`**

| Attribute Key | Type | Notes |
|---|---|---|
| `telegram_id` | Integer | Required, add Index |
| `username` | String (64) | |
| `first_name` | String (64) | |
| `plan` | String (16) | `free` / `premium` |
| `referrals` | Integer | Default 0 |
| `notification_style` | String (16) | `instant` / `grouped` / `digest` |
| `quiet_hours` | String (16) | `off` / `10pm_6am` / `11pm_7am` |
| `created_at` | String (32) | ISO 8601 |

**`alerts`**

| Attribute Key | Type | Notes |
|---|---|---|
| `telegram_id` | Integer | Required, Index |
| `asset` | String (16) | e.g. `USDNGN`, `BTCNGN` |
| `condition` | String (16) | `above` / `below` / `pct_up` / `pct_down` |
| `target` | Float | Required |
| `active` | Boolean | Default true, Index |
| `created_at` | String (32) | |

**`subscriptions`**

| Attribute Key | Type |
|---|---|
| `telegram_id` | Integer (Index) |
| `plan` | String (16) |
| `expires_at` | String (16) |

**`referrals`**

| Attribute Key | Type |
|---|---|
| `referrer` | Integer (Index) |
| `referred` | Integer (Unique Index) |
| `created_at` | String (16) |

### 4. Render deployment

1. Connect your GitHub repo as a new Web Service on Render
2. Set **Start Command**: `python bot.py`
3. Add environment variable `PYTHON_VERSION = 3.12.0` (Render ignores `render.yaml`'s `pythonVersion` field unless deployed via Blueprint)
4. Add all required env vars (see `.env.example`)
5. Push to `main` — Render auto-deploys

### 5. Telegram bot commands

Via **@BotFather** → `/setcommands`:

```
start - Open main menu
help - How to use RateWatch NG
```

Admin commands (`/admin`, `/users`, `/broadcast`) are intentionally left out of the public menu — they only work for `ADMIN_TELEGRAM_ID` and can be typed manually.

## Known operational notes

- **CoinGecko free tier** rate-limits aggressively (HTTP 429). `crypto_service.py` caches results for 90 seconds to absorb this — if you see `429` in logs occasionally, it's expected and the bot falls back to the last cached price.
- **Telegram "Message is not modified" errors** happen when a button is pressed twice producing identical content. All handlers wrap `edit_message_text` calls to swallow this specific error silently — any other error still surfaces normally.
- **Global error handler** in `bot.py` logs every unhandled exception with a full traceback instead of failing silently. Check Render logs first when something "does nothing."

## Admin Commands

| Command | Description |
|---|---|
| `/admin` | Show stats panel |
| `/users` | List first 50 users |
| `/premium <id>` | Grant premium to a user |
| `/broadcast <msg>` | Send message to all users |

## License

MIT
