from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from RioAdBot.plugins.start import start
from RioAdBot.plugins.purchase import purchase, button_handler

TOKEN = "7717505592:AAFprS-Sc-W34Sm2pfJ8srkPw1e91qbnoxY"

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("purchase", purchase))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
