from telethon import TelegramClient
import re
from config import api_id, api_hash, channel_username

async def fetch_video_urls():
    async with TelegramClient('session_name', api_id, api_hash) as client:
        async for message in client.iter_messages(channel_username, limit=5):
            if message.video:  # Check if the message contains a video
                # Get the direct video file URL (temporary)
                print(f"Video Message ID: {message.id}")
                video = await client.download_media(message.video, file=bytes)
                message_text = message.message
                new_filename = re.sub('[^a-zA-Z ]+', '', message_text)
                new_filename = new_filename[:30]
                with open(f'{new_filename}.mp4', 'wb') as fp:
                    fp.write(video)
                # print(message, end='\n'*3)

if __name__ == "__main__":
    import asyncio
    asyncio.run(fetch_video_urls())