import logging
import os
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler
from RioAdBot.plugins.welcome import start  # Keep this import

# Load environment variables from .env file
load_dotenv()

# Get the bot token from environment variables
TOKEN = os.getenv('BOT_TOKEN')

if TOKEN is None:
    raise ValueError("Bot token is not set in the .env file")

# Enable logging for debugging purposes
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

async def start_command(update, context):
    """Handles the /start command."""
    await start(update, context)

async def purchase_command(update, context):
    """Handles the /purchase command."""
    from RioAdBot.plugins.purchase import purchase  # ✅ Move import inside function
    await purchase(update, context)

def main():
    # Create Application instance and pass the bot token
    app = Application.builder().token(TOKEN).build()

    # Add handlers for commands
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("purchase", purchase_command))

    # Start the Bot
    logger.info("Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()
