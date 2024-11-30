import asyncio
import download_service, upload_service
import repository
import argparse

parser = argparse.ArgumentParser(description="Kakashi, the telegram channnel copy jutsu")

parser.add_argument('--upload', action='store_true', help="Flag to trigger upload process.")

args = parser.parse_args()

if __name__ == "__main__":
    repository.init_db()
    if args.upload:
        asyncio.run(upload_service.upload_videos())
    else:
        asyncio.run(download_service.download_videos())
    