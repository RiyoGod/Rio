import os
import logging
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler
from RioAdBot.plugins.start import start_command
from RioAdBot.plugins.welcome import log_user_to_group  # ✅ Correct function name


# ✅ Load environment variables
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
LOG_GROUP_ID = os.getenv("LOG_GROUP_ID")

if not TOKEN:
    raise ValueError("BOT_TOKEN is missing in the .env file")
if not LOG_GROUP_ID:
    raise ValueError("LOG_GROUP_ID is missing in the .env file")
LOG_GROUP_ID = int(LOG_GROUP_ID)

# ✅ Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ✅ Start command with logging
async def start_and_log(update, context):
    """Handles /start and logs new users."""
    await start_command(update, context)  # Send welcome message
    await log_new_user(update, context)   # Log user to group

# ✅ Main function
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start_and_log))
    logger.info("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
