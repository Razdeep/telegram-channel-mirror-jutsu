from telethon import TelegramClient
import config
import logging
import asyncio

# Replace these with your API credentials
api_id = config.api_id
api_hash = config.api_hash


async def forward_existing_messages():
    try:
        async with TelegramClient("download_session", api_id, api_hash) as client:
            async for message in client.iter_messages(
                config.forward_channel_id_source, limit=4000, reversed=True
            ):
                await client.send_message(
                    config.forward_channel_id_destination, message
                )
                logging.info(f"Message forwarded: {message.text}")
    except Exception as e:
        logging.exception(f"Failed to forward messages: {e}")


if __name__ == "__main__":
    asyncio.run(forward_existing_messages())
