from bot_src.main import start_discord, client, handle_replies
from bot_src.threads import start_threads
from bot_src.data import messages, labels
from operator import itemgetter

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

    # print("message recieved")
    # print(formated_message)

    if message.author.id == client.user.id:
        return
    messages.append(json.dumps(formated_message, separators=(",",":")))
    # labels.append(f"{author}.{author_name}.{channel}.{channel_name}.{guild}")

    # messages.append(json.dumps(formated_message, separators=(",",":")))
    # labels.append(f"{author}")

    # messages.append(json.dumps(formated_message, separators=(",",":")))
    # labels.append(f"{channel}")

    # messages.append(json.dumps(formated_message, separators=(",",":")))
    # labels.append(f"{guild}")

    # messages.append(json.dumps(formated_message, separators=(",",":")))
    # labels.append(f"{channel_name}")

    # messages.append(json.dumps(formated_message, separators=(",",":")))
    # labels.append(f"{author_name}")
    messages.save()



start_discord()
