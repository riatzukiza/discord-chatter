"""It is where we define the model stuff"""
from shared.textgenrnn.textgenrnn import textgenrnn
from shared.mongodb import discord_message_collection
import shared.settings as settings
from  discord.ext.commands import Bot

import os
import json
import time

DISCORD_CLIENT_USER_ID = os.environ.get('DISCORD_CLIENT_USER_ID')
DISCORD_CLIENT_USER_NAME = os.environ.get('DISCORD_CLIENT_USER_NAME')

model=textgenrnn(settings.MODEL_PATH,name=settings.MODEL_NAME)

def get_messages_for_training():
    print("DISCORD_CLIENT_USER_ID:")
    print(DISCORD_CLIENT_USER_ID)
    print("DISCORD_CLIENT_USER_NAME:")
    print(DISCORD_CLIENT_USER_NAME)
    results = discord_message_collection.find({
        "recipient":DISCORD_CLIENT_USER_ID,
    })
    training_data=[]
    for message in results:
        training_data.append(json.dumps({
            "recipient":message['recipient'],
            "recipient_name":message['recipient_name'],
            "created_at":str(message['created_at']),
            "raw_mentions":message['raw_mentions'],
            "author_name":message['author_name'],
            "guild":message['guild'],
            "channel_name": message['channel_name'],
            "content":message['content'],
            "author":message['author'],
            "channel":message['channel']
        } , separators=(",",":")))
    return training_data

while True:
    messages=get_messages_for_training()
    # print("Training data:", messages)
    if not messages:
        time.sleep(10)
        continue
    try:
        model.train_on_texts(
            texts=messages,
            train_size=settings.TEXTGEN_TRAIN_SIZE,
            dropout=settings.TEXTGEN_DROPOUT,
            batch_size=settings.TEXTGEN_BATCH_SIZE,
            num_epochs=settings.TEXTGEN_NUM_EPOCHS,
            base_lr=settings.TEXTGEN_BASE_LR,
            verbose=settings.TEXTGEN_VERBOSE,
            gen_epochs=int(os.environ.get('GEN_EPOCHS',10)))

    except Exception as e:
        print("An error was caught and this is what happened:")
        __import__('traceback').print_exc()
        print("The process will try again")
