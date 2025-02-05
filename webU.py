import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from telegram import Bot

# Load environment variables from .env file
load_dotenv()

# Get API tokens from environment variables
CRYPTOBOT_SECRET = "335393:AAZMPAfpnvAFGLApXm4BTKVbxNAuTVxbd9t"
TELEGRAM_BOT_TOKEN = "7717505592:AAFprS-Sc-W34Sm2pfJ8srkPw1e91qbnoxY"

if not CRYPTOBOT_SECRET or not TELEGRAM_BOT_TOKEN:
    raise ValueError("Missing API tokens! Set CRYPTOBOT_SECRET and TELEGRAM_BOT_TOKEN in .env")

# Initialize Telegram bot
bot = Bot(token=TELEGRAM_BOT_TOKEN)

app = Flask(__name__)

@app.route('/webhook', methods=['POST', 'GET'])
def webhook():
    if request.method == 'GET':
        return "Webhook is active!", 200  # Respond with success for GET requests
    
    data = request.json  # Get JSON data from CryptoBot
    print("Received Data:", data)  # Debugging: Print received data
    
    # Example: If payment is successful, notify the user
    if data.get("status") == "paid":
        user_id = data.get("payload")  # Store user ID in 'payload' field
        amount = data.get("amount")
        asset = data.get("asset")
        invoice_id = data.get("invoice_id")
        
        message = f"✅ Payment Received!\n\n💰 Amount: {amount} {asset}\n🧾 Invoice ID: {invoice_id}"
        
        # Send a message to the user via Telegram bot
        bot.send_message(chat_id=user_id, text=message)

    return jsonify({"status": "ok"}), 200  # Respond with success

if name == '__main__':
    app.run(host="0.0.0.0", port=5000)
