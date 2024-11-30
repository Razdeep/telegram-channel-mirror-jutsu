from telethon import TelegramClient
import re
from config import api_id, api_hash, channel_id_source, channel_id_destination
import sqlite3
import asyncio
from pathlib import Path
import logging
from repository import conn
import constants
import upload_service, download_service, repository

if __name__ == "__main__":
    # init_db()
    asyncio.run(download_service.download_videos())
    # asyncio.run(upload_service.upload_videos())