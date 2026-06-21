from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("➕ New Alert", callback_data="new_alert"),
            InlineKeyboardButton("📋 My Alerts", callback_data="my_alerts"),
        ],
        [
            InlineKeyboardButton("📊 Rates", callback_data="rates"),
            InlineKeyboardButton("🎁 Referrals", callback_data="referrals"),
        ],
        [
            InlineKeyboardButton("⭐ Premium", callback_data="premium"),
            InlineKeyboardButton("⚙️ Settings", callback_data="settings"),
        ],
    ])
