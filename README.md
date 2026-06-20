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
| Bot | python-telegram-bot 21 |
| Database | Appwrite Cloud |
| Hosting | Render Web Service |
| Rates | ExchangeRate-API + CoinGecko |

## Repository Structure

```
ratewatch-ng/
├── bot.py                  # Entry point, webhook + job scheduler
├── handlers/               # Telegram interaction logic
│   ├── start.py
│   ├── alerts.py
│   ├── rates.py
│   ├── premium.py
│   ├── referrals.py
│   ├── settings.py
│   └── admin.py
├── ui/                     # All InlineKeyboardMarkup builders
│   ├── main_menu.py
│   ├── alert_menu.py
│   ├── rates_menu.py
│   ├── premium_menu.py
│   ├── referral_menu.py
│   └── settings_menu.py
├── services/               # External API wrappers
│   ├── forex_service.py
│   ├── crypto_service.py
│   └── notification_service.py
├── database/               # Appwrite CRUD operations
│   ├── client.py
│   ├── users_db.py
│   ├── alerts_db.py
│   ├── subscriptions_db.py
│   └── referrals_db.py
├── jobs/                   # Scheduled background tasks
│   ├── alert_checker.py
│   ├── daily_summary.py
│   └── weekly_summary.py
├── utils/
│   ├── config.py           # Environment variables
│   └── formatting.py       # Price/label helpers
├── requirements.txt
├── render.yaml
└── .env.example
```

## Setup

### 1. Clone & install

```bash
git clone https://github.com/youruser/ratewatch-ng.git
cd ratewatch-ng
pip install -r requirements.txt
```

### 2. Configure environment

Copy `.env.example` to `.env` and fill in all values.

### 3. Appwrite collections

Create the following collections in your Appwrite database with these attributes:

**Users** — `telegram_id` (integer), `username` (string), `first_name` (string), `plan` (string), `referrals` (integer), `notification_style` (string), `quiet_hours` (string), `created_at` (string)

**Alerts** — `telegram_id` (integer), `asset` (string), `condition` (string), `target` (float), `active` (boolean), `created_at` (string)

**Subscriptions** — `telegram_id` (integer), `plan` (string), `expires_at` (string)

**Referrals** — `referrer` (integer), `referred` (integer), `created_at` (string)

Add an index on `telegram_id` for each collection.

### 4. Deploy to Render

Push to GitHub. Render auto-deploys on every push using `render.yaml`. Set all env vars in the Render dashboard under **Environment**.

### 5. Set webhook

Render will set the webhook automatically via `run_webhook()` in `bot.py`. Ensure your Render service URL is accessible.

## Admin Commands

| Command | Description |
|---|---|
| `/admin` | Show stats panel |
| `/users` | List first 50 users |
| `/premium <id>` | Grant premium to a user |
| `/broadcast <msg>` | Send message to all users |

## License

MIT
