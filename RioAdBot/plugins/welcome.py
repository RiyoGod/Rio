from telegram import Update
from telegram.ext import CallbackContext

# ✅ Hardcoded Log Group ID
LOG_GROUP_ID = -1002314243507  # Replace with your actual log group ID

async def log_user_to_group(update: Update, context: CallbackContext):
    """Logs the user who starts the bot to a group."""
    user = update.effective_user
    first_name = user.first_name
    user_id = user.id
    username = f"@{user.username}" if user.username else "No Username"

    # ✅ Log Message
    log_message = (
        f"📢 **New User Started the Bot**\n\n"
        f"👤 **Name:** {first_name}\n"
        f"🆔 **User ID:** `{user_id}`\n"
        f"🔗 **Username:** {username}"
    )

    await context.bot.send_message(chat_id=LOG_GROUP_ID, text=log_message, parse_mode="Markdown")
