from  discord.ext.commands import Bot
import os
from shared.mongodb import discord_message_collection, generated_message_collection

client = Bot(command_prefix=f"ok {os.environ['MODEL_NAME']}")

def start_discord():
    client.run(os.environ['DISCORD_TOKEN'])

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

@client.event
async def on_message(message):
    if message.author.id == client.user.id:
        return
    discord_message_collection.insert_one(formatMessage(message))
    unsent_messages = generated_message_collection.find({"sent":False, "is_valid":True})
    for message in unsent_messages:
        print("sending message")
        channel = await client.fetch_channel(int(message['channel']))
        channel.send(message.content)

# @client.command()
# async def set_read_channel(ctx, channe_name):

start_discord()
