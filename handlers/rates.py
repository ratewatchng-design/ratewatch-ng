from telegram import Update
from telegram.ext import ContextTypes
from services.forex_service import get_all_forex
from services.crypto_service import get_all_crypto
from ui.rates_menu import rates_keyboard
from utils.formatting import fmt_price


def _build_rates_text(rates: dict) -> str:
    lines = ["*Current Rates*\n"]
    order = ["USDNGN", "EURNGN", "GBPNGN", "USDTNGN", "BTCNGN"]
    labels = {
        "USDNGN": "USD/NGN",
        "EURNGN": "EUR/NGN",
        "GBPNGN": "GBP/NGN",
        "USDTNGN": "USDT/NGN",
        "BTCNGN": "BTC/NGN",
    }
    for key in order:
        price = rates.get(key)
        if price:
            lines.append(f"{labels[key]}:  {fmt_price(price, key)}")
        else:
            lines.append(f"{labels[key]}:  —")
    return "\n".join(lines)


async def _fetch_all_rates() -> dict:
    import asyncio
    forex, crypto = await asyncio.gather(get_all_forex(), get_all_crypto())
    return {**forex, **crypto}


async def rates_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    rates = await _fetch_all_rates()
    text = _build_rates_text(rates)
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=rates_keyboard())


async def refresh_rates(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer("Refreshing...")
    rates = await _fetch_all_rates()
    text = _build_rates_text(rates)
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=rates_keyboard())


async def daily_summary_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    rates = await _fetch_all_rates()
    # For on-demand daily summary, we show current rates without change deltas
    lines = [
        "📊 *Daily Forex Summary*\n",
        f"USD/NGN\n{fmt_price(rates.get('USDNGN', 0))}",
        f"\nEUR/NGN\n{fmt_price(rates.get('EURNGN', 0))}",
        f"\nGBP/NGN\n{fmt_price(rates.get('GBPNGN', 0))}",
        f"\nUSDT/NGN\n{fmt_price(rates.get('USDTNGN', 0))}",
    ]
    await query.edit_message_text(
        "\n".join(lines),
        parse_mode="Markdown",
        reply_markup=rates_keyboard(),
    )
