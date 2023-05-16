"""This service creates messages from the model and saves them in mongodb
"""
from shared.textgenrnn.textgenrnn import textgenrnn

import os
import random
import json
import datetime

from shared.mongodb import generated_message_collection
import shared.settings as settings



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
    first_pass=json.loads(model.generate(
        progress=False,
        n=1,
        prefix='{"recipient":"'+str(settings.DISCORD_CLIENT_USER_ID),
        # Give it a head start and let it know we mean buisness with JSON
        temperature=temp,
        return_as_list=True)[0])
    return model.generate(
        progress=False,
        n=1,
        prefix='{"recipient":"'+str(settings.DISCORD_CLIENT_USER_ID)+',"channel":'+str(first_pass['channel'])+',"channel_name":"'+first_pass['channel_name']+'",',
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
