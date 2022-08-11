"""It is where we define the model stuff"""
from shared.textgenrnn.textgenrnn import textgenrnn
from shared.mongodb import discord_message_collection
import shared.settings as settings
from  discord.ext.commands import Bot

import os
import json
client = Bot(command_prefix=f"ok {os.environ['MODEL_NAME']}")

model=textgenrnn(settings.MODEL_PATH,name=settings.MODEL_NAME)


def get_messages_for_training():
    results = discord_message_collection.find({
        "recipient":client.user.id,
        "recipient_name":client.user.name
    })
    training_data=[]
    for message in results:
        training_data.append(json.dumps({
            "recipient":message.recpient,
            "recipient_name":message.recipient_name,
            "created_at":str(message.created_at),
            "raw_mentions":message.raw_mentions,
            "author_name":message.author_name,
            "guild":message.guild,
            "channel_name": message.channel_name,
            "content":message.content,
            "author":message.author,
            "channel":message.channel
        } , separators=(",",":")))
    return training_data

while True:
    try:
        model.train_on_texts(
            texts=get_messages_for_training(),
            train_size=settings.TEXTGEN_TRAIN_SIZE,
            dropout=settings.TEXTGEN_DROPOUT,
            batch_size=settings.TEXTGEN_BATCH_SIZE,
            num_epochs=settings.TEXTGEN_NUM_EPOCHS,
            base_lr=settings.TEXTGEN_BASE_LR,
            verbose=settings.TEXTGEN_VERBOSE,
            gen_epochs=1)

    except Exception as e:
        print("An error was caught and this is what happened:")
        __import__('traceback').print_exc()
        print("The process will try again")
