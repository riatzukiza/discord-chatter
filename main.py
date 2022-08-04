from bot_src.main import start_discord, client, handle_replies
from bot_src.threads import start_threads
from bot_src.data import messages, labels
from operator import itemgetter
from bot_src.database import get_database
db=get_database()

message_collection=db[f'discord_messages']

import asyncio

import json
import os

def formatMessage(message):
    channel = message.channel
    author = message.author

    if hasattr(channel, 'name'):
        channel_name= channel.name
    else:
        channel_name = f"DM from {channel.recipient.name}"
    return {
        "recipient":client.user.id,
        "recipient_name":client.user.name,
        "created_at":str(message.created_at),
        "raw_mentions":message.raw_mentions,
        "author_name":author.name,
        "guild":message.guild.id,
        "channel_name": channel_name,
        "content":message.content,
        "author":author.id,
        "channel":channel.id
    }
@client.event
async def on_ready():
    print('ready')
    # These need to be here.
    start_threads()
    await handle_replies()

# class LabelSpace:
#     def __init__(self,) -> None:




@client.event
async def on_message(message):

    formated_message =formatMessage(message)

    # guild,channel,channel_name,author,author_name = itemgetter('guild','channel','channel_name','author','author_name')(formated_message)


    if message.author.id == client.user.id:
        return
    message_collection.insert_one({
        **formated_message
    })




start_discord()
