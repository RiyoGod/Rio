from telethon import TelegramClient, events
import asyncio

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
    chat_id = event.chat_id
    message = event.message
    
    # Show typing action
    async with bot.action(chat_id, 'typing'):
        # Forward the message to the user account
        sent_msg = await user.send_message(NEZUKO_BOT, message)
        
        # Store the conversation tracking
        conversations[sent_msg.id] = chat_id

@user.on(events.NewMessage(from_users=NEZUKO_BOT))
async def handle_nezuko_reply(event):
    reply = event.message
    original_msg_id = reply.reply_to_msg_id
    
    if original_msg_id in conversations:
        chat_id = conversations.pop(original_msg_id)
        
        # Forward text and voice messages in both groups and private chats
        if reply.voice:
            await bot.send_file(chat_id, reply.voice)
        else:
            await bot.send_message(chat_id, reply.text)

async def main():
    await user.start()
    print("Userbot started!")
    await bot.run_until_disconnected()
    
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
