import logging
import asyncio
import os
from datetime import time as dtime
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, ConversationHandler, filters
)
from handlers.start import start_handler, help_handler
from handlers.alerts import (
    new_alert_asset, new_alert_condition, new_alert_target,
    my_alerts_handler, remove_alert_handler, confirm_remove_alert,
    CHOOSING_ASSET, CHOOSING_CONDITION, ENTERING_TARGET
)
from handlers.rates import rates_handler, refresh_rates, daily_summary_handler
from handlers.premium import premium_handler, subscribe_handler
from handlers.referrals import referrals_handler
from handlers.settings import (
    settings_handler, notif_style_handler, set_notif_style,
    quiet_hours_handler, set_quiet_hours
)
from handlers.admin import admin_handler, users_handler, broadcast_handler
from jobs.alert_checker import check_alerts
from jobs.daily_summary import send_daily_summary
from jobs.weekly_summary import send_weekly_summary
from utils.config import BOT_TOKEN
import pytz

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def main() -> None:
    app = Application.builder().token(BOT_TOKEN).build()

    # Conversation handler for alert creation
    alert_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(new_alert_asset, pattern="^new_alert$")],
        states={
            CHOOSING_ASSET: [CallbackQueryHandler(new_alert_condition, pattern="^asset_")],
            CHOOSING_CONDITION: [CallbackQueryHandler(new_alert_target, pattern="^cond_")],
            ENTERING_TARGET: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_remove_alert)
            ],
        },
        fallbacks=[CallbackQueryHandler(start_handler, pattern="^home$")],
        per_message=False,
        per_chat=True,
    )

    # Commands
    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("help", help_handler))
    app.add_handler(CommandHandler("admin", admin_handler))
    app.add_handler(CommandHandler("users", users_handler))
    app.add_handler(CommandHandler("broadcast", broadcast_handler))

    # Conversation
    app.add_handler(alert_conv)

    # Callback queries
    app.add_handler(CallbackQueryHandler(start_handler, pattern="^home$"))
    app.add_handler(CallbackQueryHandler(my_alerts_handler, pattern="^my_alerts$"))
    app.add_handler(CallbackQueryHandler(remove_alert_handler, pattern="^remove_alert$"))
    app.add_handler(CallbackQueryHandler(remove_alert_handler, pattern="^delete_alert_"))
    app.add_handler(CallbackQueryHandler(rates_handler, pattern="^rates$"))
    app.add_handler(CallbackQueryHandler(refresh_rates, pattern="^refresh_rates$"))
    app.add_handler(CallbackQueryHandler(daily_summary_handler, pattern="^daily_summary$"))
    app.add_handler(CallbackQueryHandler(premium_handler, pattern="^premium$"))
    app.add_handler(CallbackQueryHandler(subscribe_handler, pattern="^subscribe$"))
    app.add_handler(CallbackQueryHandler(referrals_handler, pattern="^referrals$"))
    app.add_handler(CallbackQueryHandler(settings_handler, pattern="^settings$"))
    app.add_handler(CallbackQueryHandler(notif_style_handler, pattern="^notif_style$"))
    app.add_handler(CallbackQueryHandler(set_notif_style, pattern="^style_"))
    app.add_handler(CallbackQueryHandler(quiet_hours_handler, pattern="^quiet_hours$"))
    app.add_handler(CallbackQueryHandler(set_quiet_hours, pattern="^qh_"))

    # Scheduled jobs
    job_queue = app.job_queue
    tz = pytz.timezone("Africa/Lagos")

    job_queue.run_repeating(check_alerts, interval=60, first=10)
    job_queue.run_daily(send_daily_summary, time=dtime(7, 0, tzinfo=tz))
    job_queue.run_daily(send_weekly_summary, time=dtime(8, 0, tzinfo=tz), days=(0,))

    # Webhook
    hostname = os.environ.get("RENDER_EXTERNAL_HOSTNAME", "")
    webhook_url = f"https://{hostname}/webhook"
    logger.info("RateWatch NG starting — webhook: %s", webhook_url)

    async with app:
        await app.bot.set_webhook(
            url=webhook_url,
            drop_pending_updates=True,
        )
        await app.start()
        await app.updater.start_webhook(
            listen="0.0.0.0",
            port=8000,
            url_path="/webhook",
        )
        # Run forever
        await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
