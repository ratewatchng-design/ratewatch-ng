"""
Forex service — fetches NGN rates from ExchangeRate-API (free tier).
Falls back to a secondary source if the primary fails.
"""

import logging
import httpx

logger = logging.getLogger(__name__)

PRIMARY_URL = "https://open.er-api.com/v6/latest/USD"
FALLBACK_URL = "https://api.exchangerate-api.com/v4/latest/USD"

_cache: dict = {}


async def _fetch_usd_base() -> dict | None:
    """Fetch all rates with USD as base. Returns raw rates dict."""
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            resp = await client.get(PRIMARY_URL)
            resp.raise_for_status()
            data = resp.json()
            rates = data.get("rates", {})
            if "NGN" in rates:
                return rates
        except Exception as e:
            logger.warning(f"Primary forex fetch failed: {e}")

        try:
            resp = await client.get(FALLBACK_URL)
            resp.raise_for_status()
            data = resp.json()
            return data.get("rates", {})
        except Exception as e:
            logger.error(f"Fallback forex fetch failed: {e}")
            return None


async def get_usd_ngn() -> dict | None:
    rates = await _fetch_usd_base()
    if not rates:
        return None
    ngn = rates.get("NGN")
    return {"price": round(ngn, 2)} if ngn else None


async def get_eur_ngn() -> dict | None:
    rates = await _fetch_usd_base()
    if not rates:
        return None
    usd_ngn = rates.get("NGN")
    eur_usd = rates.get("EUR")
    if not usd_ngn or not eur_usd:
        return None
    # EUR/NGN = (USD/NGN) / (EUR/USD)
    eur_ngn = usd_ngn / eur_usd
    return {"price": round(eur_ngn, 2)}


async def get_gbp_ngn() -> dict | None:
    rates = await _fetch_usd_base()
    if not rates:
        return None
    usd_ngn = rates.get("NGN")
    gbp_usd = rates.get("GBP")
    if not usd_ngn or not gbp_usd:
        return None
    gbp_ngn = usd_ngn / gbp_usd
    return {"price": round(gbp_ngn, 2)}


async def get_all_forex() -> dict:
    """Returns all forex rates in one call (single API hit)."""
    rates = await _fetch_usd_base()
    result = {}
    if not rates:
        return result
    usd_ngn = rates.get("NGN")
    if usd_ngn:
        result["USDNGN"] = round(usd_ngn, 2)
    eur = rates.get("EUR")
    if eur and usd_ngn:
        result["EURNGN"] = round(usd_ngn / eur, 2)
    gbp = rates.get("GBP")
    if gbp and usd_ngn:
        result["GBPNGN"] = round(usd_ngn / gbp, 2)
    return result
