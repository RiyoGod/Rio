import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, CallbackContext
from RioAdBot.plugins.welcome import start
from RioAdBot.plugins.purchase import purchase_command, button_handler

# ✅ Load environment variables
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
LOG_GROUP_ID = os.getenv("LOG_GROUP_ID")

# ✅ Validate environment variables
if not TOKEN:
    raise ValueError("BOT_TOKEN is missing in the .env file")
if not LOG_GROUP_ID:
    raise ValueError("LOG_GROUP_ID is missing in the .env file")
LOG_GROUP_ID = int(LOG_GROUP_ID)  # Convert to integer

# ✅ Logging setup
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ✅ Function to log new users
async def log_new_user(update: Update, context: CallbackContext):
    """Logs when a user starts the bot."""
    user = update.message.from_user
    log_message = (
        f"📢 **New User Started the Bot**\n\n"
        f"🆔 **User ID:** `{user.id}`\n"
        f"👤 **Username:** @{user.username if user.username else 'N/A'}\n"
        f"📛 **Name:** {user.full_name}"
    )
    
    # ✅ Send log to the log group
    await context.bot.send_message(chat_id=LOG_GROUP_ID, text=log_message, parse_mode="Markdown")

# ✅ Start command with logging
async def start_command(update: Update, context: CallbackContext):
    """Handles /start command and logs new users."""
    await start(update, context)  # Call the existing start function
    await log_new_user(update, context)  # Log the user

# ✅ Main function
def main():
    app = Application.builder().token(TOKEN).build()
    
    # ✅ Handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("purchase", purchase_command))
    app.add_handler(CallbackQueryHandler(button_handler))

    logger.info("Bot is running...")
    app.run_polling()

# ✅ Run the bot
if __name__ == "__main__":
    main()
