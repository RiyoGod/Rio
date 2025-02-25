from telethon import TelegramClient, events
import asyncio

# API Credentials (Get these from https://my.telegram.org/)
API_ID = 21715362  # Replace with your API ID
API_HASH = "e9ee23b30cffbb5081c6318c3a555f5d"  # Replace with your API hash
BOT_TOKEN = "7644887882:AAE8Us4J8-uultwW6ubtYxM7ddLYSiytvXs"  # Replace with your bot token
USER_SESSION = "BQFLWaIAPYzYatgsmv8Ohj3PyPObR6QQ48LR0TFKKvi05ae2qvD8jylY_WxLJkGIrzZHEIqScrDGJv34t7vZO9jM-4z9ACdp7pvBh0SuU6dSuNw4DSUamovXtNzTPuWxPLRrPFGCG3-s4sSau7aQDfE1-SdMs5c7BdB45rQcYVwsBxj5MEnE2PtPNqEvCUlKmtvReAwqjHfBPRgXBgGulhCGB1Cl9GnUNjGGvZ_tRX-9ksKojGxqwUL0WxnfpbOXKqnl0qvczMMnwUKD5fREtBFmbfQEeedhfeUwYzD0Y6E0YEi5ovp632V3lJAtWmhi6Ryi1EC2opZvnt2XlVb4-cANj7dkzQAAAAHJtXFRAA"  # Replace with your userbot session
NEZUKO_BOT = "@im_nezuko_bot"

# Initialize the bot and user client
bot = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)
user = TelegramClient('user', API_ID, API_HASH, sequential_updates=True)

# Dictionary to track conversations
conversations = {}

@bot.on(events.NewMessage)
async def handle_user_message(event):
    user_id = event.sender_id
    message = event.message
    
    # Forward the message to the user account
    sent_msg = await user.send_message(NEZUKO_BOT, message.text)
    
    # Store the conversation tracking
    conversations[sent_msg.id] = user_id

@user.on(events.NewMessage(from_users=NEZUKO_BOT))
async def handle_nezuko_reply(event):
    reply = event.message
    original_msg_id = reply.reply_to_msg_id
    
    if original_msg_id in conversations:
        user_id = conversations.pop(original_msg_id)
        await bot.send_message(user_id, reply.text)

async def main():
    await user.start()
    print("Userbot started!")
    await bot.run_until_disconnected()
    
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
