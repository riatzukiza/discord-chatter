from .replies import start_discord, client, handle_replies

from .threads import start_threads

from operator import itemgetter

from .database import get_database

from  discord.ext.commands import Bot
import json
import os
import asyncio


client = Bot(command_prefix=f"./{os.environ['MODEL_NAME']}")


### Reply handler##############
async def handle_recent_replies():
    try:
        while replies.data:
            reply_value = replies.pop(0,save=True)

            if isinstance(reply_value,str):
                reply = json.loads(reply_value)
            else:
                reply = reply_value

            try:
                channel = await client.fetch_channel(int(reply["channel"]))
            except:
                channel = await client.fetch_channel(int(os.environ["DEFAULT_CHANNEL"]))

            if channel is None:
                channel = await client.fetch_channel(int(os.environ["DEFAULT_CHANNEL"]))
                print(channel)

            if channel is not None and reply['content']:
                print(f"sending {reply['content']}")
                await channel.send(reply["content"])
            else:
                print("default channel not working?")
    except:
        # print("ops")
        # __import__('traceback').print_exc()
        pass

async def handle_replies():
    while True:
        await asyncio.sleep(5)
        await handle_recent_replies()

def start_discord():
    client.run(os.environ['DISCORD_TOKEN'])


import asyncio

import json
import os

