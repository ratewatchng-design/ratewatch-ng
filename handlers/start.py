import logging
from telegram import Update
from telegram.ext import ContextTypes
from database.users_db import get_user, get_or_create_user, is_premium
from database.alerts_db import count_user_alerts, FREE_ALERT_LIMIT
from database.referrals_db import record_referral
from ui.main_menu import main_menu_keyboard
from utils.formatting import fmt_price
from services.forex_service import get_usd_ngn

logger = logging.getLogger(__name__)


async def _build_main_menu_text() -> tuple[str, object]:
    """Builds the shared main-menu text + keyboard. Used by both
    start_handler (after registration) and main_menu_handler (home button)."""
    rate_data = await get_usd_ngn()
    rate_line = f"USD/NGN: {fmt_price(rate_data['price'])}" if rate_data else "USD/NGN: Loading..."
    return rate_line


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handles the /start command only.
    Registers the user in Appwrite ONLY if they don't already exist —
    checked explicitly so we never silently create duplicate documents
    for the same telegram_id on repeat /start presses.
    Then hands off to the same menu rendering used by main_menu_handler.
    """
    user = update.effective_user
    tg_id = user.id

    try:
        existing = get_user(tg_id)
    except Exception as e:
        logger.error(f"Could not verify if user {tg_id} exists: {e}")
        await update.message.reply_text(
            "⚠️ We're having trouble reaching our database right now. "
            "Please try /start again in a moment."
        )
        return

    if existing is None:
        # Brand new user — register them once.
        get_or_create_user(tg_id, user.username or "", user.first_name or "")

        # Handle referral deep link: /start <referrer_id> — only on first join
        args = context.args or []
        if args:
            try:
                referrer_id = int(args[0])
                if referrer_id != tg_id:
                    record_referral(referrer_id, tg_id)
            except (ValueError, TypeError):
                pass

    # Whether new or returning, show the main menu the same way.
    await _render_main_menu(update, context)


async def main_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handles the 🏠 Main Menu / 'home' callback button only.
    Does NOT touch the database for user creation — the user is assumed
    to already be registered since they could only reach this button
    after a successful /start.
    """
    await _render_main_menu(update, context)


async def _render_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    tg_id = update.effective_user.id

    premium = is_premium(tg_id)
    alert_count = count_user_alerts(tg_id)
    limit = "∞" if premium else str(FREE_ALERT_LIMIT)

    rate_line = await _build_main_menu_text()

    text = (
        f"📈 *RateWatch NG*\n\n"
        f"Active Alerts: {alert_count}/{limit}\n"
        f"{rate_line}\n\n"
        f"Choose an option:"
    )

    kb = main_menu_keyboard()

    if update.callback_query:
        await update.callback_query.answer()
        try:
            await update.callback_query.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)
        except Exception as e:
            if "not modified" not in str(e).lower():
                raise
    else:
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=kb)


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (
        "*RateWatch NG — Help*\n\n"
        "Track USD, EUR, GBP, USDT & BTC rates against the Naira.\n\n"
        "*/start* — Register & open main menu\n"
        "*/help* — Show this message\n\n"
        "*Free plan:* 3 alerts, USD only, 30-min polling\n"
        "*Premium:* Unlimited alerts, all assets, instant polling\n\n"
        "Tap ⭐ Premium in the menu to upgrade."
    )
    await update.message.reply_text(text, parse_mode="Markdown")
