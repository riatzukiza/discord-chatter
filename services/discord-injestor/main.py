import os
import asyncio
import discord

from shared.mongodb import discord_message_collection, generated_message_collection

import shared.settings as settings

client = discord.Client()

DISCORD_CLIENT_USER_ID = os.environ.get('DISCORD_CLIENT_USER_ID')
DISCORD_CLIENT_USER_NAME = os.environ.get('DISCORD_CLIENT_USER_NAME')


def start_discord():
    client.run(settings.DISCORD_TOKEN)

def formatMessage(message):
    channel = message.channel
    author = message.author

    # if DISCORD_CLIENT_USER_ID != client.user.id:
    #     raise Exception("IDs don't match")

    if hasattr(channel, 'name'):
        channel_name= channel.name
    else:
        channel_name = f"DM from {channel.recipient.name}"
    return {
        "recipient":DISCORD_CLIENT_USER_ID,
        "recipient_name":DISCORD_CLIENT_USER_NAME,
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
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    print('ready')

@client.event
async def on_message(message):
    if message.author.id == client.user.id:
        return
    message_data = formatMessage(message)
    # print(message_data)
    discord_message_collection.insert_one(message_data)
    unsent_messages = generated_message_collection.find({"sent":False, "is_valid":True})
    for message in unsent_messages:
        print("sending message")
        channel = await client.fetch_channel(int(message['channel']))
        channel.send(message.content)

start_discord()
