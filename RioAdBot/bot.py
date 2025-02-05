from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from RioAdBot.plugins.start import start
from RioAdBot.plugins.purchase import purchase

TOKEN = "7717505592:AAFprS-Sc-W34Sm2pfJ8srkPw1e91qbnoxY"

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("purchase", purchase))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
