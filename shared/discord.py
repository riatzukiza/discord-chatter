"""
A small library for interating with the discord api
"""

import discord
import os
from . import settings

def format_message(message):
    channel = message.channel
    author = message.author

    if hasattr(channel, 'name'):
        channel_name= channel.name
    else:
        channel_name = f"DM from {channel.recipient.name}"
    return {
        "id": message.id,
        "recipient":settings.DISCORD_CLIENT_USER_ID,
        "recipient_name":settings.DISCORD_CLIENT_USER_NAME,
        "created_at":str(message.created_at),
        "raw_mentions":message.raw_mentions,
        "author_name":author.name,
        "guild":message.guild.id,
        "channel_name": channel_name,
        "content":message.content,
        "author":author.id,
        "channel":channel.id
    }



