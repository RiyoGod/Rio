# start.py

import logging
import os
from dotenv import load_dotenv
from telegram.ext import Updater, CommandHandler
from RioAdBot.plugins.welcome import start
from RioAdBot.plugins.purchase import purchase

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

def main():
    # Create Updater and pass your bot's token
    updater = Updater(TOKEN)

    # Register the dispatcher to add handlers for commands
    dispatcher = updater.dispatcher

    # Add handlers for commands
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("purchase", purchase))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you stop it manually (Ctrl + C)
    updater.idle()

if __name__ == '__main__':
    main()
