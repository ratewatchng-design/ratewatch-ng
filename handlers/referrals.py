from telegram import Update
from telegram.ext import ContextTypes
from database.referrals_db import get_referral_count
from ui.referral_menu import referral_keyboard

REFERRAL_REWARDS = {
    1: "+1 alert slot",
    3: "+3 alert slots",
    10: "30 days Premium 🎉",
}


async def referrals_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    tg_id = update.effective_user.id

    count = get_referral_count(tg_id)
    bot_username = (await context.bot.get_me()).username
    ref_link = f"https://t.me/{bot_username}?start={tg_id}"

    reward_lines = "\n".join(
        f"• {n} referral{'s' if n > 1 else ''} → {reward}"
        for n, reward in REFERRAL_REWARDS.items()
    )

    text = (
        f"🎁 *Referral Programme*\n\n"
        f"Your referrals: *{count}*\n\n"
        f"Share your link:\n`{ref_link}`\n\n"
        f"*Rewards:*\n{reward_lines}"
    )
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=referral_keyboard())
