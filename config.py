import os
from dotenv import load_dotenv

load_dotenv()

CRYPTOBOT_SECRET = os.getenv("CRYPTOBOT_SECRET" , "335393:AAZMPAfpnvAFGLApXm4BTKVbxNAuTVxbd9t")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN" , "7717505592:AAFprS-Sc-W34Sm2pfJ8srkPw1e91qbnoxY")
BOT_TOKEN = os.getenv("BOT_TOKEN" , "7717505592:AAFprS-Sc-W34Sm2pfJ8srkPw1e91qbnoxY")

if not CRYPTOBOT_SECRET or not TELEGRAM_BOT_TOKEN:
    raise ValueError("Missing API tokens! Set CRYPTOBOT_SECRET and TELEGRAM_BOT_TOKEN in .env")
