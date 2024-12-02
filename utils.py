import constants
from pathlib import Path


def get_absolute_downloads_path(filename: str):
    return f"{constants.DOWNLOAD_FOLDER}/{filename}"


def get_thumbnail_name_from_video_filename(video_filename: str):
    return f"{video_filename[0:len(video_filename) - 4]}.jpg"


def delete_file(filename: str):
    file_path = Path(get_absolute_downloads_path(filename))
    if file_path.exists():
        file_path.unlink()


def delete_video_and_thumbnail(video_filename: str):
    thumbnail_filename = get_thumbnail_name_from_video_filename(video_filename)
    delete_file(video_filename)
    delete_file(thumbnail_filename)
