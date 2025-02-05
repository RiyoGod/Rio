from telegram import Update
from telegram.ext import CallbackContext
from config import LOG_GROUP_ID

async def start(update: Update, context: CallbackContext):
    user = update.effective_user
    user_id = user.id
    username = user.username or "No Username"
    first_name = user.first_name or "No Name"

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


    log_message = (
        f"📌 **New User Started the Bot**\n"
        f"👤 **Name:** {first_name}\n"
        f"📌 **User ID:** `{user_id}`\n"
        f"🔗 **Username:** @{username}" if user.username else "None"
    )

    # Send welcome message to the user
    await update.message.reply_text(welcome_message)

    # Send log message to the log group
    await context.bot.send_message(chat_id=LOG_GROUP_ID, text=log_message, parse_mode="Markdown")
