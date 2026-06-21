from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def referral_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🏠 Main Menu", callback_data="home"),
        ],
    ])
