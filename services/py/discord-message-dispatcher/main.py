import asyncio
from datetime import time
from random import randint
import discord
import json

from shared.mongodb import generated_message_collection

import shared.settings as settings
intents = discord.Intents.default()
client = discord.Client(intents=intents)




# @client.event
# async def on_message(message):
#     if message.author.id == client.user.id:
#         return
#     message_data = formatMessage(message)
#     print(message_data)
    # discord_message_collection.insert_one(message_data)

# def decode_attachments(attachments):
#     return [discord.File(base_64_decode_bitmap(attachment),"image.png") for attachment in attachments]

# {"current_id": 348261730905882624}
async def handle_generated_messages():
    unsent_messages = generated_message_collection.find({"sent":False, "is_valid":True})
    for message in unsent_messages:
        print(f"sending message: {message['sample_text']}")

        try:
            sample_data=json.loads(message['sample_text'])
            for sample in sample_data:
                print(sample)
                try:
                    channel = await client.fetch_channel(int(sample['channel']))
                except Exception as e:
                    print("default channel", int(settings.DEFAULT_CHANNEL))
                    channel = await client.fetch_channel(int(settings.DEFAULT_CHANNEL))

                print(channel.name)

                try:
                    # await asyncio.sleep(randint(1,2))
                    generated_message_collection.update_one({"_id":message['_id']},{"$set":{"sent":True}})
                    await channel.send(sample['content'])
                except Exception as e:
                    print(e)
                    print(f"failed to send message: {sample}")
                    pass
        except Exception as e:
            print(e)
            generated_message_collection.update_one({"_id":message['_id']},{"$set":{"is_valid":False,"sent":False}})
            print(f"failed to send message: {message['sample_text']}")
            continue

@client.event
async def on_ready():
    while True:
        await handle_generated_messages()
        await asyncio.sleep(1)
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    print('ready')
client.run(settings.DISCORD_TOKEN)
