from telegram import Update
from telegram.ext import CallbackContext

async def start(update: Update, context: CallbackContext) -> None:
    """Handles the /start command and sends a welcome message."""
    name = update.effective_user.first_name

    welcome_message = (
        f"✨ Welcome to @MuzzxAdBot • {name}!\n\n"
        "To get started, use /purchase to buy a plan.\n\n"
        "Everything is fully automated, and your ads will go live immediately after payment confirmation.\n\n"
        "Start boosting your ads effortlessly! 🎯"
    )
    
    await update.message.reply_text(welcome_message)
