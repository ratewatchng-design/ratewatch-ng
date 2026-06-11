import logging
from datetime import datetime, timezone
from telegram import Bot, InlineKeyboardMarkup
from ui.alert_menu import triggered_alert_keyboard
from utils.formatting import fmt_price, fmt_asset_label, fmt_condition

logger = logging.getLogger(__name__)


async def send_alert_triggered(
    bot: Bot,
    telegram_id: int,
    alert: dict,
    current_price: float,
) -> None:
    asset_label = fmt_asset_label(alert["asset"])
    current_fmt = fmt_price(current_price, alert["asset"])
    target_fmt = fmt_price(alert["target"], alert["asset"])
    condition_label = fmt_condition(alert["condition"])
    time_str = datetime.now(timezone.utc).strftime("%H:%M")

    text = (
        f"🔔 *ALERT TRIGGERED*\n\n"
        f"*{asset_label}*\n\n"
        f"Current:  {current_fmt}\n"
        f"Target:   {target_fmt}\n"
        f"Condition: {condition_label}\n"
        f"Time:     {time_str}"
    )

    kb: InlineKeyboardMarkup = triggered_alert_keyboard(alert["$id"])

    try:
        await bot.send_message(
            chat_id=telegram_id,
            text=text,
            parse_mode="Markdown",
            reply_markup=kb,
        )
    except Exception as e:
        logger.error(f"Failed to send alert to {telegram_id}: {e}")


async def send_message(bot: Bot, telegram_id: int, text: str, **kwargs) -> None:
    try:
        await bot.send_message(chat_id=telegram_id, text=text, **kwargs)
    except Exception as e:
        logger.error(f"Failed to send message to {telegram_id}: {e}")
