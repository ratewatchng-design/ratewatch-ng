import logging
from telegram import Update
from telegram.ext import ContextTypes
from database.users_db import get_all_users, get_premium_users
from database.alerts_db import get_all_active_alerts
from handlers.premium import activate_premium
from services.notification_service import send_message
from utils.config import ADMIN_TELEGRAM_ID

logger = logging.getLogger(__name__)


def _is_admin(update: Update) -> bool:
    return update.effective_user.id == ADMIN_TELEGRAM_ID


async def admin_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_admin(update):
        return
    users = get_all_users()
    premium = get_premium_users()
    alerts = get_all_active_alerts()
    text = (
        f"🛠 *Admin Panel*\n\n"
        f"Total users: {len(users)}\n"
        f"Premium users: {len(premium)}\n"
        f"Active alerts: {len(alerts)}\n\n"
        f"Commands:\n"
        f"/users — list users\n"
        f"/premium <id> — grant premium\n"
        f"/broadcast <msg> — send to all users"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


async def users_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_admin(update):
        return
    users = get_all_users()
    if not users:
        await update.message.reply_text("No users found.")
        return
    lines = []
    for u in users[:50]:
        name = u.get("first_name", "")
        username = f"@{u['username']}" if u.get("username") else "—"
        plan = u.get("plan", "free")
        lines.append(f"{u['telegram_id']} | {name} {username} | {plan}")
    await update.message.reply_text(
        "*Users (first 50):*\n\n" + "\n".join(lines),
        parse_mode="Markdown"
    )


async def broadcast_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_admin(update):
        return
    if not context.args:
        await update.message.reply_text("Usage: /broadcast <message>")
        return
    msg = " ".join(context.args)
    users = get_all_users()
    sent, failed = 0, 0
    for user in users:
        try:
            await send_message(context.bot, user["telegram_id"], msg)
            sent += 1
        except Exception:
            failed += 1
    await update.message.reply_text(f"✅ Broadcast done.\nSent: {sent} | Failed: {failed}")


async def grant_premium_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_admin(update):
        return
    if not context.args:
        await update.message.reply_text("Usage: /premium <telegram_id>")
        return
    try:
        tg_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("Invalid Telegram ID.")
        return
    await activate_premium(tg_id)
    await update.message.reply_text(f"✅ Premium granted to {tg_id}.")
