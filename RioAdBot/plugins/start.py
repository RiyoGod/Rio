import logging
import os
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler
from RioAdBot.plugins.welcome import start
from RioAdBot.plugins.purchase import purchase

# Load environment variables from .env file
load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')

if TOKEN is None:
    raise ValueError("Bot token is not set in the .env file")

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("purchase", purchase))

    logger.info("Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()
