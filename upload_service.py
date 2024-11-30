import constants
from telethon import TelegramClient
import re
from config import api_id, api_hash, channel_id_source, channel_id_destination
import sqlite3
import asyncio
from pathlib import Path
import logging
from repository import conn


async def upload_video(filename):
    filepath = f'{constants.DOWNLOAD_FOLDER}/{filename}'
    # Ensure the video file exists
    if not Path(filepath).exists():
        print(f"File not found: {filepath}")
        return
    
    async with TelegramClient('session_name', api_id, api_hash) as client:
        print(f"Uploading video: {filepath}")
        # Send the video to the private channel
        message = await client.send_file(
            entity=channel_id_destination,
            file=filepath,
            caption=filename,
            supports_streaming=True
        )
        print(f"Video uploaded successfully. Message ID: {message.id}")


async def upload_videos():
    for message_id, filename in get_pending_videos_to_upload():
        await upload_video(filename)
        update_upload_status(message_id, 'uploaded')

def update_upload_status(message_id: str, status_text: str):
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE messages set upload_status=? WHERE message_id=?
    """, (status_text, message_id))

    conn.commit()

def get_pending_videos_to_upload():
    cursor = conn.cursor()

    cursor.execute("""
    SELECT message_id, new_filename from messages
                   where not upload_status = "uploaded"
    """)

    res = [item for item in cursor.fetchall()]

    return res