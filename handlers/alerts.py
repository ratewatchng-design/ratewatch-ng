import logging
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from database.users_db import is_premium
from database.alerts_db import (
    get_user_alerts, create_alert, delete_alert,
    count_user_alerts, FREE_ALERT_LIMIT,
)
from services.forex_service import get_all_forex
from services.crypto_service import get_all_crypto
from ui.alert_menu import (
    asset_selection_keyboard, condition_selection_keyboard,
    pct_condition_keyboard, alert_created_keyboard,
    my_alerts_keyboard, remove_alert_keyboard,
)
from utils.formatting import fmt_price, fmt_asset_label, fmt_alert_short

logger = logging.getLogger(__name__)

# ConversationHandler states
CHOOSING_ASSET = 0
CHOOSING_CONDITION = 1
ENTERING_TARGET = 2

ASSET_LABELS = {
    "USDNGN": "🇺🇸 USD/NGN",
    "EURNGN": "🇪🇺 EUR/NGN",
    "GBPNGN": "🇬🇧 GBP/NGN",
    "USDTNGN": "💵 USDT/NGN",
    "BTCNGN": "🪙 BTC/NGN",
}

PREMIUM_ASSETS = {"EURNGN", "GBPNGN", "USDTNGN", "BTCNGN"}


async def new_alert_asset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    tg_id = update.effective_user.id

    premium = is_premium(tg_id)
    alert_count = count_user_alerts(tg_id)

    if not premium and alert_count >= FREE_ALERT_LIMIT:
        await query.edit_message_text(
            "⚠️ *Alert Limit Reached*\n\n"
            f"Free plan allows {FREE_ALERT_LIMIT} active alerts.\n\n"
            "Upgrade to ⭐ Premium for unlimited alerts.",
            parse_mode="Markdown",
            reply_markup=asset_selection_keyboard(),
        )
        return ConversationHandler.END

    await query.edit_message_text(
        "Choose an asset:",
        reply_markup=asset_selection_keyboard(),
    )
    return CHOOSING_ASSET


async def new_alert_condition(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    tg_id = update.effective_user.id

    asset = query.data.replace("asset_", "")
    premium = is_premium(tg_id)

    if asset in PREMIUM_ASSETS and not premium:
        await query.edit_message_text(
            f"⭐ *{fmt_asset_label(asset)} is a Premium asset*\n\n"
            "Upgrade to monitor EUR, GBP, USDT & BTC.",
            parse_mode="Markdown",
            reply_markup=asset_selection_keyboard(),
        )
        return CHOOSING_ASSET

    context.user_data["alert_asset"] = asset

    # Fetch current rate
    all_forex = await get_all_forex()
    all_crypto = await get_all_crypto()
    all_rates = {**all_forex, **all_crypto}
    current = all_rates.get(asset)
    rate_line = f"Current Rate: {fmt_price(current, asset)}" if current else ""

    label = fmt_asset_label(asset)
    await query.edit_message_text(
        f"*{label}*\n\n{rate_line}\n\nChoose condition:",
        parse_mode="Markdown",
        reply_markup=condition_selection_keyboard(asset),
    )
    return CHOOSING_CONDITION


async def new_alert_target(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    data = query.data  # cond_above / cond_below / cond_pct
    if data == "cond_pct":
        await query.edit_message_text(
            "Choose percentage direction:",
            reply_markup=pct_condition_keyboard(),
        )
        return CHOOSING_CONDITION

    condition = data.replace("cond_", "")
    context.user_data["alert_condition"] = condition

    asset = context.user_data.get("alert_asset", "")
    label = fmt_asset_label(asset)
    is_btc = asset == "BTCNGN"
    example = "180000000\n190000000" if is_btc else "1700\n1750\n1800"

    cond_word = "above" if "above" in condition else "below"
    if "pct" in condition:
        await query.edit_message_text(
            "Enter the percentage change to trigger the alert.\n\n"
            "Example:\n5\n10\n15"
        )
    else:
        await query.edit_message_text(
            f"Enter target price for {label} ({cond_word}).\n\n"
            f"Example:\n{example}"
        )
    return ENTERING_TARGET


async def confirm_remove_alert(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receives the typed target price and saves the alert."""
    text = update.message.text.strip().replace(",", "").replace("₦", "")
    tg_id = update.effective_user.id
    asset = context.user_data.get("alert_asset", "")
    condition = context.user_data.get("alert_condition", "above")

    try:
        target = float(text)
    except ValueError:
        await update.message.reply_text(
            "❌ Invalid number. Please enter a numeric price (e.g. 1750):"
        )
        return ENTERING_TARGET

    # Save alert
    create_alert(tg_id, asset, condition, target)

    label = fmt_asset_label(asset)
    symbol = ">" if condition in ("above", "pct_up") else "<"
    price_fmt = fmt_price(target, asset)

    await update.message.reply_text(
        f"✅ *Alert Created*\n\n"
        f"{label} {symbol} {price_fmt}\n\n"
        f"You'll be notified immediately.",
        parse_mode="Markdown",
        reply_markup=alert_created_keyboard(),
    )
    context.user_data.clear()
    return ConversationHandler.END


async def my_alerts_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    tg_id = update.effective_user.id

    alerts = get_user_alerts(tg_id)

    if not alerts:
        await query.edit_message_text(
            "📋 *My Alerts*\n\nYou have no active alerts.\n\nTap ➕ to create one.",
            parse_mode="Markdown",
            reply_markup=my_alerts_keyboard(),
        )
        return

    lines = "\n".join(
        f"{i + 1}. {fmt_alert_short(a)}" for i, a in enumerate(alerts)
    )
    await query.edit_message_text(
        f"📋 *Your Active Alerts*\n\n{lines}",
        parse_mode="Markdown",
        reply_markup=my_alerts_keyboard(),
    )


async def remove_alert_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    tg_id = update.effective_user.id
    data = query.data

    # Direct delete from triggered alert message
    if data.startswith("delete_alert_"):
        alert_id = data.replace("delete_alert_", "")
        try:
            delete_alert(alert_id)
        except Exception as e:
            logger.error(f"Delete alert error: {e}")
        alerts = get_user_alerts(tg_id)
        if not alerts:
            await query.edit_message_text(
                "✅ Alert deleted.\n\nYou have no remaining alerts.",
                reply_markup=my_alerts_keyboard(),
            )
            return
        lines = "\n".join(f"{i + 1}. {fmt_alert_short(a)}" for i, a in enumerate(alerts))
        await query.edit_message_text(
            f"✅ Alert deleted.\n\n📋 *Remaining Alerts*\n\n{lines}",
            parse_mode="Markdown",
            reply_markup=my_alerts_keyboard(),
        )
        return

    # Show removal picker
    alerts = get_user_alerts(tg_id)
    if not alerts:
        await query.edit_message_text(
            "You have no active alerts to remove.",
            reply_markup=my_alerts_keyboard(),
        )
        return

    await query.edit_message_text(
        "Select alert to delete:",
        reply_markup=remove_alert_keyboard(alerts),
    )
