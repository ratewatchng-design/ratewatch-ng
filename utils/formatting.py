def fmt_price(value: float, asset: str = "") -> str:
    """Format a price value with naira symbol and commas."""
    if asset == "BTCNGN" or value >= 1_000_000:
        return f"₦{value:,.0f}"
    return f"₦{value:,.0f}"


def fmt_asset_label(asset: str) -> str:
    mapping = {
        "USDNGN": "USD/NGN",
        "EURNGN": "EUR/NGN",
        "GBPNGN": "GBP/NGN",
        "USDTNGN": "USDT/NGN",
        "BTCNGN": "BTC/NGN",
    }
    return mapping.get(asset, asset)


def fmt_condition(condition: str) -> str:
    mapping = {
        "above": "Above Price",
        "below": "Below Price",
        "pct_up": "% Increase",
        "pct_down": "% Decrease",
    }
    return mapping.get(condition, condition)


def fmt_condition_symbol(condition: str) -> str:
    mapping = {
        "above": ">",
        "below": "<",
        "pct_up": "↑",
        "pct_down": "↓",
    }
    return mapping.get(condition, "")


def fmt_alert_short(alert: dict) -> str:
    asset = fmt_asset_label(alert["asset"])
    symbol = fmt_condition_symbol(alert["condition"])
    price = fmt_price(alert["target"], alert["asset"])
    return f"{asset} {symbol} {price}"
