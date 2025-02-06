import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

# 🔹 NowPayments API Key (Replace with yours)
NOWPAYMENTS_API_KEY = "54494930-1b6d-45dd-ae40-5887d2e11d45"

# 🔹 Plan Prices
plan_prices = {
    "basic": {"weekly": 40, "monthly": 100},
    "premium": {"weekly": 250, "monthly": 500},
    "immortal": {"weekly": 500, "monthly": 1000},
}

# 🔹 Supported Crypto Assets
SUPPORTED_ASSETS = ["USDT", "BTC", "ETH", "SOL", "TRX", "ADA"]

# 🔹 Function to Create Payment Address
def create_payment(amount, currency, user_id):
    url = "https://api.nowpayments.io/v1/invoice"
    headers = {"x-api-key": NOWPAYMENTS_API_KEY, "Content-Type": "application/json"}

    payload = {
        "price_amount": amount,
        "price_currency": "USD",
        "pay_currency": currency,
        "order_id": str(user_id),
        "order_description": "Your Plan Purchase",
        "is_fixed_rate": True,
        "ipn_callback_url": "https://yourwebsite.com/payment_callback",
    }

    response = requests.post(url, headers=headers, json=payload).json()

    if response.get("id"):
        return response["pay_address"], response.get("payment_url"), response.get("qr_code")
    return None, None, None

# 🔹 Function to Check Payment Status
def check_payment_status(order_id):
    url = f"https://api.nowpayments.io/v1/payment/{order_id}"
    headers = {"x-api-key": NOWPAYMENTS_API_KEY}

    response = requests.get(url, headers=headers).json()

    return response.get("payment_status", "unknown")

# 🔹 Purchase Command
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
        [InlineKeyboardButton("Basic Plan", callback_data="plan_basic")],
        [InlineKeyboardButton("Premium Plan", callback_data="plan_premium")],
        [InlineKeyboardButton("Immortal Plan", callback_data="plan_immortal")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(message, reply_markup=reply_markup, parse_mode="Markdown")

# 🔹 Handle Button Clicks
async def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id  

    if query.data.startswith("plan_"):
        selected_plan = query.data.split("_")[1]
        if selected_plan in plan_prices:
            keyboard = [
                [InlineKeyboardButton(f"Monthly (${plan_prices[selected_plan]['monthly']})", callback_data=f"duration_{selected_plan}_monthly")],
                [InlineKeyboardButton(f"Weekly (${plan_prices[selected_plan]['weekly']})", callback_data=f"duration_{selected_plan}_weekly")],
                [InlineKeyboardButton("🔙 Back", callback_data="back_to_plans")],
            ]
            await query.edit_message_text("Select duration:", reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await query.edit_message_text("❌ Invalid plan. Please try again.")

    elif query.data.startswith("duration_"):
        _, plan, duration = query.data.split("_", 2)  # ✅ Fixed to unpack properly
        if plan in plan_prices and duration in plan_prices[plan]:
            amount = plan_prices[plan][duration]
            keyboard = [
                [InlineKeyboardButton(f"{asset}", callback_data=f"pay_{plan}_{duration}_{asset}") for asset in SUPPORTED_ASSETS],
                [InlineKeyboardButton("🔙 Back", callback_data="back_to_plans")],
            ]
            await query.edit_message_text("🔹 Select Payment Currency:", reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await query.edit_message_text("❌ Invalid duration. Please try again.")

    elif query.data.startswith("pay_"):
        _, plan, duration, currency = query.data.split("_", 3)  # ✅ Fixed unpacking
        amount = plan_prices.get(plan, {}).get(duration)
        
        if not amount:
            await query.edit_message_text("❌ Invalid plan or duration. Please try again.")
            return

        pay_address, pay_url, qr_code = create_payment(amount, currency, user_id)

        if pay_address:
            keyboard = [
                [InlineKeyboardButton("🔄 Check Payment", callback_data=f"check_{pay_url}")],
                [InlineKeyboardButton("🔙 Back", callback_data="back_to_plans")],
            ]
            await query.edit_message_text(
                f"💰 **Payment for {plan.replace('_', ' ').title()} ({duration.title()})**\n\n"
                f"Send **{amount} {currency}** to:\n"
                f"**{pay_address}**\n\n"
                f"🔹 [Click here to view QR Code]({qr_code})",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )
        else:
            await query.edit_message_text("❌ Failed to generate a payment address. Try again later.")

    elif query.data.startswith("check_"):
        order_id = query.data.split("_")[1]
        status = check_payment_status(order_id)

        if status == "confirmed":
            await query.edit_message_text("✅ **Payment received successfully!**\nYour plan is now active.")
        elif status == "waiting":
            await query.edit_message_text("⌛ **Payment is still pending.**\nPlease wait a moment and try again.")
        elif status == "failed":
            await query.edit_message_text("❌ **Payment failed!**\nPlease try again.")
        else:
            await query.edit_message_text("⚠️ **Could not check payment status.** Try again later.")

    elif query.data == "back_to_plans":
        await purchase_command(update, context)  # Call purchase command again to show plans
