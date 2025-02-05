from telegram.ext import Application, CommandHandler
from RioAdBot.plugins.welcome import start  # ✅ Import directly from welcome.py
from RioAdBot.plugins.start import purchase_command  # ✅ Import the function

TOKEN = "7717505592:AAFprS-Sc-W34Sm2pfJ8srkPw1e91qbnoxY"

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("purchase", purchase_command))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
