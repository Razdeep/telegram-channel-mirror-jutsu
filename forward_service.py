from telethon import TelegramClient
import config
import logging
import asyncio
import time
import sys

# Replace these with your API credentials
api_id = config.api_id
api_hash = config.api_hash


async def forward_existing_messages():
    try:
        async with TelegramClient("download_session", api_id, api_hash) as client:
            '''
            async for message in client.iter_messages(
                config.forward_channel_id_source, limit=4000, reverse=True
            ):
                if not message.video:
                    logging.info(
                        f"skipping message id {message.id}, because it is not video"
                    )
                    continue
                await client.send_message(
                    config.forward_channel_id_destination, message
                )
                logging.info(f"Message forwarded: {message.text}")
                time.sleep(0.5)
            '''
            async for message in client.iter_messages(config.forward_channel_id_source):
                await client.forward_messages(entity=config.forward_channel_id_destination, messages=message.id, from_peer=config.forward_channel_id_source)
                logging.info("{message.id} message forwarded successfully!")
    except Exception as e:
        logging.exception(f"Failed to forward messages: {e}")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s]: %(message)s",
        datefmt="%d/%b/%Y %H:%M:%S",
        stream=sys.stdout,
    )
    asyncio.run(forward_existing_messages())
