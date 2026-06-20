from telegram import Update
from telegram.ext import ContextTypes
from database.users_db import is_premium, update_user, get_user
from database.subscriptions_db import create_or_renew_subscription
from ui.premium_menu import premium_keyboard


async def premium_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    tg_id = update.effective_user.id
    premium = is_premium(tg_id)

    if premium:
        text = (
            "⭐ *You're on Premium!*\n\n"
            "✓ Unlimited Alerts\n"
            "✓ Instant Monitoring\n"
            "✓ BTC & USDT Alerts\n"
            "✓ Weekly Reports\n\n"
            "Thank you for subscribing! 🙏"
        )
    else:
        text = (
            "⭐ *Premium Benefits*\n\n"
            "✓ Unlimited Alerts\n"
            "✓ Instant Monitoring\n"
            "✓ BTC Alerts\n"
            "✓ USDT Alerts\n"
            "✓ Weekly Reports\n\n"
            "Price: ₦999/month"
        )

    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=premium_keyboard())


async def subscribe_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    # Payment integration placeholder — manual activation for now
    text = (
        "💳 *Subscribe to Premium*\n\n"
        "To complete your subscription:\n\n"
        "1. Send ₦999 to our payment details\n"
        "2. Forward your receipt to @ratewatchng_support\n"
        "3. We'll activate your account within minutes\n\n"
        "_Automated payment coming soon._"
    )
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=premium_keyboard())


async def activate_premium(telegram_id: int) -> None:
    """Called by admin to manually grant premium. Also used by future payment webhook."""
    user = get_user(telegram_id)
    if user:
        update_user(user["$id"], {"plan": "premium"})
    create_or_renew_subscription(telegram_id, days=30)
