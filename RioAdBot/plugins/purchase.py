import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

# ✅ NOWPayments API Key
NOWPAYMENTS_API_KEY = "54494930-1b6d-45dd-ae40-5887d2e11d45"

# ✅ Generate Crypto Payment Address
def generate_payment_address(amount, currency, order_id):
    url = "https://api.nowpayments.io/v1/payment"
    headers = {
        "x-api-key": NOWPAYMENTS_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "price_amount": amount,
        "price_currency": "USD",  
        "pay_currency": currency,  
        "order_id": str(order_id),
        "order_description": "Plan Purchase",
        "is_fixed_rate": True
    }
    
    response = requests.post(url, json=payload, headers=headers).json()
    print("🔍 API Response:", response)  # Debugging Log

    if response.get("payment_id"):
        return response["pay_address"], response["pay_currency"], response["payment_id"]
    else:
        return None, None, None

# ✅ Check Payment Status
def check_payment(payment_id):
    url = f"https://api.nowpayments.io/v1/payment/{payment_id}"
    headers = {"x-api-key": NOWPAYMENTS_API_KEY}
    
    response = requests.get(url, headers=headers).json()

    if response.get("payment_status") == "finished":
        return "paid"
    elif response.get("payment_status") == "waiting":
        return "pending"
    elif response.get("payment_status") == "failed":
        return "failed"
    else:
        return "unknown"

# ✅ /purchase Command
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

# ✅ Button Handler
async def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id  
    selected_plan = query.data

    plan_prices = {
        "basic_plan_weekly": 40,
        "basic_plan_monthly": 100,
        "premium_plan_weekly": 250,
        "premium_plan_monthly": 500,
        "immortal_plan_weekly": 500,
        "immortal_plan_monthly": 1000
    }

    # ✅ Handle Plan Selection
    if selected_plan in ["basic_plan", "premium_plan", "immortal_plan"]:
        keyboard = [
            [InlineKeyboardButton("Monthly", callback_data=f"{selected_plan}_monthly")],
            [InlineKeyboardButton("Weekly", callback_data=f"{selected_plan}_weekly")],
            [InlineKeyboardButton("🔙 Back", callback_data="back_to_plans")],
        ]
        await query.edit_message_text("Select duration:", reply_markup=InlineKeyboardMarkup(keyboard))
    
    # ✅ Handle Payment Address Generation
    elif selected_plan in plan_prices:
        amount = plan_prices[selected_plan]
        currency = "USDT"  # Default currency (Can be changed)
        
        pay_address, pay_currency, payment_id = generate_payment_address(amount, currency, user_id)

        if pay_address:
            qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={pay_address}"
            
            keyboard = [
                [InlineKeyboardButton("🔗 Copy Address", callback_data="copy_address")],
                [InlineKeyboardButton("🔄 Check Payment", callback_data=f"check_{payment_id}")],
                [InlineKeyboardButton("🔙 Back", callback_data="back_to_plans")],
            ]
            
            await query.edit_message_text(
                f"💰 **Payment for {selected_plan.replace('_', ' ').title()}**\n"
                f"💵 **Amount:** {amount} USD\n"
                f"💳 **Currency:** {pay_currency}\n"
                f"🏦 **Address:** `{pay_address}`\n\n"
                f"📌 *Scan QR Code Below:*",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )
            await query.message.reply_photo(photo=qr_url)

        else:
            await query.edit_message_text("❌ Failed to generate a payment address. Try again later.")

    # ✅ Check Payment Status
    elif query.data.startswith("check_"):
        payment_id = query.data.split("_")[1]
        status = check_payment(payment_id)

        if status == "paid":
            await query.edit_message_text("✅ **Payment received successfully!**\nYour plan is now active.")
        elif status == "pending":
            await query.edit_message_text("⌛ **Payment is still pending.**\nPlease wait and try again.")
        elif status == "failed":
            await query.edit_message_text("❌ **Payment failed.**\nPlease generate a new invoice.")
        else:
            await query.edit_message_text("⚠️ **Could not check payment status.** Try again later.")

    # ✅ Back to Plans
    elif query.data == "back_to_plans":
        await purchase_command(update, context)  # Call purchase command again
