import asyncio
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext, MessageHandler, filters
from RioAdBot.plugins.purchase import check_payment

# Log group ID (replace with your actual log group ID)
LOG_GROUP_ID = -1002314243507  # Replace with your log group ID

# Dictionary to track users who need to submit an ad
pending_ads = {}

async def request_ad(update: Update, context: CallbackContext):
    """Ask the user to send their ad after payment verification."""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    invoice_id = query.data.split("_")[1]

    # Check payment status
    status = check_payment(int(invoice_id))

    if status == "paid":
        pending_ads[user_id] = invoice_id
        await query.message.reply_text(
            "**✅ Payment confirmed!**\n\n"
            "**Now, please send your ad message (text, image, or video).**",
            parse_mode="Markdown"
        )
    else:
        await query.message.reply_text(
            "⚠ **Payment not verified.** Please complete the payment first.",
            parse_mode="Markdown"
        )

async def receive_ad(update: Update, context: CallbackContext):
    """Handle ad submission and forward it to the log group."""
    user = update.effective_user
    user_id = user.id

    if user_id not in pending_ads:
        return  # Ignore messages from users who haven't paid

    invoice_id = pending_ads.pop(user_id)

    # Fetch plan details (you may store plan details in the database)
    purchased_plan = "Unknown Plan"  # You can fetch actual details based on the invoice

    # Forward the ad to the log group
    sent_message = await update.message.forward(chat_id=LOG_GROUP_ID)

    # Send details about the purchase
    await context.bot.send_message(
        chat_id=LOG_GROUP_ID,
        text=(
            f"**📢 New Ad Submission**\n"
            f"**👤 User:** [{user.first_name}](tg://user?id={user_id})\n"
            f"**💳 Purchased Plan:** {purchased_plan}\n"
            f"**📜 Ad ID:** `{sent_message.message_id}`"
        ),
        parse_mode="Markdown"
    )

    await update.message.reply_text(
        "**✅ Your ad has been submitted successfully!**",
        parse_mode="Markdown"
    )

# Add handlers (ensure these are registered in your bot's main script)
ad_handler = MessageHandler(filters.ALL, receive_ad)
