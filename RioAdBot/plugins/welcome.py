import os
from telegram import Update
from telegram.ext import CallbackContext

# ✅ Load Log Group ID directly
LOG_GROUP_ID = os.getenv("LOG_GROUP_ID")
if not LOG_GROUP_ID:
    raise ValueError("LOG_GROUP_ID is missing in the .env file")

LOG_GROUP_ID = int(LOG_GROUP_ID)  # ✅ Convert to integer

async def log_new_user(update: Update, context: CallbackContext):
    """Logs when a user starts the bot."""
    user = update.effective_user
    first_name = user.first_name
    user_id = user.id
    username = f"@{user.username}" if user.username else "No Username"

    log_message = (
        f"📢 **New User Started the Bot**\n\n"
        f"👤 **Name:** {first_name}\n"
        f"🆔 **User ID:** `{user_id}`\n"
        f"🔗 **Username:** {username}"
    )

    await context.bot.send_message(chat_id=LOG_GROUP_ID, text=log_message, parse_mode="Markdown")
