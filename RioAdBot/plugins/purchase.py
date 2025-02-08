import requests
import qrcode
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
import datetime

# 🔹 Your CryptoBot API Key
CRYPTOBOT_SECRET = "335607:AA3yJu1fkPWWbczmD6hw8uesXCiAwzIJWm1"

# In-memory storage for user subscriptions (You can replace this with a database)
subscriptions = {}

# 🔹 Function to Generate a USDT Payment Invoice
def get_usdt_address(amount, user_id):
    url = "https://pay.crypt.bot/api/createInvoice"
    headers = {"Crypto-Pay-API-Token": CRYPTOBOT_SECRET, "Content-Type": "application/json"}

    payload = {
        "asset": "USDT",
        "amount": amount,
        "description": "Your Plan Purchase",
        "hidden_message": "Thanks for your payment!",
        "payload": str(user_id),
        "allow_comments": False,
        "allow_anonymous": False,
        "expires_in": 3600  # Invoice expires in 1 hour
    }

    response = requests.post(url, headers=headers, json=payload).json()

    if response["ok"]:
        return response["result"]["address"]  # Fetch the generated USDT deposit address
    else:
        print(f"◆ ERROR: Failed to create USDT invoice → {response}")  # Debugging log
        return None

# 🔹 Function to Generate QR Code for USDT Address
def generate_qr_code(usdt_address):
    qr = qrcode.make(usdt_address)
    qr_path = f"/tmp/usdt_qr_{usdt_address[-6:]}.png"
    qr.save(qr_path)
    return qr_path

# 🔹 Purchase Command
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

    print(f"◆ DEBUG: Button clicked → {query.data}")  # ✅ Debugging log

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

        usdt_address = get_usdt_address(amount, user_id)
        if not usdt_address:
            await query.edit_message_text("⚠ Error: Could not generate a USDT deposit address. Try again later.")
            return

        qr_path = generate_qr_code(usdt_address)
        await context.bot.send_photo(
            chat_id=user_id,
            photo=open(qr_path, "rb"),
            caption=f"◆ **Payment for {plan.replace('_', ' ').title()} ({duration.title()})**\n\n"
                    f"Send **${amount} USDT** to the address below:\n\n"
                    f"🔹 **USDT Address:** `{usdt_address}`\n\n"
                    f"✅ Scan the QR Code or copy the address to pay."
        )

    elif query.data == "back_to_plans":
        await purchase_command(update, context)  # Show plan selection again

    else:
        print(f"⚠ DEBUG: Unknown button action → {query.data}")
        await query.edit_message_text("⚠ **Invalid selection. Try again.**")

# 🔹 Job to Check for Expired Plans and Notify User
async def check_expiration(context: CallbackContext):
    for user_id, subscription in subscriptions.items():
        if subscription["expiration"] < datetime.datetime.now():
            user = await context.bot.get_chat(user_id)
            await user.send_message(f"Your **{subscription['plan'].replace('_', ' ').title()}** plan has expired. Please renew your subscription.")
            del subscriptions[user_id]
