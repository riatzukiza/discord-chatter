"""This service creates messages from the model and saves them in mongodb
"""
from shared.nano_gpt.generator import generate_text_from_gpt_model
from shared.nano_gpt.trainer import setup_model,encode_document

import torch
from shared.mongodb import discord_message_collection


import os
import re
import random
import json
import datetime

from shared.mongodb import generated_message_collection, duck_gpt
from shared.training_data import collect_messages, encode_message,get_most_recent_messages, get_messages_for_inference
import shared.settings as settings

service_started=datetime.datetime.utcnow()
model_loaded=datetime.datetime.utcnow()

def get_frame(): return encode_message(duck_gpt.find_one())
def dir_is_not_empty(path): return os.path.exists(path) and len(os.listdir(path)) > 0

def generate_frame(message_size) -> str:
    # We load this model in to not conflict with anything happening in training.
    # This is the model as of now, training could finish and there is another model available
    prefix_messages=get_messages_for_inference(message_size)
    prefix="["
    for message in prefix_messages:
        prefix+=json.dumps(encode_message(message), separators=(",",":"))+','
    return prefix


# try:


while True:
    print("loading", settings.model_path)
    model, model_args, iter_num, best_val_loss, checkpoint, scaler,optimizer=setup_model(
        out_dir=settings.model_path,
        device='cuda',
        init_from="resume" if dir_is_not_empty(settings.model_path) else "gpt2-medium",
    )
    started=datetime.datetime.utcnow()
    message_size=random.randint(5,100)
    prefix=generate_frame(message_size=message_size)+'{"channel":'

    temp=random.uniform(
        float(settings.MIN_TEMP),
        float(settings.MAX_TEMP)
    )
    message= generate_text_from_gpt_model(
        model=model,
        seed=random.randint(0,99999999),
        temperature=temp,
        device='cuda',
        start=prefix,
        max_new_tokens=10000,
    )[0]
    print("message generated",message)
    finished=datetime.datetime.utcnow()

    print("batch complete, saving messages")
    message_data=json.loads(message)

    print(f"generated {len(message_data)} messages")
    generated_messages=message_data[message_size:]

    print(generated_messages)
    is_valid=True
    model=None
    torch.cuda.empty_cache()

    print(f"valid message:{message}")
    generated_message_collection.insert_one({
        "message_text":json.dumps(generated_messages),
        "temp":temp,
        "started":started,
        "finished":finished,
        "model":settings.model_path,
        "is_valid":is_valid,
        "sent":False
    })
