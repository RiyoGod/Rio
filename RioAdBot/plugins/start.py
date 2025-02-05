import logging
import os
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler
from RioAdBot.plugins import get_start, get_purchase  # ✅ Use lazy import functions

# Load environment variables from .env file
load_dotenv()

TOKEN = os.getenv('BOT_TOKEN')
if TOKEN is None:
    raise ValueError("Bot token is not set in the .env file")

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

async def start_command(update, context):
    """Handles the /start command."""
    start = get_start()
    await start(update, context)

async def purchase_command(update, context):
    """Handles the /purchase command."""
    purchase = get_purchase()
    await purchase(update, context)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("purchase", purchase_command))

    logger.info("Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()
