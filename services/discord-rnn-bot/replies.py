import json
import os
import asyncio



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
            # text_channel_list = []
            # for guild in client.guilds:
            #     for channel in guild.text_channels:
            #         text_channel_list.append(channel.name)
            # print(text_channel_list)

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

