import constants
from telethon import TelegramClient
from telethon.tl.types import DocumentAttributeVideo
from config import api_id, api_hash, channel_id_destination
from pathlib import Path
from repository import conn
import logging
from moviepy.editor import VideoFileClip


def compute_video_details(filepath: str):
    clip = VideoFileClip(filepath)
    duration = int(clip.duration)  # Duration in seconds
    width, height = clip.size  # Aspect ratio
    clip.close()
    return [duration, width, height]


async def upload_video(filename):
    filepath = f"{constants.DOWNLOAD_FOLDER}/{filename}"
    # Ensure the video file exists
    if not Path(filepath).exists():
        logging.info(f"File not found: {filepath}")
        return False

    duration, width, height = compute_video_details(filepath)

    if duration * width * height == 0:
        logging.error(f"duration or width or height is 0, please check {filename}")
        return False

    async with TelegramClient("session_name", api_id, api_hash) as client:
        logging.info(f"Uploading video: {filepath}")
        # Send the video to the private channel
        message = await client.send_file(
            entity=channel_id_destination,
            file=filepath,
            caption=filename,
            supports_streaming=True,
            attributes=[
                DocumentAttributeVideo(
                    duration=duration,
                    w=width,
                    h=height,
                    supports_streaming=True,  # Allows streaming in Telegram
                )
            ],
        )
        logging.info(f"Video uploaded successfully. Message ID: {message.id}")

    return True


async def upload_videos(cleanup=True):
    for message_id, filename in get_pending_videos_to_upload():
        upload_successful = await upload_video(filename)
        if upload_successful:
            update_upload_status(message_id, "uploaded")
        if cleanup:
            delete_video(filename)


def delete_video(filename: str):
    file_path = Path(f"{constants.DOWNLOAD_FOLDER}/{filename}")
    if file_path.exists():
        file_path.unlink()


def update_upload_status(message_id: str, status_text: str):
    cursor = conn.cursor()

    cursor.execute(
        """
    UPDATE messages set upload_status=? WHERE message_id=?
    """,
        (status_text, message_id),
    )

    conn.commit()


def get_pending_videos_to_upload():
    cursor = conn.cursor()

    cursor.execute("""
    SELECT message_id, new_filename from messages
                   where not upload_status = "uploaded"
    """)

    res = [item for item in cursor.fetchall()]

    return res
