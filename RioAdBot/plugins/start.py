from telegram import Update
from telegram.ext import CallbackContext
from RioAdBot.plugins.welcome import log_user_to_group  # ✅ Correct function name

async def start_command(update: Update, context: CallbackContext):
    """Handles the /start command."""
    user = update.effective_user
    first_name = user.first_name

    # ✅ Short & Fully Bold Welcome Message
    welcome_message = (
        f"**Hello, {first_name}!**\n"
        "**Welcome to @BoostAdvertBot – the ultimate ad automation tool.**\n\n"
        "**Why Choose Us?**\n"
        "**- Automated & targeted advertising**\n"
        "**- Affordable promotion plans**\n"
        "**- Secure crypto payments**\n\n"
        "**Get Started:**\n"
        "**Use /purchase to buy ad plans.**\n"
        "**Need help? Contact @Boostadvert.**"
    )

    await update.message.reply_text(welcome_message, parse_mode="Markdown")

    # ✅ Log user to the group
    await log_user_to_group(update, context)  # ✅ Correct function call
