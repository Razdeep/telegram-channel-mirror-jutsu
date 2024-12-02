from enum import Enum

DOWNLOAD_FOLDER = "downloads"


class DownloadStatus(Enum):
    NOT_DOWNLOADED = "no"
    DOWNLOADED = "downloaded"


class UploadStatus(Enum):
    NOT_UPLOADED = "no"
    UPLOADED = "uploaded"
