

import logging
import os
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler
from telegram import Update
from telegram.ext import CallbackContext

async def start_command(update: Update, context: CallbackContext):
    """Handles the /start command."""
    user = update.effective_user
    first_name = user.first_name

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

    await update.message.reply_text(welcome_message, parse_mode="Markdown")


# Load environment variables
load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')

if TOKEN is None:
    raise ValueError("Bot token is not set in the .env file")

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

async def purchase_command(update, context):
    """Handles the /purchase command."""
    from RioAdBot.plugins.purchase import show_plans  # Lazy import
    await show_plans(update, context)



def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("purchase", purchase_command))

    logger.info("Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()
