import logging
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext

from RioAdBot.plugins.welcome import start  # ✅ Import welcome message

# Load environment variables
load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')

if TOKEN is None:
    raise ValueError("Bot token is not set in the .env file")

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# ✅ Updated: Directly handle the /purchase command
async def purchase_command(update: Update, context: CallbackContext):
    """Handles the /purchase command without show_plans."""
    message = (
        "> **Choose Your Plan!!**\n\n"
        "▫ **Basic Plan**\n"
        "**├ Accounts: 1**\n"
        "**├ Intervals: 5 min**\n"
        "**•|  Price: $40/week | $100/month |•**\n\n"
        "**▫ Premium Plan**\n"
        "**├ Accounts: 4**\n"
        "**├ Intervals: 30 sec**\n"
        "**•| Price: $250/week | $500/month |•**\n\n"
        "**▫ Immortal Plan**\n"
        "**├ Accounts: 10**\n"
        "**├ Intervals: 60 sec**\n"
        "**•| Price: $500/week | $1000/month |•**\n\n"
        "---\n\n"
        "> Select a Plan to Continue Via Below Buttons!\n\n"
        "For support, contact @Boostadvert."
    )
    await update.message.reply_text(message, parse_mode="Markdown")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("purchase", purchase_command))  # ✅ No more show_plans

    logger.info("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
