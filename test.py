import os
import requests
import qrcode
from flask import Flask, request, jsonify
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler

# Configurations
BOT_TOKEN = "8180105447:AAH9btPiiHLkRPGRnnsQ-31tcpyRp4-zZyM"
NOWPAYMENTS_API_KEY = "5015ef49-3bba-4a38-ab4a-aade26ac84eb"
WEBHOOK_URL = "https://3fc2-13-211-93-128.ngrok-free.app/webhook"

app = Flask(__name__)
bot = Bot(token=BOT_TOKEN)

# Store invoices
pending_payments = {}

# 1️⃣ Start Command
async def start(update: Update, context):
    message = "Welcome! Use /buy to purchase with crypto."
    await update.message.reply_text(message)

# 2️⃣ Buy Command - Show Plans
async def buy(update: Update, context):
    keyboard = [
        [InlineKeyboardButton("Basic ($10)", callback_data="buy_10")],
        [InlineKeyboardButton("Premium ($50)", callback_data="buy_50")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Choose a plan:", reply_markup=reply_markup)

# 3️⃣ Handle Payment Request
async def handle_buy(update: Update, context):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    amount = int(query.data.split("_")[1])  # Extract amount
    
    # Create invoice
    invoice = create_invoice(amount, user_id)
    if not invoice:
        await query.message.reply_text("Failed to create invoice. Try again.")
        return
    
    # Generate QR Code
    qr_path = generate_qr_code(invoice["invoice_url"])
    
    # Send Payment Info
    await bot.send_photo(
        chat_id=user_id,
        photo=open(qr_path, "rb"),
        caption=f"Send **{amount} USD** in crypto.\n\n"
                f"🔹 **Payment Link:** [Click to Pay]({invoice['invoice_url']})",
        parse_mode="Markdown"
    )
    pending_payments[invoice["id"]] = user_id  # Store for verification

# 4️⃣ Create Invoice using NowPayments API
def create_invoice(amount, user_id):
    url = "https://api.nowpayments.io/v1/invoice"
    headers = {"x-api-key": NOWPAYMENTS_API_KEY, "Content-Type": "application/json"}
    
    payload = {
        "price_amount": amount,
        "price_currency": "usd",
        "pay_currency": "usdt",
        "order_id": str(user_id),
        "order_description": "Crypto Payment",
        "ipn_callback_url": WEBHOOK_URL
    }
    
    response = requests.post(url, json=payload, headers=headers).json()
    
    if "id" in response:
        return response
    return None

# 5️⃣ Generate QR Code
def generate_qr_code(payment_url):
    qr = qrcode.make(payment_url)
    qr_path = f"/tmp/qr_{payment_url[-6:]}.png"
    qr.save(qr_path)
    return qr_path

# 6️⃣ Webhook for Payment Verification
@app.route("/webhook", methods=["POST"])
def handle_webhook():
    data = request.json
    invoice_id = data.get("payment_id")
    status = data.get("payment_status")
    
    if invoice_id in pending_payments and status == "finished":
        user_id = pending_payments.pop(invoice_id)
        bot.send_message(chat_id=user_id, text="✅ Payment received! Your plan is activated.")
    
    return jsonify({"status": "ok"})

# 7️⃣ Setup Telegram Bot Handlers
def main():
    app_bot = Application.builder().token(BOT_TOKEN).build()
    
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(CommandHandler("buy", buy))
    app_bot.add_handler(CallbackQueryHandler(handle_buy, pattern="buy_.*"))
    
    app_bot.run_polling()

# 8️⃣ Run Flask Webhook Server
if __name__ == "__main__":
    from threading import Thread
    
    Thread(target=lambda: app.run(host="0.0.0.0", port=5000)).start()
    main()
