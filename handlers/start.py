from telegram import Update
from telegram.ext import ContextTypes
from database.users_db import get_or_create_user, is_premium
from database.alerts_db import count_user_alerts, FREE_ALERT_LIMIT
from database.referrals_db import record_referral
from ui.main_menu import main_menu_keyboard
from utils.formatting import fmt_price
from services.forex_service import get_usd_ngn


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    tg_id = user.id

    # Register / fetch user
    get_or_create_user(tg_id, user.username or "", user.first_name or "")

    # Handle referral deep link: /start <referrer_id>
    args = context.args or []
    if args:
        try:
            referrer_id = int(args[0])
            if referrer_id != tg_id:
                record_referral(referrer_id, tg_id)
        except (ValueError, TypeError):
            pass

    premium = is_premium(tg_id)
    alert_count = count_user_alerts(tg_id)
    limit = "∞" if premium else str(FREE_ALERT_LIMIT)

    # Try to show live USD rate in header
    rate_data = await get_usd_ngn()
    rate_line = f"USD/NGN: {fmt_price(rate_data['price'])}" if rate_data else "USD/NGN: Loading..."

    text = (
        f"📈 *RateWatch NG*\n\n"
        f"Active Alerts: {alert_count}/{limit}\n"
        f"{rate_line}\n\n"
        f"Choose an option:"
    )

    kb = main_menu_keyboard()

    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)
    else:
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=kb)


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (
        "*RateWatch NG — Help*\n\n"
        "Track USD, EUR, GBP, USDT & BTC rates against the Naira.\n\n"
        "*/start* — Open main menu\n"
        "*/help* — Show this message\n\n"
        "*Free plan:* 3 alerts, USD only, 30-min polling\n"
        "*Premium:* Unlimited alerts, all assets, instant polling\n\n"
        "Tap ⭐ Premium in the menu to upgrade."
    )
    await update.message.reply_text(text, parse_mode="Markdown")
