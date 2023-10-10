"""This service creates messages from the model and saves them in mongodb
"""
from shared.textgenrnn.textgenrnn import textgenrnn
from shared.mongodb import discord_message_collection

import os
import random
import json
import datetime

from shared.mongodb import generated_message_collection
import shared.settings as settings

def extract_hashtags_from_string(string):
    return [hashtag.lower() for hashtag in string.split() if hashtag.startswith("#")]

def remove_hashtag_from_string(string):
    return " ".join(word for word in string.split() if not word.startswith("#"))

def extract_mentions_from_string(string):
    return [mention.lower() for mention in string.split() if mention.startswith("@")]

def remove_mention_from_string(string):
    return " ".join(word for word in string.split() if not word.startswith("@"))

def extract_urls_from_string(string):
    return [url.lower() for url in string.split() if url.startswith("http")]

def remove_url_from_string(string):
    return " ".join(word for word in string.split() if not word.startswith("http"))

def encode_sample(message):
    return {
        "recipient":message['recipient'],
        "channel":message['channel'],
        "channel_name": message['channel_name'],
        "content":remove_hashtag_from_string(
            remove_mention_from_string(
                remove_url_from_string(
                    message['content']
                )
            )
        )
    }

def collect_samples(size=10):
    return discord_message_collection.aggregate([
        { "$match": { "recipient":settings.DISCORD_CLIENT_USER_ID} },
        {"$sample":{"size":size}},
    ], allowDiskUse=True)
    # Collect all channels first

def generate_batch(temp) -> str:
    # We load this model in to not conflict with anything happening in training.
    # This is the model as of now, training could finish and there is another model available
    model=textgenrnn(
        settings.MODEL_PATH,
        name=settings.MODEL_NAME,
        max_gen_length=settings.MAX_GENERATED_LENGTH,
        config={
            'rnn_layers': settings.TEXTGEN_RNN_LAYERS,
            'rnn_size': settings.TEXTGEN_RNN_SIZE,
            'rnn_bidirectional': settings.TEXTGEN_RNN_BIDIRECTIONAL,
            'max_length': settings.TEXTGEN_MAX_LENGTH,
            'max_words': settings.TEXTGEN_MAX_WORDS,
            'dim_embeddings': settings.TEXTGEN_DIM_EMBEDDINGS,
            'word_level': settings.TEXTGEN_WORD_LEVEL,
            'single_text': settings.TEXTGEN_SINGLE_TEXT
        }
    )
    prefix_samples=collect_samples(9)
    prefix="["
    for sample in prefix_samples:
        print("accumulating frame prefix",sample)
        prefix+=json.dumps(encode_sample(sample), separators=(",",":"))+','

    return model.generate(
        progress=False,
        n=1,
        prefix=prefix,
        # Give it a head start and let it know we mean buisness with JSON
        temperature=temp,
        return_as_list=True)[0]

while True:
    print("trying to make a message")
    try:
        temp=random.uniform(
            float(settings.MIN_TEMP),
            float(settings.MAX_TEMP)
        )
        started=datetime.datetime.utcnow()
        sample=generate_batch(temp)
        print("sample generated",sample)
        finished=datetime.datetime.utcnow()
    except Exception as e:
        print("failed")
        print(e)
        continue
    try:
        print("batch complete, saving samples")
        print("temp",temp)
        sample_data=json.loads(sample)
        is_valid=True
        print(f"valid sample:{sample}")
    except Exception as e:
        sample_data={}
        print(f"invalid sample:{sample}")
        is_valid=False
    generated_message_collection.insert_one({
        "sample_text":sample,
        "temp":temp,
        "started":started,
        "finished":finished,
        "model":settings.MODEL_NAME,
        "is_valid":is_valid,
        "sent":False,
        "train_size" :settings.TEXTGEN_TRAIN_SIZE,
        "dropout":settings.TEXTGEN_DROPOUT,
        "batch_size":settings.TEXTGEN_BATCH_SIZE,
        "num_epochs":settings.TEXTGEN_NUM_EPOCHS,
        "base_lr":settings.TEXTGEN_BASE_LR,
    })
