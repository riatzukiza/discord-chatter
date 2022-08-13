"""This service creates messages from the model and saves them in mongodb
"""
from shared.textgenrnn.textgenrnn import textgenrnn

import os
import random
import json
import datetime

from shared.mongodb import generated_message_collection
import shared.settings as settings



def generate_batch(temp):
    # We load this model in to not conflict with anything happening in training.
    # This is the model as of now, training could finish and there is another model available
    model=textgenrnn(settings.MODEL_PATH,name=settings.MODEL_NAME)
    return model.generate(
        max_gen_length=settings.MAX_GENERATED_LENGTH,
        progress=False,
        n=settings.EXAMPLES_GENERATED_PER_BATCH,
        prefix='{"',# Give it a head start and let it know we mean buisness with JSON
        temperature=temp,
        return_as_list=True)

while True:

    temp=random.uniform(
        float(settings.MIN_TEMP),
        float(settings.MAX_TEMP)
    )
    started=datetime.datetime.utcnow()
    batch=generate_batch(temp)
    finished=datetime.datetime.utcnow()
    # print("batch complete",batch)

    for sample in batch:
        try:
            sample_data=json.loads(sample),
            is_valid=True
        except Exception as e:
            sample_data=None
            is_valid=False
        generated_message_collection.insert_one({
            "sample_text":sample,
            "sample_data":sample_data,
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
