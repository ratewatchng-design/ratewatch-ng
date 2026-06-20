from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def rates_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔄 Refresh", callback_data="refresh_rates"),
            InlineKeyboardButton("📅 Daily Summary", callback_data="daily_summary"),
        ],
        [
            InlineKeyboardButton("🏠 Main Menu", callback_data="home"),
        ],
    ])
