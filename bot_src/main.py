from  discord.ext.commands import Bot
import json
import os
import asyncio
from .data import replies


client = Bot(command_prefix=f"./{os.environ['MODEL_NAME']}")


### Reply handler##############
async def handle_recent_replies():
    try:
        while replies:
            reply = replies.pop(0)
            with open(os.environ['REPLIES_JSON'],'w') as f:
                json.dump(replies,f)
            print("hanldling reply")
            print(reply)

            try:
                channel = await client.fetch_channel(int(reply["channel"]))
            except:
                channel = await client.fetch_channel(int(os.environ["DEFAULT_CHANNEL"]))
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
                channel = await client.fetch_channel(int(os.environ["DEFAULT_CHANNEL"]))
                print(channel)

            if channel is not None and reply['content']:
                print(f"sending {reply['content']}")
                await channel.send(reply["content"])
            else:
                print("default channel not working?")
    except:
        print("ops")
        __import__('traceback').print_exc()
        pass

async def handle_replies():
    while True:
        await asyncio.sleep(5)
        await handle_recent_replies()

def start_discord():
    client.run(os.environ['DISCORD_TOKEN'])
