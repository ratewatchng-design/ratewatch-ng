from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from utils.formatting import fmt_alert_short


def asset_selection_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🇺🇸 USD/NGN", callback_data="asset_USDNGN"),
            InlineKeyboardButton("🇪🇺 EUR/NGN", callback_data="asset_EURNGN"),
        ],
        [
            InlineKeyboardButton("🇬🇧 GBP/NGN", callback_data="asset_GBPNGN"),
            InlineKeyboardButton("💵 USDT/NGN", callback_data="asset_USDTNGN"),
        ],
        [
            InlineKeyboardButton("🪙 BTC/NGN", callback_data="asset_BTCNGN"),
        ],
        [
            InlineKeyboardButton("⬅️ Back", callback_data="home"),
        ],
    ])


def condition_selection_keyboard(asset: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📈 Above Price", callback_data="cond_above"),
            InlineKeyboardButton("📉 Below Price", callback_data="cond_below"),
        ],
        [
            InlineKeyboardButton("📊 Change %", callback_data="cond_pct"),
        ],
        [
            InlineKeyboardButton("⬅️ Back", callback_data="new_alert"),
        ],
    ])


def pct_condition_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📈 % Increase", callback_data="cond_pct_up"),
            InlineKeyboardButton("📉 % Decrease", callback_data="cond_pct_down"),
        ],
        [
            InlineKeyboardButton("⬅️ Back", callback_data="new_alert"),
        ],
    ])


def alert_created_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("➕ Create Another", callback_data="new_alert"),
            InlineKeyboardButton("📋 My Alerts", callback_data="my_alerts"),
        ],
        [
            InlineKeyboardButton("🏠 Main Menu", callback_data="home"),
        ],
    ])


def my_alerts_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("❌ Remove Alert", callback_data="remove_alert"),
            InlineKeyboardButton("➕ Add Alert", callback_data="new_alert"),
        ],
        [
            InlineKeyboardButton("🏠 Main Menu", callback_data="home"),
        ],
    ])


def remove_alert_keyboard(alerts: list[dict]) -> InlineKeyboardMarkup:
    rows = []
    for alert in alerts:
        label = fmt_alert_short(alert)
        rows.append([InlineKeyboardButton(label, callback_data=f"delete_alert_{alert['$id']}")])
    rows.append([InlineKeyboardButton("⬅️ Back", callback_data="my_alerts")])
    return InlineKeyboardMarkup(rows)


def triggered_alert_keyboard(alert_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📊 Current Rates", callback_data="rates"),
            InlineKeyboardButton("❌ Delete Alert", callback_data=f"delete_alert_{alert_id}"),
        ],
        [
            InlineKeyboardButton("🏠 Home", callback_data="home"),
        ],
    ])
