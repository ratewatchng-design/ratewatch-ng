"""
Weekly summary job — fires every Monday at 8 AM WAT.
Sent only to premium users.
"""

import logging
import asyncio
from telegram.ext import ContextTypes
from database.users_db import get_premium_users
from services.forex_service import get_all_forex
from services.crypto_service import get_all_crypto
from utils.formatting import fmt_price

logger = logging.getLogger(__name__)


async def send_weekly_summary(context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        forex, crypto = await asyncio.gather(get_all_forex(), get_all_crypto())
        rates = {**forex, **crypto}

        usd = rates.get("USDNGN", 0)
        eur = rates.get("EURNGN", 0)
        gbp = rates.get("GBPNGN", 0)
        usdt = rates.get("USDTNGN", 0)
        btc = rates.get("BTCNGN", 0)

        text = (
            f"📈 *Weekly Market Summary*\n\n"
            f"USD/NGN:  {fmt_price(usd)}\n"
            f"EUR/NGN:  {fmt_price(eur)}\n"
            f"GBP/NGN:  {fmt_price(gbp)}\n"
            f"USDT/NGN: {fmt_price(usdt)}\n"
            f"BTC/NGN:  {fmt_price(btc, 'BTCNGN')}\n\n"
            f"_Powered by RateWatch NG ⭐_"
        )

        premium_users = get_premium_users()
        for user in premium_users:
            try:
                await context.bot.send_message(
                    chat_id=user["telegram_id"],
                    text=text,
                    parse_mode="Markdown",
                )
            except Exception as e:
                logger.warning(f"Weekly summary failed for {user['telegram_id']}: {e}")

    except Exception as e:
        logger.error(f"Weekly summary job error: {e}", exc_info=True)
