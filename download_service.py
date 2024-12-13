from telethon import TelegramClient
import re
from config import api_id, api_hash, channel_id_source
import sqlite3
from pathlib import Path
import logging
from repository import conn
import constants
import upload_service

# import asyncio
import utils

def check_filename_already_exists_in_local(filename):
    return Path(utils.get_absolute_downloads_path(filename)).exists()


def generate_new_filename(message_text, message_id):
    if message_text == "":
        return f"{message_id}.mp4"
    new_filename = re.sub(constants.FILENAME_REGEX_PATTERN, "", message_text)[:30].strip()
    if new_filename == "":
        return f"{message_id}.mp4"
    if check_filename_already_exists_in_local(f"{new_filename}.mp4"):
        new_filename = f"{new_filename}_{message_id}"
    new_filename = f"{new_filename}.mp4"
    return new_filename


async def download_videos(also_upload=False):
    async with TelegramClient("download_session", api_id, api_hash) as client:
        async for message in client.iter_messages(
            channel_id_source, limit=1000, reverse=True
        ):
            if not message.video:
                logging.info(
                    f"skipping message id {message.id}, because it is not video"
                )
                continue

            new_filename = generate_new_filename(message.message, message.id)

            should_download = check_should_download(int(message.id))

            if not should_download:
                logging.info(
                    f"skipping message id {message.id}, because {new_filename} was already downloaded before"
                )
                continue

            put_download_entry_in_db(
                int(message.id), new_filename, str(message.message)
            )

            logging.info(
                f"Downloading video Message ID: {message.id}, filename: {new_filename}, video size: {message.video.size // (1024*1024)} MB approx"
            )

            try:
                video = await client.download_media(message.video, file=bytes)
            except Exception as ex:
                logging.error(f"error downloading {new_filename}")
                logging.exception(ex)
                continue

            with open(f"{constants.DOWNLOAD_FOLDER}/{new_filename}", "wb") as fp:
                fp.write(video)

            update_download_status(
                message.id, constants.DownloadStatus.DOWNLOADED.value
            )

            if also_upload:
                cleanup = True
                # executor = deadpool.SingletonExecutor()
                # executor.submit(
                #     upload_service.run_upload_workflow,
                #     message.id,
                #     new_filename,
                #     cleanup,
                # )

                # asyncio.create_task(
                #     upload_service.run_upload_workflow(
                #         message.id, new_filename, cleanup
                #     )
                # )

                await upload_service.run_upload_workflow(
                    message.id, new_filename, cleanup
                )


def update_download_status(message_id: str, status_text: str):
    cursor = conn.cursor()

    cursor.execute(
        """
    UPDATE messages set download_status=? WHERE message_id=?
    """,
        (status_text, message_id),
    )

    conn.commit()
    cursor.close()


def get_current_timestamp():
    from datetime import datetime

    current_datetime = datetime.now()
    datetime_str = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
    return str(datetime_str)


def check_should_download(message_id: int):
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
        select message_id,download_status from messages where message_id=?
        """,
            (message_id,),
        )
        res = [item for item in cursor.fetchall()]
        if len(res) == 0:
            return True
        if res[0][1] == constants.DownloadStatus.DOWNLOADED.value:
            return False
    except Exception as ex:
        logging.exception(ex)
    return True


def put_download_entry_in_db(message_id: int, new_filename: str, message: str):
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
        INSERT INTO messages("message_id","new_filename","download_status","upload_status","content","download_timestamp","upload_timestamp") 
                    VALUES (?,?,?,?,?,?,?);
        """,
            (
                int(message_id),
                new_filename,
                constants.DownloadStatus.NOT_DOWNLOADED.value,
                constants.UploadStatus.NOT_UPLOADED.value,
                str(message),
                "",
                "",
            ),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        return False
    except Exception as ex:
        logging.exception(ex)
        return False
    return True
