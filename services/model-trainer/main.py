"""It is where we define the model stuff"""
from shared.textgenrnn.textgenrnn import textgenrnn
from shared.mongodb import discord_message_collection
import shared.settings as settings
from  discord.ext.commands import Bot

import os
import json
import time

DISCORD_CLIENT_USER_ID = int(os.environ.get('DISCORD_CLIENT_USER_ID',0))
DISCORD_CLIENT_USER_NAME = os.environ.get('DISCORD_CLIENT_USER_NAME')

model=textgenrnn(settings.MODEL_PATH,name=settings.MODEL_NAME,

            dropout=settings.TEXTGEN_DROPOUT,
            config={
                'rnn_layers': settings.TEXTGEN_RNN_LAYERS,
                'rnn_size': settings.TEXTGEN_RNN_SIZE,
                'rnn_bidirectional': settings.TEXTGEN_RNN_BIDIRECTIONAL,
                'max_length': settings.TEXTGEN_MAX_LENGTH,
                'max_words': settings.TEXTGEN_MAX_WORDS,
                'dim_embeddings': settings.TEXTGEN_DIM_EMBEDDINGS,
                'word_level': settings.TEXTGEN_WORD_LEVEL,
                'single_text': settings.TEXTGEN_SINGLE_TEXT
            },
                 )

def get_messages_for_training():
    print("DISCORD_CLIENT_USER_ID:")
    print(DISCORD_CLIENT_USER_ID)
    print("DISCORD_CLIENT_USER_NAME:")
    print(DISCORD_CLIENT_USER_NAME)
    results = discord_message_collection.aggregate([
        { "$match": { "recipient": int(DISCORD_CLIENT_USER_ID) } },
        { "$sample": { "size": 1000 } },
    ])
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
            batch_size=settings.TEXTGEN_BATCH_SIZE,
            num_epochs=settings.TEXTGEN_NUM_EPOCHS,
            base_lr=settings.TEXTGEN_BASE_LR,
            verbose=settings.TEXTGEN_VERBOSE,
            gen_epochs=int(os.environ.get('GEN_EPOCHS',10))
        )

    except Exception as e:
        print("An error was caught and this is what happened:")
        __import__('traceback').print_exc()
        print("The process will try again")
