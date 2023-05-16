import os
import asyncio
import discord
import json

from shared.mongodb import discord_message_collection, generated_message_collection
from shared.images import base_64_decode_bitmap

import shared.settings as settings
intents = discord.Intents.default()
client = discord.Client(intents=intents)


def start_discord():
    client.run(settings.DISCORD_TOKEN)


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

# @client.event
# async def on_message(message):
#     if message.author.id == client.user.id:
#         return
#     message_data = formatMessage(message)
#     print(message_data)
    # discord_message_collection.insert_one(message_data)

def decode_attachments(attachments):
    return [discord.File(base_64_decode_bitmap(attachment),"image.png") for attachment in attachments]

async def handle_generated_messages():
    unsent_messages = generated_message_collection.find({"sent":False, "is_valid":True})
    for message in unsent_messages:
        print(f"sending message: {message['sample_text']}")

        try:
            sample_data=json.loads(message['sample_text'])
            print(sample_data)
            try:
                channel = await client.fetch_channel(int(sample_data['channel']))
            except Exception as e:
                channel = await client.fetch_channel(int(settings.DEFAULT_CHANNEL))

            print(channel.name)

            generated_message_collection.update_one({"_id":message['_id']},{"$set":{"sent":True}})
            attachments=decode_attachments(sample_data.get('attachments',[]))
            await channel.send(sample_data['content'], files=attachments)
        except Exception as e:
            print(e)
            generated_message_collection.update_one({"_id":message['_id']},{"$set":{"is_valid":False,"sent":False}})
            print(f"failed to send message: {message['sample_text']}")
            continue
start_discord()
