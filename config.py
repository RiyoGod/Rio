import os
from dotenv import load_dotenv

load_dotenv()

CRYPTOBOT_SECRET = os.getenv("CRYPTOBOT_SECRET")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not CRYPTOBOT_SECRET or not TELEGRAM_BOT_TOKEN:
    raise ValueError("Missing API tokens! Set CRYPTOBOT_SECRET and TELEGRAM_BOT_TOKEN in .env")
