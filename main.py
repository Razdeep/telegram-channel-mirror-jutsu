from telethon import TelegramClient
import re
from config import api_id, api_hash, channel_username
import sqlite3
import asyncio
from pathlib import Path

download_folder = 'downloads'

conn = sqlite3.connect("messages.db")

# Initialize SQLite Database
def init_db():
    cursor = conn.cursor()
    # Create a table to store messages if it doesn't exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY,
        new_filename TEXT,
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
        async for message in client.iter_messages(channel_username, limit=5, reverse=True):
            if not message.video:
                print(f'skipping message id {message.id}, because it is not video')
                continue
            print(f"Downloading video Message ID: {message.id}, video size: {message.video.size // (1024*1024)} MB approx")
            # video = await client.download_media(message.video, file=bytes)
            new_filename = generate_new_filename(message.message, message.id)

            put_download_entry_in_db(int(message.id), new_filename, str(message.message))
            
            # with open(f'{download_folder}/{new_filename}', 'wb') as fp:
            #     fp.write(video)

def get_current_timestamp():
    from datetime import datetime
    current_datetime = datetime.now()
    datetime_string = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
    return str(datetime_string)

def put_download_entry_in_db(message_id: int, new_filename: str, message: str):
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO messages("id","new_filename","download_status","upload_status","content","download_timestamp","upload_timestamp") 
                   VALUES (?,?,?,?,?,?,?);
    ''', (int(message_id),new_filename,'downloading','not started', str(message),str(get_current_timestamp),''))
    conn.commit()

if __name__ == "__main__":
    init_db()
    asyncio.run(download_videos())
