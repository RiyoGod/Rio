from telethon.sync import TelegramClient
from telethon.tl.functions.channels import GetParticipants, EditBanned
from telethon.tl.types import ChannelParticipantsBanned, ChatBannedRights

# Replace these with your actual details
API_ID = '26416419'
API_HASH = 'c109c77f5823c847b1aeb7fbd4990cc4'
PHONE_NUMBER = 'YOUR_PHONE_NUMBER'  # Your personal Telegram number (like +9198XXXXXX)
CHANNEL_USERNAME = 'YOUR_CHANNEL_USERNAME'  # Example: 'my_channel'

async def main():
    async with TelegramClient('userbot', API_ID, API_HASH) as client:
        await client.start(PHONE_NUMBER)
        
        # Fetch pending join requests (these are technically in "banned" state until approved)
        participants = await client(GetParticipants(
            channel=CHANNEL_USERNAME,
            filter=ChannelParticipantsBanned(''),
            offset=0,
            limit=200,
            hash=0
        ))

        if not participants.users:
            print("No pending join requests.")
            return
        
        # Loop through all pending requests and approve them
        for user in participants.users:
            print(f"Approving {user.first_name}")
            await client(EditBanned(
                channel=CHANNEL_USERNAME,
                user_id=user.id,
                banned_rights=ChatBannedRights(until_date=0)  # This unbans = approves
            ))

        print("All requests approved!")

# Run the script
import asyncio
asyncio.run(main())
