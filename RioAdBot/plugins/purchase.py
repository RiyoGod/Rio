import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

# 🔹 CryptoBot API Key
CRYPTOBOT_SECRET = "335607:AA3yJu1fkPWWbczmD6hw8uesXCiAwzIJWm1"

# 🔹 Function to Create Invoice
def create_invoice(amount, currency, user_id):
    url = "https://pay.crypt.bot/api/createInvoice"
    headers = {"Crypto-Pay-API-Token": CRYPTOBOT_SECRET, "Content-Type": "application/json"}

    payload = {
        "asset": currency,
        "amount": amount,
        "description": "Your Plan Purchase",
        "hidden_message": "Thanks for your payment!",
        "paid_btn_name": "viewItem",
        "paid_btn_url": "https://yourwebsite.com/order_status",
        "payload": str(user_id),
        "allow_comments": False,
        "allow_anonymous": False,
        "expires_in": 3600
    }

    response = requests.post(url, headers=headers, json=payload).json()

    if response["ok"]:
        return response["result"]["invoice_id"], response["result"]["pay_url"]
    else:
        return None, None

# 🔹 Function to Check Payment Status
def check_payment(invoice_id):
    url = "https://pay.crypt.bot/api/getInvoices"
    headers = {"Crypto-Pay-API-Token": CRYPTOBOT_SECRET}

    response = requests.get(url, headers=headers).json()

    if response["ok"]:
        for invoice in response["result"]["items"]:
            if invoice["invoice_id"] == invoice_id:
                return invoice["status"]  # "paid", "active", "expired"

    return "unknown"

# 🔹 Safe Message Editing Function (Fixes Telegram Edit Error)
async def safe_edit_message(query, text, reply_markup=None):
    try:
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    except:
        await query.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")

# 🔹 Function to Show Plan Selection
async def show_plan_selection(update):
    message = (
        "➜ **Choose Your Plan!**\n\n"
        "◆ **Basic Plan**\n"
        "├ Accounts: 1\n"
        "├ Intervals: 5 min\n"
        "└ Price: $40/week | $100/month\n\n"
        "◆ **Premium Plan**\n"
        "├ Accounts: 4\n"
        "├ Intervals: 30 sec\n"
        "└ Price: $250/week | $500/month\n\n"
        "◆ **Immortal Plan**\n"
        "├ Accounts: 10\n"
        "├ Intervals: 60 sec\n"
        "└ Price: $500/week | $1000/month\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "➜ Select a Plan to Continue Below!\n\n"
        "For support, contact @Boostadvert."
    )

    keyboard = [
        [InlineKeyboardButton("◆ Basic Plan", callback_data="basic_plan")],
        [InlineKeyboardButton("◆ Premium Plan", callback_data="premium_plan")],
        [InlineKeyboardButton("◆ Immortal Plan", callback_data="immortal_plan")],
    ]

    await update.message.reply_text(message, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

# 🔹 Purchase Command (Async)
async def purchase_command(update: Update, context: CallbackContext):
    print("✔ /purchase command triggered!")  # Debugging log
    await show_plan_selection(update)

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

    print(f"Button clicked: {query.data}")  # Debugging log

    if query.data in plan_prices:
        selected_plan = query.data
        keyboard = [
            [InlineKeyboardButton(f"● Monthly (${plan_prices[selected_plan]['monthly']})", callback_data=f"{selected_plan}_monthly")],
            [InlineKeyboardButton(f"● Weekly (${plan_prices[selected_plan]['weekly']})", callback_data=f"{selected_plan}_weekly")],
            [InlineKeyboardButton("↩ Back", callback_data="back_to_plans")],
        ]
        await safe_edit_message(query, "➜ Select a duration:", InlineKeyboardMarkup(keyboard))

    elif any(plan in query.data for plan in plan_prices):
        plan, duration = query.data.rsplit("_", 1)
        amount = plan_prices[plan][duration]
        invoice_id, pay_url = create_invoice(amount, "USDT", user_id)

        if pay_url:
            keyboard = [
                [InlineKeyboardButton("✔ Pay Now", url=pay_url)],
                [InlineKeyboardButton("🔄 Check Payment", callback_data=f"check_{invoice_id}")],
                [InlineKeyboardButton("✖ Cancel Payment", callback_data=f"back_to_{plan}")],
                [InlineKeyboardButton("↩ Back", callback_data=f"back_to_{plan}")],
            ]
            await safe_edit_message(
                query,
                f"💵 **Payment for {plan.replace('_', ' ').title()} ({duration.title()})**\n\n"
                f"Click **'Pay Now'** to complete the payment.",
                InlineKeyboardMarkup(keyboard)
            )
        else:
            await safe_edit_message(query, "❌ Failed to create invoice. Try again later.")

    elif query.data.startswith("check_"):
        invoice_id = int(query.data.split("_")[1])
        status = check_payment(invoice_id)

        if status == "paid":
            await safe_edit_message(query, "✔ **Payment received successfully!**\nYour plan is now active.")
        elif status == "active":
            await safe_edit_message(query, "⌛ **Payment is still pending.**\nPlease wait a moment and try again.")
        elif status == "expired":
            await safe_edit_message(query, "❌ **Invoice expired!**\nPlease generate a new invoice.")
        else:
            await safe_edit_message(query, "⚠ **Could not check payment status.** Try again later.")

    elif query.data.startswith("back_to_"):
        plan = query.data.replace("back_to_", "")
        
        if plan in plan_prices:  # Going back to weekly/monthly selection
            keyboard = [
                [InlineKeyboardButton(f"● Monthly (${plan_prices[plan]['monthly']})", callback_data=f"{plan}_monthly")],
                [InlineKeyboardButton(f"● Weekly (${plan_prices[plan]['weekly']})", callback_data=f"{plan}_weekly")],
                [InlineKeyboardButton("↩ Back", callback_data="back_to_plans")],
            ]
            await safe_edit_message(query, "➜ Select a duration:", InlineKeyboardMarkup(keyboard))

        else:  # Going back to plan selection
            await show_plan_selection(query)
