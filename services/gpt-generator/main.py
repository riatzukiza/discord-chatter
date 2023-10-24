"""This service creates messages from the model and saves them in mongodb
"""
from shared.nano_gpt.generator import generate_text_from_gpt_model
from shared.nano_gpt.trainer import setup_model,encode_document

from shared.mongodb import discord_message_collection

import os
import re
import random
import json
import datetime

from shared.mongodb import generated_message_collection, duck_gpt
from shared.training_data import collect_samples, encode_sample,get_most_recent_messages, get_messages_for_inference
import shared.settings as settings

service_started=datetime.datetime.utcnow()
model_loaded=datetime.datetime.utcnow()

def get_frame(): return encode_sample(duck_gpt.find_one())
def dir_is_not_empty(path): return os.path.exists(path) and len(os.listdir(path)) > 0

def generate_frame(sample_size) -> str:
    # We load this model in to not conflict with anything happening in training.
    # This is the model as of now, training could finish and there is another model available
    prefix_samples=get_messages_for_inference(sample_size)
    prefix="["
    for sample in prefix_samples:
        prefix+=json.dumps(encode_sample(sample), separators=(",",":"))+','
    return prefix


# try:


while True:
    model, model_args, iter_num, best_val_loss, checkpoint, scaler,optimizer=setup_model(
        out_dir=settings.model_path,
        device='cuda',
        init_from="resume" if dir_is_not_empty(settings.model_path) else "gpt2-medium",
    )
    started=datetime.datetime.utcnow()
    sample_size=random.randint(5,100)
    prefix=generate_frame(sample_size=sample_size)+'{"channel":'

    temp=random.uniform(
        float(settings.MIN_TEMP),
        float(settings.MAX_TEMP)
    )
    sample= generate_text_from_gpt_model(
        model=model,
        seed=random.randint(0,99999999),
        temperature=temp,
        device='cuda',
        start=prefix,
        max_new_tokens=10000,
    )[0]
    print("sample generated",sample)
    finished=datetime.datetime.utcnow()

    print("batch complete, saving samples")
    sample_data=json.loads(sample)
    print(f"generated {len(sample_data)} samples")
    generated_messages=sample_data[sample_size:]
    print(generated_messages)
    is_valid=True
    print(f"valid sample:{sample}")
    generated_message_collection.insert_one({
        "sample_text":json.dumps(generated_messages),
        "temp":temp,
        "started":started,
        "finished":finished,
        "model":settings.model_path,
        "is_valid":is_valid,
        "sent":False
    })
