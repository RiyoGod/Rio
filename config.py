import os
from dotenv import load_dotenv

load_dotenv()

CRYPTOBOT_SECRET = os.getenv("CRYPTOBOT_SECRET" , "335607:AA3yJu1fkPWWbczmD6hw8uesXCiAwzIJWm1")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN" , "7717505592:AAFprS-Sc-W34Sm2pfJ8srkPw1e91qbnoxY")
BOT_TOKEN = os.getenv("BOT_TOKEN" , "7717505592:AAFprS-Sc-W34Sm2pfJ8srkPw1e91qbnoxY")
LOG_GROUP_ID = os.getenv("LOG_GROUP_ID")


if LOG_GROUP_ID is None:
    raise ValueError("LOG_GROUP_ID is missing in the .env file")

LOG_GROUP_ID = int(LOG_GROUP_ID)  # ✅ Safe conversion

if not CRYPTOBOT_SECRET or not TELEGRAM_BOT_TOKEN:
    raise ValueError("Missing API tokens! Set CRYPTOBOT_SECRET and TELEGRAM_BOT_TOKEN in .env")

LOG_GROUP_ID = -1002314243507  # Replace with your log group's chat ID
