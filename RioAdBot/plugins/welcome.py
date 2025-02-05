# plugins/welcome.py

from telegram import Update
from telegram.ext import CallbackContext

def start(update: Update, context: CallbackContext) -> None:
    # Get the name of the user who started the bot
    name = update.effective_user.first_name

    # Send the welcome message
    welcome_message = f"✨ Welcome to @MuzzxAdBot • {name}!\n\n" \
                      "To get started, use /purchase to buy a plan.\n\n" \
                      "Everything is fully automated, and your ads will go live immediately after payment confirmation.\n\n" \
                      "Start boosting your ads effortlessly! 🎯"
    
    update.message.reply_text(welcome_message)
  
