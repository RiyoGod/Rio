from telethon import TelegramClient, events
from pymongo import MongoClient
import asyncio

API_ID = 21715362
API_HASH = "e9ee23b30cffbb5081c6318c3a555f5d"
BOT_TOKEN = "7644887882:AAE8Us4J8-uultwW6ubtYxM7ddLYSiytvXs"
USER_SESSION = "BQFLWaIAPYz..."  # Replace with your user session
NEZUKO_BOT = "@im_nezuko_bot"

# MongoDB setup
mongo_client = MongoClient("mongodb+srv://Seller8:buyed9@cluster0.eiyva.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = mongo_client["chatbot_db"]
chatbot_settings = db["chatbot_settings"]

# Initialize bot and user client
bot = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)
user = TelegramClient('user', API_ID, API_HASH, sequential_updates=True)
conversations = {}

def is_chatbot_enabled(chat_id):
    setting = chatbot_settings.find_one({"chat_id": chat_id})
    return setting is None or setting.get("enabled", True)

@bot.on(events.NewMessage(pattern=r"/chatbot (enable|disable)"))
async def chatbot_toggle(event):
    chat_id = event.chat_id
    sender = await event.get_sender()
    chat = await event.get_chat()

    if chat and hasattr(chat, "admin_rights") and chat.admin_rights:
        is_admin = chat.admin_rights.is_admin
    else:
        is_admin = False
    
    if not is_admin:
        await event.reply("Only admins can enable/disable the chatbot.")
        return
    
    action = event.pattern_match.group(1)
    if action == "enable":
        chatbot_settings.update_one({"chat_id": chat_id}, {"$set": {"enabled": True}}, upsert=True)
        await event.reply("Chatbot has been enabled.")
    else:
        chatbot_settings.update_one({"chat_id": chat_id}, {"$set": {"enabled": False}}, upsert=True)
        await event.reply("Chatbot has been disabled.")

@bot.on(events.NewMessage)
async def handle_user_message(event):
    chat_id = event.chat_id
    message = event.message.text
    
    if not is_chatbot_enabled(chat_id):
        return
    
    message = message.replace("Nezuko", "Mitsuha 💗")
    if "@" in message:
        message = "@UncountableAura"
    
    async with bot.action(chat_id, 'typing'):
        sent_msg = await user.send_message(NEZUKO_BOT, message)
        conversations[sent_msg.id] = chat_id

@user.on(events.NewMessage(from_users=NEZUKO_BOT))
async def handle_nezuko_reply(event):
    reply = event.message
    original_msg_id = reply.reply_to_msg_id
    
    if original_msg_id in conversations:
        chat_id = conversations.pop(original_msg_id)
        
        if reply.voice:
            async with bot.action(chat_id, 'record_audio'):
                await bot.send_file(chat_id, reply.voice)
        else:
            text = reply.text.replace("Nezuko", "Mitsuha 💗")
            if "@" in text:
                text = "@UncountableAura"
            await bot.send_message(chat_id, text)

async def main():
    await user.start()
    print("Userbot started!")
    await bot.run_until_disconnected()
    
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
