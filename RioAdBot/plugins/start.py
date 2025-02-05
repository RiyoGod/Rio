from telegram import Update
from telegram.ext import CallbackContext
from RioAdBot.plugins.welcome import log_user_to_group  # ✅ Correct function name

async def start_command(update: Update, context: CallbackContext):
    """Handles the /start command."""
    user = update.effective_user
    first_name = user.first_name

    # ✅ Welcome Message
    welcome_message = (
        f"**Hello, {first_name}!**\n"
        "Welcome to **@BoostAdvertBot**, your go-to advertising solution.\n\n"
        "✨ *What can I do for you?*\n"
        "- **Exclusive advertising services**\n"
        "- **Premium & affordable plans**\n"
        "- **Secure crypto payments**\n\n"
        "__Get started now!__\n"
        "Use **/purchase** to explore our plans and begin.\n\n"
        "Need help? Contact **@Boostadvert** for support."
    )

    await update.message.reply_text(welcome_message, parse_mode="Markdown")

    # ✅ Log user to the group
    await log_user_to_group(update, context)  # ✅ Correct function call
