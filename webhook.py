import requests
from flask import Flask, request, jsonify
from telegram import Bot

# 🔹 Your API Keys
TELEGRAM_BOT_TOKEN = "7717505592:AAFprS-Sc-W34Sm2pfJ8srkPw1e91qbnoxY"
CRYPTOBOT_SECRET = "335393:AAZMPAfpnvAFGLApXm4BTKVbxNAuTVxbd9t"

# 🔹 Initialize Flask & Telegram Bot
app = Flask(name)
bot = Bot(token=TELEGRAM_BOT_TOKEN)

# 🔹 Webhook Route (Must Allow POST Requests)
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json  # Get JSON data from CryptoBot

    if not data or "invoice_id" not in data:
        return jsonify({"error": "Invalid data"}), 400

    invoice_id = data["invoice_id"]
    amount = data["amount"]
    currency = data["asset"]
    status = data["status"]
    user_id = data["payload"]  # Telegram User ID from Invoice

    if status == "paid":
        bot.send_message(chat_id=user_id, text=f"✅ Payment of {amount} {currency} received! Your service is now active.")

    return jsonify({"status": "ok"}), 200

# 🔹 Run Flask Webhook Server
if name == 'main':
    app.run(host="0.0.0.0", port=5000)
