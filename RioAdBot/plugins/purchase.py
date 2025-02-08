import requests
import qrcode
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
import datetime

# 🔹 Your CryptoBot API Key
CRYPTOBOT_SECRET = "335607:AA3yJu1fkPWWbczmD6hw8uesXCiAwzIJWm1"

# In-memory storage for user subscriptions (Replace this with a database in production)
subscriptions = {}

# 🔹 Function to Fetch USDT Address with Better Error Handling
def get_usdt_address():
    url = "https://pay.crypt.bot/api/getBalance"
    headers = {"Crypto-Pay-API-Token": CRYPTOBOT_SECRET}

    response = requests.get(url, headers=headers).json()

    if not response.get("ok"):
        print(f"◆ ERROR: Failed to fetch balance → {response}")  # Debugging log
        return None

    assets = response.get("result", [])
    for asset in assets:
        if asset.get("asset") == "USDT":
            return asset.get("wallet")

    print(f"◆ ERROR: No USDT wallet found in response → {response}")  # Debugging log
    return None

# 🔹 Function to Generate QR Code
def generate_qr_code(data):
    qr = qrcode.make(data)
    qr_path = "/mnt/data/usdt_qr.png"
    qr.save(qr_path)
    return qr_path

# 🔹 Purchase Command (Async)
async def purchase_command(update: Update, context: CallbackContext):
    message = (
        "➜ **Choose Your Plan!**\n\n"
        "◆ **Basic Plan**\n"
        "├ Accounts: 1\n"
        "├ Intervals: 5 min\n"
        "└ Price: **$40/week** | **$100/month**\n\n"
        "◆ **Premium Plan**\n"
        "├ Accounts: 4\n"
        "├ Intervals: 30 sec\n"
        "└ Price: **$250/week** | **$500/month**\n\n"
        "◆ **Immortal Plan**\n"
        "├ Accounts: 10\n"
        "├ Intervals: 60 sec\n"
        "└ Price: **$500/week** | **$1000/month**\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "➜ **Select a Plan to Continue Below!**\n\n"
        "For support, contact @Boostadvert."
    )

    keyboard = [
        [InlineKeyboardButton("◆ Basic Plan", callback_data="basic_plan")],
        [InlineKeyboardButton("◆ Premium Plan", callback_data="premium_plan")],
        [InlineKeyboardButton("◆ Immortal Plan", callback_data="immortal_plan")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.effective_chat.send_message(message, reply_markup=reply_markup, parse_mode="Markdown")

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
            [InlineKeyboardButton(f"◆ Monthly (${plan_prices[selected_plan]['monthly']})", callback_data=f"{selected_plan}_monthly")],
            [InlineKeyboardButton(f"◆ Weekly (${plan_prices[selected_plan]['weekly']})", callback_data=f"{selected_plan}_weekly")],
            [InlineKeyboardButton("◀ Back", callback_data="back_to_plans")],
        ]
        await query.edit_message_text("◆ Select duration:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif any(plan in query.data for plan in plan_prices):
        plan, duration = query.data.rsplit("_", 1)
        amount = plan_prices[plan][duration]

        usdt_address = get_usdt_address()
        if not usdt_address:
            await query.edit_message_text("⚠ Error: Could not fetch USDT address. Try again later.")
            return

        qr_path = generate_qr_code(usdt_address)
        await context.bot.send_photo(chat_id=user_id, photo=open(qr_path, "rb"), caption=f"◆ **Payment for {plan.replace('_', ' ').title()} ({duration.title()})**\n\n"
                                                                                        f"Send **${amount} USDT** to the address below:\n\n"
                                                                                        f"🔹 **USDT Address:** `{usdt_address}`\n\n"
                                                                                        f"✅ Scan the QR Code or copy the address to pay.")

    elif query.data == "back_to_plans":
        await purchase_command(update, context)  # Call purchase command again to show plans

    else:
        await query.edit_message_text("⚠ **Invalid selection. Try again.**")
