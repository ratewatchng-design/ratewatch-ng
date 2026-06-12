from telegram import Update
from telegram.ext import ContextTypes
from database.users_db import get_user, update_user
from ui.settings_menu import settings_keyboard, notif_style_keyboard, quiet_hours_keyboard

STYLE_LABELS = {
    "instant": "Instant — alert immediately",
    "grouped": "Grouped — combine within 15 min",
    "digest": "Daily Digest — summary only",
}

QH_LABELS = {
    "10pm_6am": "10PM – 6AM",
    "11pm_7am": "11PM – 7AM",
    "off": "Off",
}


async def settings_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "⚙️ *Preferences*\n\nCustomise your notification experience.",
        parse_mode="Markdown",
        reply_markup=settings_keyboard(),
    )


async def notif_style_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    tg_id = update.effective_user.id
    user = get_user(tg_id)
    current = (user or {}).get("notification_style", "instant")
    await query.edit_message_text(
        "🔔 *Notification Style*",
        parse_mode="Markdown",
        reply_markup=notif_style_keyboard(current),
    )


async def set_notif_style(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    tg_id = update.effective_user.id
    style = query.data.replace("style_", "")
    user = get_user(tg_id)
    if user:
        update_user(user["$id"], {"notification_style": style})
    label = STYLE_LABELS.get(style, style)
    await query.edit_message_text(
        f"✅ Notification style set to:\n*{label}*",
        parse_mode="Markdown",
        reply_markup=notif_style_keyboard(style),
    )


async def quiet_hours_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    tg_id = update.effective_user.id
    user = get_user(tg_id)
    current = (user or {}).get("quiet_hours", "off")
    await query.edit_message_text(
        "🌙 *Quiet Hours*\n\nYou won't receive alerts during this period.",
        parse_mode="Markdown",
        reply_markup=quiet_hours_keyboard(current),
    )


async def set_quiet_hours(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    tg_id = update.effective_user.id
    setting = query.data.replace("qh_", "")
    user = get_user(tg_id)
    if user:
        update_user(user["$id"], {"quiet_hours": setting})
    label = QH_LABELS.get(setting, setting)
    await query.edit_message_text(
        f"✅ Quiet hours set to: *{label}*",
        parse_mode="Markdown",
        reply_markup=quiet_hours_keyboard(setting),
    )
