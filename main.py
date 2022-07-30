from bot_src.main import start_discord, client, handle_replies
from bot_src.threads import start_threads
from bot_src.data import incomeing

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
        "author_name":author.name,
        "channel_name": channel_name,
        "content":message.content,
        "author":author.id,
        "channel":channel.id
    }
@client.event
async def on_ready():
    start_threads()
    await asyncio.sleep(10)
    await handle_replies()

@client.event
async def on_message(message):

    if message.author.id == client.user.id:
        print ("not responding to self.")
        return

    incomeing.append(formatMessage(message))
    with open(os.environ['INCOMEING_JSON'],'w') as f:
        json.dump(incomeing,f)


start_discord()
