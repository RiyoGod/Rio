from flask import Flask, request, jsonify
from telegram import Bot
import os

TOKEN = "7717505592:AAFprS-Sc-W34Sm2pfJ8srkPw1e91qbnoxY"
CRYPTO_SECRET = "335393:AAdkGGk4TEr8Hna2sWFGDhveyhXe6nSUbM2"  # Set in CryptoBot webhook settings
bot = Bot(token=TOKEN)

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def receive_payment():
    data = request.json

    # Verify request origin
    if "secret" not in data or data["secret"] != CRYPTO_SECRET:
        return jsonify({"error": "Unauthorized"}), 403

    # Extract payment details
    user_id = data["user_id"]
    amount = data["amount"]
    currency = data["currency"]
    status = data["status"]

    if status == "success":
        # Notify user of successful payment
        bot.send_message(chat_id=user_id, text=f"✅ Payment received: {amount} {currency}. Your plan is now active!")

        # TODO: Activate user plan in your system (e.g., database update)

    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
