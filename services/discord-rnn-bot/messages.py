from .replies import start_discord, client, handle_replies

from .threads import start_threads

from operator import itemgetter

from .database import get_database

from  discord.ext.commands import Bot
import json
import os
import asyncio
import asyncio

import json
import os

db=get_database()

message_collection=db[f'discord_messages']

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
    print ('threads started')

@client.event
async def on_message(message):
    formated_message =formatMessage(message)
    if message.author.id == client.user.id:
        return
    message_collection.insert_one({
        **formated_message
    })




start_discord()
