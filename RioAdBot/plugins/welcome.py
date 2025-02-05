from telegram import Update
from telegram.ext import CallbackContext

# ✅ Directly Set Log Group ID (Replace with your actual log group ID)
LOG_GROUP_ID = -1002314243507  # <-- Replace this with your actual group ID

async def start_command(update: Update, context: CallbackContext):
    """Handles the /start command and logs the user to a group."""
    user = update.effective_user
    first_name = user.first_name
    user_id = user.id
    username = f"@{user.username}" if user.username else "No Username"

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

    # ✅ Log Message
    log_message = (
        f"📢 **New User Started the Bot**\n\n"
        f"👤 **Name:** {first_name}\n"
        f"🆔 **User ID:** `{user_id}`\n"
        f"🔗 **Username:** {username}"
    )
    await context.bot.send_message(chat_id=LOG_GROUP_ID, text=log_message, parse_mode="Markdown")
