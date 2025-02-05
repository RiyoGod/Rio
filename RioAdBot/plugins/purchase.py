import requests
import qrcode
from io import BytesIO
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import CallbackContext

# ✅ CryptoBot API Token
CRYPTOBOT_SECRET = "335607:AA3yJu1fkPWWbczmD6hw8uesXCiAwzIJWm1"

# ✅ Function to Get a Payment Address
def get_payment_address(asset):
    url = "https://pay.crypt.bot/api/getMyDepositAddresses"
    headers = {"Crypto-Pay-API-Token": CRYPTOBOT_SECRET}

    response = requests.get(url, headers=headers).json()
    
    if response["ok"]:
        for item in response["result"]:
            if item["asset"] == asset:
                return item["address"]
    
    return None

# ✅ Function to Generate QR Code
def generate_qr_code(payment_address):
    qr = qrcode.make(payment_address)
    img_io = BytesIO()
    qr.save(img_io, format="PNG")
    img_io.seek(0)
    return img_io

# ✅ Purchase Command (Async)
async def purchase_command(update: Update, context: CallbackContext):
    message = (
        "**💰 Choose Your Payment Plan**\n\n"
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
        "**Select a plan to proceed with payment.**\n"
        "For support, contact @Boostadvert."
    )

    keyboard = [
        [InlineKeyboardButton("Basic Plan", callback_data="basic_plan")],
        [InlineKeyboardButton("Premium Plan", callback_data="premium_plan")],
        [InlineKeyboardButton("Immortal Plan", callback_data="immortal_plan")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(message, reply_markup=reply_markup, parse_mode="Markdown")

# ✅ Handle Payment Requests
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
        
        # ✅ Get the payment address
        payment_address = get_payment_address("USDT")
        
        if payment_address:
            # ✅ Generate QR code
            qr_code = generate_qr_code(payment_address)

            # ✅ Send QR Code + Payment Info
            await query.message.reply_photo(
                photo=InputFile(qr_code, filename="payment_qr.png"),
                caption=f"💰 **Send {amount} USDT to this address:**\n\n`{payment_address}`\n\n"
                        "Scan the QR code to pay easily.\n\n"
                        "**After payment, send your transaction ID to @Boostadvert for confirmation.**",
                parse_mode="Markdown"
            )
        else:
            await query.edit_message_text("❌ Failed to generate a payment address. Try again later.")

    elif query.data == "back_to_plans":
        await purchase_command(update, context)
