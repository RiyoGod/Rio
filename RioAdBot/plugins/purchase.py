import requests
import qrcode
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

# 🔹 Your NowPayments API Key
NOWPAYMENTS_API_KEY = "54494930-1b6d-45dd-ae40-5887d2e11d45"

# 🔹 Supported Cryptos
SUPPORTED_ASSETS = ["USDT", "SOL", "TRX", "ADA"]

# 🔹 Function to Create Payment Address
def create_payment_address(amount, currency, user_id):
    url = "https://api.nowpayments.io/v1/invoice"
    headers = {
        "x-api-key": NOWPAYMENTS_API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "price_amount": amount,
        "price_currency": "USD",
        "pay_currency": currency,
        "order_id": str(user_id),
        "order_description": "Plan Purchase"
    }

    response = requests.post(url, headers=headers, json=payload).json()

    if response.get("id"):
        return response["pay_address"], response["pay_currency"], response["payment_url"]
    return None, None, None

# 🔹 Function to Check Payment Status
def check_payment_status(invoice_id):
    url = f"https://api.nowpayments.io/v1/payment/{invoice_id}"
    headers = {"x-api-key": NOWPAYMENTS_API_KEY}

    response = requests.get(url, headers=headers).json()

    if response.get("payment_status"):
        return response["payment_status"]
    return "unknown"

# 🔹 Generate QR Code
def generate_qr_code(payment_address):
    qr = qrcode.make(payment_address)
    qr.save("payment_qr.png")

# 🔹 Purchase Command (Async)
async def purchase_command(update: Update, context: CallbackContext):
    message = (
        "> **Choose Your Plan!!**\n\n"
        "▫ **Basic Plan**\n"
        "**├ Accounts: 1**\n"
        "**├ Intervals: 5 min**\n"
        "**•|  Price: $40/week | $100/month |•**\n\n"
        "**▫ Premium Plan**\n"
        "**├ Accounts: 4**\n"
        "**├ Intervals: 30 sec**\n"
        "**•| Price: $250/week | $500/month |•**\n\n"
        "**▫ Immortal Plan**\n"
        "**├ Accounts: 10**\n"
        "**├ Intervals: 60 sec**\n"
        "**•| Price: $500/week | $1000/month |•**\n\n"
        "---\n\n"
        "> Select a Plan to Continue Via Below Buttons!\n\n"
        "For support, contact @Boostadvert."
    )

    keyboard = [
        [InlineKeyboardButton("Basic Plan", callback_data="basic_plan")],
        [InlineKeyboardButton("Premium Plan", callback_data="premium_plan")],
        [InlineKeyboardButton("Immortal Plan", callback_data="immortal_plan")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(message, reply_markup=reply_markup, parse_mode="Markdown")

# 🔹 Handle Button Clicks (Async)
async def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id  

    plan_prices = {
        "basic_plan": {"weekly": 40, "monthly": 100},
        "premium_plan": {"weekly": 250, "monthly": 500},
        "immortal_plan": {"weekly": 500, "monthly": 1000},
    }

    if query.data in plan_prices:
        selected_plan = query.data
        keyboard = [
            [InlineKeyboardButton(f"Monthly (${plan_prices[selected_plan]['monthly']})", callback_data=f"{selected_plan}_monthly")],
            [InlineKeyboardButton(f"Weekly (${plan_prices[selected_plan]['weekly']})", callback_data=f"{selected_plan}_weekly")],
            [InlineKeyboardButton("🔙 Back", callback_data="back_to_plans")],
        ]
        await query.edit_message_text("Select duration:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif any(plan in query.data for plan in plan_prices):
        plan, duration = query.data.rsplit("_", 1)
        amount = plan_prices[plan][duration]

        keyboard = [
            [InlineKeyboardButton(f"USDT", callback_data=f"pay_{amount}_USDT")],
            [InlineKeyboardButton(f"SOL", callback_data=f"pay_{amount}_SOL")],
            [InlineKeyboardButton(f"TRX", callback_data=f"pay_{amount}_TRX")],
            [InlineKeyboardButton(f"ADA", callback_data=f"pay_{amount}_ADA")],
            [InlineKeyboardButton("🔙 Back", callback_data="back_to_plans")],
        ]
        await query.edit_message_text(f"💰 **Payment for {plan.replace('_', ' ').title()} ({duration.title()})**\n\n"
                                      f"Select a cryptocurrency to proceed.",
                                      reply_markup=InlineKeyboardMarkup(keyboard),
                                      parse_mode="Markdown")

    elif query.data.startswith("pay_"):
        _, amount, currency = query.data.split("_")
        amount = int(amount)

        payment_address, pay_currency, pay_url = create_payment_address(amount, currency, user_id)

        if payment_address:
            generate_qr_code(payment_address)
            keyboard = [
                [InlineKeyboardButton("🔄 Check Payment", callback_data=f"check_{user_id}")],
                [InlineKeyboardButton("🔙 Back", callback_data="back_to_plans")],
            ]
            await query.edit_message_text(f"💰 **Pay {amount} USD in {pay_currency}**\n\n"
                                          f"📍 **Wallet Address:** `{payment_address}`\n\n"
                                          f"📸 **Scan QR to Pay**\n"
                                          f"(Or click the button below to check payment status)\n",
                                          reply_markup=InlineKeyboardMarkup(keyboard),
                                          parse_mode="Markdown")
            await context.bot.send_photo(chat_id=query.message.chat_id, photo=open("payment_qr.png", "rb"))
        else:
            await query.edit_message_text("❌ Failed to generate a payment address. Try again later.")

    elif query.data.startswith("check_"):
        invoice_id = query.data.split("_")[1]
        status = check_payment_status(invoice_id)

        if status == "finished":
            await query.edit_message_text("✅ **Payment received successfully!**\nYour plan is now active.")
        elif status == "waiting":
            await query.edit_message_text("⌛ **Payment is still pending.**\nPlease wait a moment and try again.")
        elif status == "expired":
            await query.edit_message_text("❌ **Invoice expired!**\nPlease generate a new invoice.")
        else:
            await query.edit_message_text("⚠️ **Could not check payment status.** Try again later.")

    elif query.data == "back_to_plans":
        await purchase_command(update, context)  # Call purchase command again to show plans
