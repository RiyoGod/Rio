import requests
import qrcode
from io import BytesIO
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import CallbackContext

# 🔹 Your CryptoBot API Key
CRYPTOBOT_SECRET = "335607:AA3yJu1fkPWWbczmD6hw8uesXCiAwzIJWm1"

# 🔹 Get Payment Address
def get_payment_address(asset="USDT"):
    url = "https://pay.crypt.bot/api/getMyDepositAddresses"
    headers = {"Crypto-Pay-API-Token": CRYPTOBOT_SECRET}

    response = requests.get(url, headers=headers).json()
    print("🔍 API Response:", response)  # ✅ Debugging output

    if response["ok"]:
        for item in response["result"]:
            if item["asset"] == asset:
                return item["address"]
    
    return None

# 🔹 Generate QR Code
def generate_qr_code(payment_address):
    qr = qrcode.make(payment_address)
    bio = BytesIO()
    qr.save(bio, format="PNG")
    bio.seek(0)
    return bio

# 🔹 Check Payment Status
def check_payment_status(asset="USDT", min_amount=10):
    url = "https://pay.crypt.bot/api/getPayments"
    headers = {"Crypto-Pay-API-Token": CRYPTOBOT_SECRET}

    response = requests.get(url, headers=headers).json()
    print("🔍 Payment Check Response:", response)  # ✅ Debugging output

    if response["ok"]:
        for payment in response["result"]:
            if payment["asset"] == asset and payment["amount"] >= min_amount:
                return payment["status"]  # "completed" or "pending"
    
    return "not_received"

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
        [InlineKeyboardButton("Basic Plan", callback_data="basic_plan")],
        [InlineKeyboardButton("Premium Plan", callback_data="premium_plan")],
        [InlineKeyboardButton("Immortal Plan", callback_data="immortal_plan")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.effective_chat.send_message(message, reply_markup=reply_markup, parse_mode="Markdown")

# 🔹 Handle Button Clicks
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

        payment_address = get_payment_address("USDT")
        if payment_address:
            qr_code = generate_qr_code(payment_address)
            
            message = (
                f"💰 **Payment for {plan.replace('_', ' ').title()} ({duration.title()})**\n\n"
                f"📥 **Send exactly** `{amount} USDT` to:\n"
                f"`{payment_address}`\n\n"
                "🔗 **Scan the QR Code to Pay:**"
            )

            keyboard = [
                [InlineKeyboardButton("🔄 Check Payment", callback_data=f"check_payment_{amount}")],
                [InlineKeyboardButton("🔙 Back", callback_data="back_to_plans")],
            ]

            await query.message.reply_photo(photo=InputFile(qr_code, filename="payment_qr.png"), caption=message, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        else:
            await query.edit_message_text("❌ Failed to generate a payment address. Try again later.")

    elif query.data.startswith("check_payment"):
        amount = int(query.data.split("_")[2])  # Get the expected amount
        status = check_payment_status("USDT", amount)

        if status == "completed":
            await query.edit_message_text("✅ **Payment received successfully!**\nYour plan is now active.")
        elif status == "pending":
            await query.edit_message_text("⌛ **Payment is still pending.**\nPlease wait a moment and try again.")
        else:
            await query.edit_message_text("❌ **No payment detected yet.**\nMake sure you've sent the correct amount.")

    elif query.data == "back_to_plans":
        await purchase_command(update, context)
