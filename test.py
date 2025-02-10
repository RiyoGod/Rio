import asyncio
import logging
import os
from telethon import TelegramClient, events
from pymongo import MongoClient
from dotenv import load_dotenv

# Load Environment Variables
load_dotenv()

# Bot Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN", "8180105447:AAH9btPiiHLkRPGRnnsQ-31tcpyRp4-zZyM")
API_ID = int(os.getenv("API_ID", 26416419))
API_HASH = os.getenv("API_HASH", "c109c77f5823c847b1aeb7fbd4990cc4")
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://jc07cv9k3k:bEWsTrbPgMpSQe2z@cluster0.nfbxb.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
DB_NAME = "auto_reply_bot"

# MongoDB Connection
mongo_client = MongoClient(MONGO_URI)
db = mongo_client[DB_NAME]
accounts_collection = db["accounts"]
replies_collection = db["replies"]

# Dictionary to store active userbot clients
active_clients = {}

# Enable Debug Logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

# Main Telegram Bot
bot = TelegramClient("bot", API_ID, API_HASH)
bot.start(bot_token=BOT_TOKEN)


async def start_userbot(session_name, api_id, api_hash, phone):
    """ Start a userbot session for an account """
    try:
        client = TelegramClient(session_name, api_id, api_hash)

        await client.connect()
        if not await client.is_user_authorized():
            await client.send_code_request(phone)
            code = input(f"Enter the code for {phone}: ")
            await client.sign_in(phone, code)

        active_clients[phone] = client

        # Load auto-reply settings
        user_replies = replies_collection.find_one({"phone": phone}) or {}

        @client.on(events.NewMessage(incoming=True))
        async def auto_reply(event):
            chat_id = event.chat_id
            sender = await event.get_sender()
            message_text = event.message.message

            logging.debug(f"Received message in chat {chat_id} from {sender.id}: {message_text}")

            if event.is_private and "dm_reply" in user_replies:
                await event.reply(user_replies["dm_reply"])
                logging.info(f"Sent DM reply to {sender.id}")
            elif event.is_group and sender.username in message_text:
                if "group_reply" in user_replies:
                    await event.reply(user_replies["group_reply"])
                    logging.info(f"Sent group reply in chat {chat_id}")

        logging.info(f"✅ Userbot for {phone} started successfully!")

        await client.run_until_disconnected()

    except Exception as e:
        logging.error(f"❌ Error starting userbot for {phone}: {e}")


@bot.on(events.NewMessage(pattern="/login"))
async def login_account(event):
    """ Command to login a new userbot account """
    try:
        args = event.raw_text.split(" ")
        if len(args) < 4:
            await event.reply("Usage: /login <api_id> <api_hash> <phone>")
            return

        api_id, api_hash, phone = args[1], args[2], args[3]

        logging.debug(f"Received /login command: API_ID={api_id}, API_HASH={api_hash}, PHONE={phone}")

        accounts_collection.insert_one({"phone": phone, "api_id": api_id, "api_hash": api_hash})

        asyncio.create_task(start_userbot(phone, api_id, api_hash, phone))

        await event.reply(f"✅ Account `{phone}` logged in and hosted successfully!")
        logging.info(f"✅ Account {phone} stored in MongoDB and hosted.")

    except Exception as e:
        logging.error(f"❌ Error in /login command: {e}")
        await event.reply("❌ Failed to login. Check logs for errors.")


@bot.on(events.NewMessage(pattern="/setgroup"))
async def set_group_reply(event):
    """ Set auto-reply message for group mentions """
    try:
        args = event.raw_text.split(" ", 1)
        if len(args) < 2:
            await event.reply("Usage: /setgroup <message>")
            return

        phone = event.sender_id
        replies_collection.update_one({"phone": phone}, {"$set": {"group_reply": args[1]}}, upsert=True)

        await event.reply("✅ Group mention auto-reply message set!")
        logging.info(f"✅ Group auto-reply set for {phone}: {args[1]}")

    except Exception as e:
        logging.error(f"❌ Error in /setgroup command: {e}")
        await event.reply("❌ Failed to set group auto-reply.")


@bot.on(events.NewMessage(pattern="/setdm"))
async def set_dm_reply(event):
    """ Set auto-reply message for direct messages """
    try:
        args = event.raw_text.split(" ", 1)
        if len(args) < 2:
            await event.reply("Usage: /setdm <message>")
            return

        phone = event.sender_id
        replies_collection.update_one({"phone": phone}, {"$set": {"dm_reply": args[1]}}, upsert=True)

        await event.reply("✅ DM auto-reply message set!")
        logging.info(f"✅ DM auto-reply set for {phone}: {args[1]}")

    except Exception as e:
        logging.error(f"❌ Error in /setdm command: {e}")
        await event.reply("❌ Failed to set DM auto-reply.")


@bot.on(events.NewMessage(pattern="/accounts"))
async def list_accounts(event):
    """ List all hosted Telegram accounts """
    try:
        accounts = accounts_collection.find()
        message = "**📜 Hosted Accounts:**\n"

        for acc in accounts:
            message += f"📱 `{acc['phone']}`\n"

        logging.info("✅ Retrieved account list.")

        await event.reply(message if message != "**📜 Hosted Accounts:**\n" else "No accounts hosted.")

    except Exception as e:
        logging.error(f"❌ Error in /accounts command: {e}")
        await event.reply("❌ Failed to retrieve accounts list.")


if __name__ == "__main__":
    logging.info("🚀 Starting Telegram bot...")

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(bot.run_until_disconnected())
    except KeyboardInterrupt:
        logging.warning("❌ Bot stopped manually.")
    finally:
        loop.close()
