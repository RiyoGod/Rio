from telethon import TelegramClient, events
import asyncio
from pymongo import MongoClient

API_ID = 21715362  # Replace with your API ID
API_HASH = "e9ee23b30cffbb5081c6318c3a555f5d"  # Replace with your API hash
BOT_TOKEN = "7644887882:AAE8Us4J8-uultwW6ubtYxM7ddLYSiytvXs"  # Replace with your bot token
USER_SESSION = "YOUR_USER_SESSION"  # Replace with your userbot session
NEZUKO_BOT = "@im_nezuko_bot"

# Initialize MongoDB
mongo_client = MongoClient("mongodb+srv://Seller8:buyed9@cluster0.eiyva.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = mongo_client["chatbot_db"]
settings_collection = db["settings"]

# Initialize the bot and user client
bot = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)
user = TelegramClient('user', API_ID, API_HASH, sequential_updates=True)

conversations = {}

def is_chatbot_enabled(chat_id):
    setting = settings_collection.find_one({"chat_id": chat_id})
    return setting is None or setting.get("enabled", True)

def set_chatbot_status(chat_id, status):
    settings_collection.update_one({"chat_id": chat_id}, {"$set": {"enabled": status}}, upsert=True)

async def is_admin(chat, user_id):
    try:
        participants = await bot.get_participants(chat, filter=telethon.tl.types.ChannelParticipantsAdmins)
        return any(p.id == user_id for p in participants)
    except Exception:
        return False

@bot.on(events.NewMessage(pattern='/chatbot (enable|disable)'))
async def chatbot_toggle(event):
    chat_id = event.chat_id
    sender = await event.get_sender()
    
    if event.is_group:
        if not await is_admin(chat_id, sender.id):
            await event.reply("Only admins can change chatbot settings in groups.")
            return
    
    status = event.pattern_match.group(1) == "enable"
    set_chatbot_status(chat_id, status)
    await event.reply(f"Chatbot {'enabled' if status else 'disabled'} successfully.")

@bot.on(events.NewMessage)
async def handle_user_message(event):
    chat_id = event.chat_id
    message = event.message
    
    if not is_chatbot_enabled(chat_id):
        return
    
    async with bot.action(chat_id, 'typing'):
        sent_msg = await user.send_message(NEZUKO_BOT, message)
        conversations[sent_msg.id] = (chat_id, message.id)

@user.on(events.NewMessage(from_users=NEZUKO_BOT))
async def handle_nezuko_reply(event):
    reply = event.message
    original_msg_id = reply.reply_to_msg_id
    
    if original_msg_id in conversations:
        chat_id, user_msg_id = conversations.pop(original_msg_id)
        
        if not is_chatbot_enabled(chat_id):
            return
        
        if reply.voice:
            async with bot.action(chat_id, 'record_audio'):
                await bot.send_file(chat_id, reply.voice, reply_to=user_msg_id)
        else:
            text_response = reply.text.replace("Nezuko", "Mitsuha 💗")
            text_response = ' '.join(['@UncountableAura' if word.startswith('@') else word for word in text_response.split()])
            await bot.send_message(chat_id, text_response, reply_to=user_msg_id)

async def main():
    await user.start()
    print("Userbot started!")
    await bot.run_until_disconnected()
    
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
