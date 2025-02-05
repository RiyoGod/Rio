from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from config import TELEGRAM_BOT_TOKEN
from plugins.start import start
from plugins.purchase import purchase

def main():
    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("purchase", purchase))
    dp.add_handler(CallbackQueryHandler(purchase))  # Handles button clicks

    updater.start_polling()
    updater.idle()

if name == "main":
    main()
