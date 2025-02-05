from telegram import Update
from telegram.ext import CallbackContext

async def start_command(update: Update, context: CallbackContext):  # ✅ Fixed name

    """Handles the /start command."""
    user = update.effective_user
    first_name = user.first_name

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
