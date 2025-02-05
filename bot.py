import logging
import os
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from RioAdBot.plugins.welcome import start
from RioAdBot.plugins.purchase import purchase_command, button_handler

# Load environment variables
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

if TOKEN is None:
    raise ValueError("Bot token is not set in the .env file")

# Setup logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    app = Application.builder().token(TOKEN).build()

    # Command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("purchase", purchase_command))

    # Button handler (for inline keyboard clicks)
    app.add_handler(CallbackQueryHandler(button_handler))

    logger.info("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
