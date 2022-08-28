"""
Extract all image attachments from all discord channel's history and base 64 encode them.
Save the base 64 encoded images a mongodb collection
"""
import asyncio
import discord
import traceback
import io

from shared.mongodb import discord_message_collection, discord_channel_collection
import shared.settings as settings
from shared.images import get_image_bitmap, base_64_encode_bitmap

intents = discord.Intents.default()
client = discord.Client(intents=intents)


def update_cursor(message: discord.Message) -> None:
    """
    Update the cursor for a channel.
    """
    print(f"Updating cursor for channel {message.channel.id} to {message.id}")
    discord_channel_collection.update_one(
        { "id": message.channel.id }, 
        { "$set": {"image_cursor": message.id} }
    )

def setup_channel(channel_id) -> None:
    """
    Setup a channel for indexing.
    """
    print(f"Setting up channel {channel_id}")
    discord_channel_collection.insert_one({
        "id": channel_id,
        "image_cursor": None
    })

def find_channel_record(channel_id): 
    """
    Find the record for a channel.
    """
    print(f"Finding channel record for {channel_id}")
    record=discord_channel_collection.find_one({"id": channel_id})
    if record is None: 
        print(f"No record found for {channel_id}")
        setup_channel(channel_id)
        record=discord_channel_collection.find_one({"id": channel_id})
    else:
        print(f"Found channel record for {channel_id}")
    print(f"Channel record: {record}")
    return record

async def get_image_attachments(message):
    """
    Get all image attachments from a discord message
    """
    image_attachments=[]
    for attachment in message.attachments:
        if attachment.filename.endswith('.png') or attachment.filename.endswith('.jpg'):
            file_like=io.BytesIO(await attachment.read())
            image_attachments.append(base_64_encode_bitmap(get_image_bitmap(file_like)))
    return image_attachments



async def next_messages(channel: discord.TextChannel):
    """
    Get the next batch of messages in a channel.
    """
    channel_record = find_channel_record(channel.id)
    print  (f"Cursor: {channel_record.get('image_cursor', None)}")
    print(f"Getting history for {channel_record}")

    if not channel_record.get('is_valid', True):
        print(f"Channel {channel_record['id']} is not valid")
        return []
    if channel_record.get("image_cursor",None) is None:
        print(f"No cursor found for {channel_record['id']}")
        try:
            return [message async for message in channel.history(limit=200, oldest_first=True)]
        # mark channel as invalid if there is an error
        except  Exception as e:
            print(f"Error getting history for {channel_record['id']}")
            print(e)
            discord_channel_collection.update_one({"id": channel_record['id']},{"$set":{"is_valid":False}})
            return []
    else:
        print(f"Cursor found for {channel} {channel_record['image_cursor']}")
        try:
            return [message async for message in channel.history(limit=200,
                                                                 oldest_first=True,
                                                                 after=channel.get_partial_message(
                                                                     channel_record.get('image_cursor', None)
                                                                 ))]
        except AttributeError as e:
            print(f"Attribute error for {channel.id}")
            print(e)
            return []

async def index_channel(channel: discord.TextChannel) -> None:
    """
    Index all messages in a channel.
    """
    newest_message = None
    print(f"Indexing channel {channel}")
    for message in await next_messages(channel):
        await asyncio.sleep(0.1)
        newest_message = message
        await index_message(message)
    if newest_message is not None:
        update_cursor(newest_message)
    print(f"Newest message: {newest_message}")

async def index_message(message: discord.Message) -> None:
    """
    Index a message only if it has not already been added to mongo.
    """
    message_record = discord_message_collection.find_one({"id": message.id})
    if message_record is not None:
        print(f"Indexing message {message.id} {message.content}")
        discord_message_collection.update_one({"id": message.id},
                                              {"$set":{"attachments": await get_image_attachments(message)}})

@client.event
async def on_ready():
    while True:
        for channel in client.get_all_channels():
            try:
                if isinstance(channel, discord.TextChannel):
                    print(f"Indexing channel {channel}")
                    await asyncio.sleep(1)
                    await index_channel( channel )
            except Exception as e:
                await asyncio.sleep(10)
                print("something happened:")
                print(e)
                traceback.print_exc()

client.run(settings.DISCORD_TOKEN)
