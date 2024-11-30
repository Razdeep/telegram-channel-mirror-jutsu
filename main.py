import asyncio
import download_service

if __name__ == "__main__":
    # init_db()
    asyncio.run(download_service.download_videos())
    # asyncio.run(upload_service.upload_videos())