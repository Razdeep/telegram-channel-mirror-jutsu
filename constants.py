from enum import Enum

DOWNLOAD_FOLDER = "downloads"

FILENAME_EXCLUDED_CHAR_REGEX =  r'[^a-zA-Z0-9\-\.\(\) ]'

FILENAME_CHAR_LIMIT = 80

class DownloadStatus(Enum):
    NOT_DOWNLOADED = "no"
    DOWNLOADED = "downloaded"


class UploadStatus(Enum):
    NOT_UPLOADED = "no"
    UPLOADED = "uploaded"
