from telegram import Update
from telegram.ext import CallbackContext
from RioAdBot.plugins.welcome import log_user_to_group  # ✅ Correct function name

async def start_command(update: Update, context: CallbackContext):
    """Handles the /start command."""
    user = update.effective_user
    first_name = user.first_name

    # ✅ Short & Impactful Welcome Message
    welcome_message = (
        f"◆ **Hello, {first_name}!** ◆\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "**Welcome to @BoostAdvertBot!**\n"
        "Your premium advertising partner.\n\n"
        "**➜ What We Offer:**\n"
        "◆ Exclusive Ads\n"
        "◆ Affordable Plans\n"
        "◆ Secure Crypto Payments\n\n"
        "**➜ Get Started:**\n"
        "◆ Use **/purchase** to explore plans.\n"
        "◆ Need help? Contact **@Boostadvert**.\n"
        "━━━━━━━━━━━━━━━━━━━━━"
    )

    await update.message.reply_text(welcome_message, parse_mode="Markdown")

    # ✅ Log user to the group
    await log_user_to_group(update, context)  # ✅ Correct function call
