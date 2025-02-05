import logging
import os
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler
from RioAdBot.plugins.purchase import purchase  # ✅ Direct import

# Load environment variables from .env file
load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')

if TOKEN is None:
    raise ValueError("Bot token is not set in the .env file")

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update, context):
    """Handles the /start command."""
    await update.message.reply_text("Welcome! Use /purchase to buy a plan.")

async def purchase_command(update, context):
    """Handles the /purchase command."""
    await purchase(update, context)  # ✅ Call purchase directly

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("purchase", purchase_command))

    logger.info("Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()
