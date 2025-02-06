import requests
import qrcode
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

# 🔹 Your NowPayments API Key
NOWPAYMENTS_API_KEY = "54494930-1b6d-45dd-ae40-5887d2e11d45"

# 🔹 Supported Crypto Currencies
SUPPORTED_ASSETS = ["USDT", "BTC", "ETH", "SOL", "TRX", "ADA"]

# 🔹 Function to Create Payment Address
def create_payment_address(amount, currency, user_id):
    url = "https://api.nowpayments.io/v1/payment"
    headers = {"x-api-key": NOWPAYMENTS_API_KEY, "Content-Type": "application/json"}

    payload = {
        "price_amount": amount,
        "price_currency": "USD",
        "pay_currency": currency,
        "ipn_callback_url": "https://yourserver.com/payment_callback",
        "order_id": str(user_id),
        "order_description": "Premium Plan Purchase"
    }

    response = requests.post(url, headers=headers, json=payload).json()

    if "payment_id" in response:
        return response["pay_address"], response["payment_id"], response["pay_amount"]
    else:
        print("🔍 API Response:", response)  # ✅ Debugging Log
        return None, None, None

# 🔹 Function to Check Payment Status
def check_payment_status(payment_id):
    url = f"https://api.nowpayments.io/v1/payment/{payment_id}"
    headers = {"x-api-key": NOWPAYMENTS_API_KEY}

    response = requests.get(url, headers=headers).json()

    if response.get("payment_status") == "finished":
        return "paid"
    elif response.get("payment_status") == "waiting":
        return "pending"
    elif response.get("payment_status") == "expired":
        return "expired"
    
    return "unknown"

# 🔹 Function to Generate QR Code
def generate_qr_code(address):
    qr = qrcode.make(address)
    qr.save("payment_qr.png")
    return "payment_qr.png"

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
            [InlineKeyboardButton("USDT", callback_data=f"{plan}_{duration}_USDT")],
            [InlineKeyboardButton("BTC", callback_data=f"{plan}_{duration}_BTC")],
            [InlineKeyboardButton("ETH", callback_data=f"{plan}_{duration}_ETH")],
            [InlineKeyboardButton("SOL", callback_data=f"{plan}_{duration}_SOL")],
            [InlineKeyboardButton("TRX", callback_data=f"{plan}_{duration}_TRX")],
            [InlineKeyboardButton("ADA", callback_data=f"{plan}_{duration}_ADA")],
            [InlineKeyboardButton("🔙 Back", callback_data="back_to_plans")],
        ]

        await query.edit_message_text("Choose a cryptocurrency:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif any(asset in query.data for asset in SUPPORTED_ASSETS):
        plan, duration, currency = query.data.split("_")
        amount = plan_prices[plan][duration]
        pay_address, payment_id, pay_amount = create_payment_address(amount, currency, user_id)

        if pay_address:
            qr_path = generate_qr_code(pay_address)
            keyboard = [
                [InlineKeyboardButton("🔄 Check Payment", callback_data=f"check_{payment_id}")],
                [InlineKeyboardButton("🔙 Back", callback_data="back_to_plans")],
            ]
            await query.message.reply_photo(photo=open(qr_path, "rb"),
                                            caption=f"💰 **Payment for {plan.replace('_', ' ').title()} ({duration.title()})**\n\n"
                                                    f"Amount: **{pay_amount} {currency}**\n"
                                                    f"Address: `{pay_address}`\n\n"
                                                    f"Scan the QR code or copy the address to pay.",
                                            reply_markup=InlineKeyboardMarkup(keyboard),
                                            parse_mode="Markdown")
        else:
            await query.edit_message_text("❌ Failed to generate a payment address. Try again later.")

    elif query.data.startswith("check_"):
        payment_id = query.data.split("_")[1]
        status = check_payment_status(payment_id)

        if status == "paid":
            await query.edit_message_text("✅ **Payment received successfully!**\nYour plan is now active.")
        elif status == "pending":
            await query.edit_message_text("⌛ **Payment is still pending.**\nPlease wait a moment and try again.")
        elif status == "expired":
            await query.edit_message_text("❌ **Invoice expired!**\nPlease generate a new invoice.")
        else:
            await query.edit_message_text("⚠️ **Could not check payment status.** Try again later.")

    elif query.data == "back_to_plans":
        await purchase_command(update, context)  # Call purchase command again to show plans
