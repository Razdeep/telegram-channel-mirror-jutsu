import constants


def get_absolute_downloads_path(filename: str):
    return f"{constants.DOWNLOAD_FOLDER}/{filename}"


def get_thumbnail_name_from_video_filename(video_filename: str):
    return f"{video_filename[0:len(video_filename) - 4]}.jpg"
