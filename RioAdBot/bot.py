from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from RioAdBot.plugins.start import start
from RioAdBot.plugins.purchase import purchase

def main():
    updater = Updater("7717505592:AAFprS-Sc-W34Sm2pfJ8srkPw1e91qbnoxY", use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("purchase", purchase))

    updater.start_polling()
    updater.idle()

if name == "main":
    main()
