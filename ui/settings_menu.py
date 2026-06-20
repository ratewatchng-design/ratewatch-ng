from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def settings_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔔 Notification Style", callback_data="notif_style"),
        ],
        [
            InlineKeyboardButton("🌙 Quiet Hours", callback_data="quiet_hours"),
        ],
        [
            InlineKeyboardButton("🏠 Main Menu", callback_data="home"),
        ],
    ])


def notif_style_keyboard(current: str = "instant") -> InlineKeyboardMarkup:
    def check(val):
        return "✓ " if current == val else ""

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(f"{check('instant')}Instant", callback_data="style_instant"),
            InlineKeyboardButton(f"{check('grouped')}Grouped", callback_data="style_grouped"),
        ],
        [
            InlineKeyboardButton(f"{check('digest')}Daily Digest", callback_data="style_digest"),
        ],
        [
            InlineKeyboardButton("⬅️ Back", callback_data="settings"),
        ],
    ])


def quiet_hours_keyboard(current: str = "off") -> InlineKeyboardMarkup:
    def check(val):
        return "✓ " if current == val else ""

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(f"{check('10pm_6am')}10PM – 6AM", callback_data="qh_10pm_6am"),
            InlineKeyboardButton(f"{check('11pm_7am')}11PM – 7AM", callback_data="qh_11pm_7am"),
        ],
        [
            InlineKeyboardButton(f"{check('off')}Off", callback_data="qh_off"),
        ],
        [
            InlineKeyboardButton("⬅️ Back", callback_data="settings"),
        ],
    ])
