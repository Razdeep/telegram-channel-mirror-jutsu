import asyncio
import download_service
import upload_service
import repository
import argparse
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s]: %(message)s",
    datefmt="%d/%b/%Y %H:%M:%S",
    stream=sys.stdout,
)

parser = argparse.ArgumentParser(description="Telegram Channel Mirror Jutsu")

parser.add_argument(
    "--upload-only", action="store_true", help="Flag to trigger only upload process."
)

parser.add_argument(
    "--download-only",
    action="store_true",
    help="Flag to trigger only download process.",
)

args = parser.parse_args()

if __name__ == "__main__":
    repository.init_db()
    if args.upload_only:
        asyncio.run(upload_service.upload_videos(cleanup=True))
    elif args.download_only:
        asyncio.run(download_service.download_videos(also_upload=False))
    else:
        asyncio.run(download_service.download_videos(also_upload=True))
