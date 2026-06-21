"""
Alert checker — runs every 60 seconds.
Fetches all active alerts, evaluates conditions, fires notifications.
Respects user quiet hours and notification style.
"""

import asyncio
import logging
from datetime import datetime, timezone
from telegram.ext import ContextTypes
from database.alerts_db import get_all_active_alerts, deactivate_alert
from database.users_db import get_user
from services.forex_service import get_all_forex
from services.crypto_service import get_all_crypto
from services.notification_service import send_alert_triggered

logger = logging.getLogger(__name__)

# In-memory grouped alert buffer: {telegram_id: [(alert, price, timestamp)]}
_grouped_buffer: dict[int, list] = {}


def _is_quiet_hour(quiet_hours_setting: str) -> bool:
    """Returns True if current WAT time falls within quiet hours."""
    now_utc = datetime.now(timezone.utc)
    # WAT = UTC+1
    wat_hour = (now_utc.hour + 1) % 24
    if quiet_hours_setting == "10pm_6am":
        return wat_hour >= 22 or wat_hour < 6
    if quiet_hours_setting == "11pm_7am":
        return wat_hour >= 23 or wat_hour < 7
    return False


def _condition_met(condition: str, current: float, target: float) -> bool:
    if condition == "above":
        return current >= target
    if condition == "below":
        return current <= target
    if condition == "pct_up":
        # target stored as percentage e.g. 5.0 means +5%
        # We can't evaluate without a baseline here — skip for now
        return False
    if condition == "pct_down":
        return False
    return False


async def check_alerts(context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        alerts = get_all_active_alerts()
        if not alerts:
            return

        forex, crypto = await asyncio.gather(get_all_forex(), get_all_crypto())
        rates = {**forex, **crypto}

        for alert in alerts:
            asset = alert.get("asset", "")
            current = rates.get(asset)
            if current is None:
                continue

            condition = alert.get("condition", "above")
            target = float(alert.get("target", 0))

            if not _condition_met(condition, current, target):
                continue

            tg_id = alert["telegram_id"]
            user = get_user(tg_id)
            if not user:
                continue

            quiet_hours = user.get("quiet_hours", "off")
            if _is_quiet_hour(quiet_hours):
                continue

            notif_style = user.get("notification_style", "instant")

            if notif_style == "instant":
                await send_alert_triggered(context.bot, tg_id, alert, current)
                deactivate_alert(alert["$id"])

            elif notif_style == "grouped":
                _grouped_buffer.setdefault(tg_id, []).append((alert, current))
                deactivate_alert(alert["$id"])

            # digest style: handled by daily_summary job

        # Flush grouped buffer
        await _flush_grouped(context)

    except Exception as e:
        logger.error(f"Alert checker error: {e}", exc_info=True)


async def _flush_grouped(context: ContextTypes.DEFAULT_TYPE) -> None:
    from services.notification_service import send_message
    from utils.formatting import fmt_price, fmt_asset_label, fmt_condition

    for tg_id, items in list(_grouped_buffer.items()):
        if not items:
            continue
        lines = ["🔔 *Alerts Triggered*\n"]
        for alert, current in items:
            asset = fmt_asset_label(alert["asset"])
            cond = fmt_condition(alert["condition"])
            lines.append(
                f"• {asset} — {cond} {fmt_price(alert['target'], alert['asset'])}\n"
                f"  Current: {fmt_price(current, alert['asset'])}"
            )
        await send_message(context.bot, tg_id, "\n".join(lines), parse_mode="Markdown")
        _grouped_buffer[tg_id] = []
