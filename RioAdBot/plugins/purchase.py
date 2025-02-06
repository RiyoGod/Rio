import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, JobQueue
import datetime

# 🔹 Your CryptoBot API Key
CRYPTOBOT_SECRET = "335607:AA3yJu1fkPWWbczmD6hw8uesXCiAwzIJWm1"

# In-memory storage for user subscriptions (You can replace this with a database)
subscriptions = {}

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
        "<u>➜ **Choose Your Plan!**</u>\n\n"
        "<u>◆ **Basic Plan**</u>\n"
        "├ Accounts: 1\n"
        "├ Intervals: 5 min\n"
        "└ Price: **$40/week** | **$100/month**\n\n"
        "<u>◆ **Premium Plan**</u>\n"
        "├ Accounts: 4\n"
        "├ Intervals: 30 sec\n"
        "└ Price: **$250/week** | **$500/month**\n\n"
        "<u>◆ **Immortal Plan**</u>\n"
        "├ Accounts: 10\n"
        "├ Intervals: 60 sec\n"
        "└ Price: **$500/week** | **$1000/month**\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "<u>➜ **Select a Plan to Continue Below!**</u>\n\n"
        "For support, contact @Boostadvert."
    )

    keyboard = [
        [InlineKeyboardButton("◆ Basic Plan", callback_data="basic_plan")],
        [InlineKeyboardButton("◆ Premium Plan", callback_data="premium_plan")],
        [InlineKeyboardButton("◆ Immortal Plan", callback_data="immortal_plan")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.effective_chat.send_message(message, reply_markup=reply_markup, parse_mode="HTML")

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
        invoice_id, pay_url = create_invoice(amount, "USDT", user_id)

        if pay_url:
            keyboard = [
                [InlineKeyboardButton("✔ Pay Now", url=pay_url)],
                [InlineKeyboardButton("⟳ Check Payment", callback_data=f"check_{invoice_id}")],
                [InlineKeyboardButton("✖ Cancel Payment", callback_data="cancel_payment")],
                [InlineKeyboardButton("◀ Back", callback_data="back_to_plans")],
            ]
            await query.edit_message_text(
                f"<u>◆ **Payment for {plan.replace('_', ' ').title()} ({duration.title()})**</u>\n\n"
                f"Click **'Pay Now'** to complete the payment.",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="HTML"
            )
        else:
            await query.edit_message_text("⚠ Error: Failed to create invoice. Try again later.")

    elif query.data.startswith("check_"):
        invoice_id = int(query.data.split("_")[1])
        status = check_payment(invoice_id)

        if status == "paid":
            await query.edit_message_text("✔ **Payment received successfully!**\nYour plan is now active.")

            # Save the subscription info (store it in your database for production)
            plan, duration = query.data.split("_")
            expiration_date = datetime.datetime.now() + (datetime.timedelta(weeks=1) if duration == "weekly" else datetime.timedelta(weeks=4))
            subscriptions[user_id] = {
                "plan": plan,
                "expiration": expiration_date
            }
            # Notify user of expiration
            await query.message.reply(f"Your **{plan.replace('_', ' ').title()}** plan will expire on **{expiration_date.strftime('%Y-%m-%d')}**.")

        elif status == "active":
            await query.edit_message_text("◆ **Payment is still pending.**\nPlease wait a moment and try again.")
        elif status == "expired":
            await query.edit_message_text("✖ **Invoice expired!**\nPlease generate a new invoice.")
        else:
            await query.edit_message_text("⚠ **Could not check payment status.** Try again later.")

    elif query.data == "cancel_payment":
        await query.edit_message_text("✖ **Payment cancelled.**\nReturning to plan selection.")
        await purchase_command(update, context)  # Call purchase command again

    elif query.data == "back_to_plans":
        await purchase_command(update, context)  # Call purchase command again to show plans

    else:
        print(f"⚠ DEBUG: Unknown button action → {query.data}")
        await query.edit_message_text("⚠ **Invalid selection. Try again.**")


# 🔹 Job to Check for Expired Plans and Notify User (Async)
async def check_expiration(context: CallbackContext):
    for user_id, subscription in subscriptions.items():
        if subscription["expiration"] < datetime.datetime.now():
            # Send expiration notification
            user = await context.bot.get_chat(user_id)
            await user.send_message(f"Your **{subscription['plan'].replace('_', ' ').title()}** plan has expired. Please renew your subscription.")
            # You can remove expired plans if needed
            del subscriptions[user_id]
