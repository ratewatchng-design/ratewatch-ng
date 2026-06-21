from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def premium_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("💳 Subscribe", callback_data="subscribe"),
        ],
        [
            InlineKeyboardButton("📩 Contact Support", url="https://t.me/ratewatchng_support"),
        ],
        [
            InlineKeyboardButton("⬅️ Back", callback_data="home"),
        ],
    ])
