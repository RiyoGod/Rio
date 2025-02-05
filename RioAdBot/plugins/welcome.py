import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, CallbackContext
from RioAdBot.plugins.welcome import send_welcome_message  # ✅ Fixed Import
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

# ✅ Start command with logging
async def start_command(update: Update, context: CallbackContext):
    """Handles /start command and logs new users."""
    await send_welcome_message(update, context)  # ✅ Fixed Function Call

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
