import asyncio
import logging
import os
from telethon import TelegramClient, events
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# Bot Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN" , "8180105447:AAH9btPiiHLkRPGRnnsQ-31tcpyRp4-zZyM")
API_ID = int(os.getenv("API_ID" , 26416419))
API_HASH = os.getenv("API_HASH" , "c109c77f5823c847b1aeb7fbd4990cc4")
MONGO_URI = os.getenv("MONGO_URI" , "mongodb+srv://jc07cv9k3k:bEWsTrbPgMpSQe2z@cluster0.nfbxb.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
DB_NAME = "auto_reply_bot"

# Initialize MongoDB
mongo_client = MongoClient(MONGO_URI)
db = mongo_client[DB_NAME]
accounts_collection = db["accounts"]
responses_collection = db["responses"]

# Dictionary to store user clients
user_clients = {}

# Initialize Bot
bot = TelegramClient("bot_session", API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# Function to add a new user account
async def add_user_account(phone_number):
    client = TelegramClient(f"sessions/{phone_number}", API_ID, API_HASH)
    await client.connect()

    if not await client.is_user_authorized():
        return "❌ Login required! Please login manually."
    
    me = await client.get_me()
    user_clients[me.id] = client
    accounts_collection.update_one({"user_id": me.id}, {"$set": {"phone": phone_number}}, upsert=True)
    
    return f"✅ Account `{me.first_name}` (`{me.id}`) added successfully!"

# Command to list hosted accounts
@bot.on(events.NewMessage(pattern="/accounts"))
async def list_accounts(event):
    accounts = list(accounts_collection.find({}))
    if not accounts:
        await event.reply("⚠️ No accounts are hosted!")
        return
    
    msg = "**📋 Hosted Accounts:**\n"
    for acc in accounts:
        msg += f"- `{acc['phone']}`\n"
    await event.reply(msg)

# Command to set group reply message
@bot.on(events.NewMessage(pattern="/setgroup (.+)"))
async def set_group_reply(event):
    user_id = event.sender_id
    message = event.pattern_match.group(1)
    
    responses_collection.update_one({"user_id": user_id}, {"$set": {"group_reply": message}}, upsert=True)
    await event.reply("✅ Group auto-reply set successfully!")

# Command to set DM reply message
@bot.on(events.NewMessage(pattern="/setdm (.+)"))
async def set_dm_reply(event):
    user_id = event.sender_id
    message = event.pattern_match.group(1)
    
    responses_collection.update_one({"user_id": user_id}, {"$set": {"dm_reply": message}}, upsert=True)
    await event.reply("✅ DM auto-reply set successfully!")

# Monitor hosted user accounts
async def monitor_accounts():
    while True:
        for user_id, client in user_clients.items():
            # Monitor Group Mentions
            @client.on(events.NewMessage)
            async def auto_reply(event):
                user_response = responses_collection.find_one({"user_id": user_id})
                
                if event.is_private and user_response and "dm_reply" in user_response:
                    await event.reply(user_response["dm_reply"])
                
                elif event.mentioned and user_response and "group_reply" in user_response:
                    await event.reply(user_response["group_reply"])

        await asyncio.sleep(5)  # Avoid excessive polling

# Start the bot
async def main():
    asyncio.create_task(monitor_accounts())
    await bot.run_until_disconnected()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
