"""
Crypto service — fetches USDT/NGN and BTC/NGN from Binance P2P / CoinGecko.
Uses CoinGecko as primary (free, no key needed).
"""

import logging
import httpx

logger = logging.getLogger(__name__)

COINGECKO_URL = (
    "https://api.coingecko.com/api/v3/simple/price"
    "?ids=tether,bitcoin&vs_currencies=ngn"
)


async def _fetch_crypto_ngn() -> dict | None:
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            resp = await client.get(COINGECKO_URL)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.error(f"CoinGecko fetch failed: {e}")
            return None


async def get_usdt_ngn() -> dict | None:
    data = await _fetch_crypto_ngn()
    if not data:
        return None
    price = data.get("tether", {}).get("ngn")
    return {"price": round(price, 2)} if price else None


async def get_btc_ngn() -> dict | None:
    data = await _fetch_crypto_ngn()
    if not data:
        return None
    price = data.get("bitcoin", {}).get("ngn")
    return {"price": round(price, 2)} if price else None


async def get_all_crypto() -> dict:
    """Returns both crypto rates in one API call."""
    data = await _fetch_crypto_ngn()
    result = {}
    if not data:
        return result
    usdt = data.get("tether", {}).get("ngn")
    btc = data.get("bitcoin", {}).get("ngn")
    if usdt:
        result["USDTNGN"] = round(usdt, 2)
    if btc:
        result["BTCNGN"] = round(btc, 2)
    return result
