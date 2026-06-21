"""
Daily summary job — fires every morning at 7 AM WAT.
Sends a concise rate summary to all users.
Includes rate change vs previous day (stored in bot_data).
"""

import logging
import asyncio
from telegram.ext import ContextTypes
from database.users_db import get_all_users
from services.forex_service import get_all_forex
from services.crypto_service import get_all_crypto
from utils.formatting import fmt_price

logger = logging.getLogger(__name__)

PREVIOUS_RATES_KEY = "previous_daily_rates"


def _delta_str(current: float, previous: float | None) -> str:
    if previous is None:
        return ""
    diff = current - previous
    sign = "+" if diff >= 0 else ""
    return f" ({sign}{fmt_price(diff)})"


async def send_daily_summary(context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        forex, crypto = await asyncio.gather(get_all_forex(), get_all_crypto())
        rates = {**forex, **crypto}
        previous: dict = context.bot_data.get(PREVIOUS_RATES_KEY, {})

        usd = rates.get("USDNGN", 0)
        eur = rates.get("EURNGN", 0)
        gbp = rates.get("GBPNGN", 0)
        usdt = rates.get("USDTNGN", 0)

        text = (
            f"📊 *Daily Forex Summary*\n\n"
            f"USD/NGN\n{fmt_price(usd)}{_delta_str(usd, previous.get('USDNGN'))}\n\n"
            f"EUR/NGN\n{fmt_price(eur)}{_delta_str(eur, previous.get('EURNGN'))}\n\n"
            f"GBP/NGN\n{fmt_price(gbp)}{_delta_str(gbp, previous.get('GBPNGN'))}\n\n"
            f"USDT/NGN\n{fmt_price(usdt)}{_delta_str(usdt, previous.get('USDTNGN'))}"
        )

        # Store current as tomorrow's previous
        context.bot_data[PREVIOUS_RATES_KEY] = rates

        users = get_all_users()
        for user in users:
            notif_style = user.get("notification_style", "instant")
            if notif_style == "digest":
                # Digest users only get the daily summary
                pass  # always send to digest users
            # Send to all users (free + premium)
            try:
                await context.bot.send_message(
                    chat_id=user["telegram_id"],
                    text=text,
                    parse_mode="Markdown",
                )
            except Exception as e:
                logger.warning(f"Daily summary failed for {user['telegram_id']}: {e}")

    except Exception as e:
        logger.error(f"Daily summary job error: {e}", exc_info=True)
