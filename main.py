from telethon import TelegramClient
import re
from config import api_id, api_hash, channel_id_source, channel_id_destination
import sqlite3
import asyncio
from pathlib import Path
import logging

DOWNLOAD_FOLDER = 'downloads'

conn = sqlite3.connect("messages.db")

# Initialize SQLite Database
def init_db():
    cursor = conn.cursor()
    # Create a table to store messages if it doesn't exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        message_id INTEGER PRIMARY KEY,
        new_filename TEXT UNIQUE,
        download_status TEXT,
        upload_status TEXT,
        content TEXT,
        download_timestamp TEXT,
        upload_timestamp timestamp TEXT
    )
    """)
    conn.commit()
    return conn

def check_filename_already_exists_in_local(filename):
    return Path(filename).exists()

def generate_new_filename(message_text, message_id):
    if message_text == '':
        return f'{message_id}.mp4'
    new_filename = re.sub('[^a-zA-Z ]+', '', message_text)[:30]
    if check_filename_already_exists_in_local(new_filename):
        new_filename = f'{new_filename}_{message_id}'
    new_filename = f'{new_filename}.mp4'
    return new_filename

async def download_videos():
    async with TelegramClient('session_name', api_id, api_hash) as client:
        async for message in client.iter_messages(channel_id_source, limit=100, reverse=True):
            if not message.video:
                print(f'skipping message id {message.id}, because it is not video')
                continue
            
            new_filename = generate_new_filename(message.message, message.id)

            should_download = put_download_entry_in_db(int(message.id), new_filename, str(message.message))

            if not should_download:
                print(f'skipping message id {message.id}, because it was already downloaded before')
                continue

            print(f"Downloading video Message ID: {message.id}, video size: {message.video.size // (1024*1024)} MB approx")

            video = await client.download_media(message.video, file=bytes)
            
            with open(f'{DOWNLOAD_FOLDER}/{new_filename}', 'wb') as fp:
                fp.write(video)

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

async def upload_video(filename):
    filepath = f'{DOWNLOAD_FOLDER}/{filename}'
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

def get_current_timestamp():
    from datetime import datetime
    current_datetime = datetime.now()
    datetime_str = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
    return str(datetime_str)

def put_download_entry_in_db(message_id: int, new_filename: str, message: str):
    cursor = conn.cursor()
    try:
        cursor.execute('''
        INSERT INTO messages("message_id","new_filename","download_status","upload_status","content","download_timestamp","upload_timestamp") 
                    VALUES (?,?,?,?,?,?,?);
        ''', (int(message_id),new_filename,'downloading','not started', str(message),'',''))
        conn.commit()
    except sqlite3.IntegrityError:
        return False
    except Exception as ex:
        logging.exception(ex)
        return False
    return True

if __name__ == "__main__":
    init_db()
    asyncio.run(download_videos())
    # asyncio.run(upload_videos())