import discord
import json
import os
import asyncio
from .data import replies


client = discord.Client()


### Reply handler##############
async def handle_recent_replies():
    while replies:
        reply = replies.pop(0)
        # with open(os.environ['REPLIES_JSON'],'w') as f:
        #     json.dump(replies,f)
        
        print("hanldling reply")
        print(reply)

        channel = client.get_channel(str(reply["channel"]))
        print(reply["channel"])
        print(channel)
        # text_channel_list = []
        # for guild in client.guilds:
        #     for channel in guild.text_channels:
        #         text_channel_list.append(channel.name)
        # print(text_channel_list)

        if channel is None:
            print("this bot tried to send to a channel it can't see")
            print(os.environ["DEFAULT_CHANNEL"])
            channel = client.get_channel(str(os.environ["DEFAULT_CHANNEL"]))
            print(channel)

        if channel is not None:
            await channel.send(reply["content"])

async def handle_replies():
    while True:
        await asyncio.sleep(5)
        await handle_recent_replies()

def start_discord():
    client.run(os.environ['DISCORD_TOKEN'])
