from telegram import Update
from telegram.ext import CallbackContext
import os

# ✅ Load Log Group ID safely
LOG_GROUP_ID = os.getenv("LOG_GROUP_ID")
if not LOG_GROUP_ID:
    raise ValueError("LOG_GROUP_ID is missing in the .env file")
LOG_GROUP_ID = int(LOG_GROUP_ID)  # Convert to integer

async def send_welcome_message(update: Update, context: CallbackContext):
    """Sends a welcome message and logs user details."""
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
