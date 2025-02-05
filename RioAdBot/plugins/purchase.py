import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

# 🔹 Your CryptoBot API Key
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
        [InlineKeyboardButton("Basic Plan", callback_data='basic_plan')],
        [InlineKeyboardButton("Premium Plan", callback_data='premium_plan')],
        [InlineKeyboardButton("Immortal Plan", callback_data='immortal_plan')],
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
        invoice_id, pay_url = create_invoice(amount, "USDT", user_id)

        if pay_url:
            keyboard = [
                [InlineKeyboardButton("✅ Pay Now", url=pay_url)],
                [InlineKeyboardButton("🔄 Check Payment", callback_data=f"check_{invoice_id}")],
                [InlineKeyboardButton("🔙 Back", callback_data="back_to_plans")],
            ]
            await query.edit_message_text(f"💰 **Payment for {plan.replace('_', ' ').title()} ({duration.title()})**\n\n"
                                          f"Click **'Pay Now'** to complete the payment.",
                                          reply_markup=InlineKeyboardMarkup(keyboard),
                                          parse_mode="Markdown")
        else:
            await query.edit_message_text("❌ Failed to create invoice. Try again later.")

    elif query.data.startswith("check_"):
        invoice_id = int(query.data.split("_")[1])
        status = check_payment(invoice_id)

        if status == "paid":
            await query.edit_message_text("✅ **Payment received successfully!**\nYour plan is now active.")
        elif status == "active":
            await query.edit_message_text("⌛ **Payment is still pending.**\nPlease wait a moment and try again.")
        elif status == "expired":
            await query.edit_message_text("❌ **Invoice expired!**\nPlease generate a new invoice.")
        else:
            await query.edit_message_text("⚠️ **Could not check payment status.** Try again later.")

    elif query.data == "back_to_plans":
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
            [InlineKeyboardButton("Basic Plan", callback_data='basic_plan')],
            [InlineKeyboardButton("Premium Plan", callback_data='premium_plan')],
            [InlineKeyboardButton("Immortal Plan", callback_data='immortal_plan')],
        ]

        await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
