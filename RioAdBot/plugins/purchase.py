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
    
    if response.get("ok") and "result" in response:
        return response["result"].get("invoice_id"), response["result"].get("pay_url")
    
    return None, None

# 🔹 Function to Check Payment Status
def check_payment(invoice_id):
    url = "https://pay.crypt.bot/api/getInvoices"
    headers = {"Crypto-Pay-API-Token": CRYPTOBOT_SECRET}

    response = requests.get(url, headers=headers).json()

    if response.get("ok") and "result" in response:
        for invoice in response["result"].get("items", []):
            if invoice.get("invoice_id") == invoice_id:
                return invoice.get("status", "unknown")
    
    return "unknown"

# 🔹 Function to Show Available Plans
async def show_plans(update, context, message="💼 **Choose Your Plan:**", edit=False):
    plans_keyboard = [
        [InlineKeyboardButton("Basic Plan - $40/week", callback_data='basic_plan')],
        [InlineKeyboardButton("Premium Plan - $250/week", callback_data='premium_plan')],
        [InlineKeyboardButton("Immortal Plan - $500/week", callback_data='immortal_plan')],
    ]
    
    if edit:
        await update.callback_query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(plans_keyboard), parse_mode="Markdown")
    else:
        await update.message.reply_text(message, reply_markup=InlineKeyboardMarkup(plans_keyboard), parse_mode="Markdown")

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
            [InlineKeyboardButton(f"Monthly - ${plan_prices[selected_plan]['monthly']}", callback_data=f"{selected_plan}_monthly")],
            [InlineKeyboardButton(f"Weekly - ${plan_prices[selected_plan]['weekly']}", callback_data=f"{selected_plan}_weekly")],
            [InlineKeyboardButton("🔙 Back", callback_data="back_to_plans")],
        ]
        await query.edit_message_text(f"📌 **{selected_plan.replace('_', ' ').title()}**\n\n🔽 Choose Duration:", 
                                      reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

    elif any(plan in query.data for plan in plan_prices):
        plan, duration = query.data.rsplit("_", 1)
        amount = plan_prices[plan][duration]
        invoice_id, pay_url = create_invoice(amount, "USDT", user_id)

        if pay_url:
            keyboard = [
                [InlineKeyboardButton("✅ Pay Now", url=pay_url)],
                [InlineKeyboardButton("🔄 Check Payment", callback_data=f"check_{invoice_id}")],
                [InlineKeyboardButton("❌ Cancel", callback_data="cancel_payment")],
            ]
            await query.edit_message_text(f"💰 **Payment for {plan.replace('_', ' ').title()} ({duration.title()})**\n\n"
                                          f"🔗 Click **'Pay Now'** to complete the payment.", 
                                          reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        else:
            await query.edit_message_text("⚠️ **Failed to create invoice.** Try again later.")

    elif query.data.startswith("check_"):
        invoice_id = int(query.data.split("_")[1])
        status = check_payment(invoice_id)

        status_messages = {
            "paid": "✅ **Payment received successfully!**\n🎉 Your plan is now active!",
            "active": "⌛ **Payment is pending.** Please wait a moment and try again.",
            "expired": "❌ **Invoice expired!** Please generate a new invoice.",
            "unknown": "⚠️ **Could not check payment status.** Try again later.",
        }
        await query.edit_message_text(status_messages.get(status, "⚠️ Unknown error occurred."))

    elif query.data == "cancel_payment":
        await show_plans(update, context, "🚫 **Payment Canceled!**\n\n🔽 Choose another plan:", edit=True)

    elif query.data == "back_to_plans":
        await show_plans(update, context, "📋 **Select a Different Plan:**", edit=True)
