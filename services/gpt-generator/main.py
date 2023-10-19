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

from shared.mongodb import generated_message_collection
from shared.training_data import collect_samples, encode_sample,get_most_recent_messages, get_messages_for_inference
import shared.settings as settings

model_path="./models/duck_gpt.v0.2.0"


    # Collect all channels first

def generate_frame() -> str:
    # We load this model in to not conflict with anything happening in training.
    # This is the model as of now, training could finish and there is another model available
    prefix_samples=get_messages_for_inference(9)
    prefix="["
    for sample in prefix_samples:
        prefix+=json.dumps(encode_sample(sample), separators=(",",":"))+','
    return prefix


model, model_args, iter_num, best_val_loss, checkpoint, scaler,optimizer=setup_model(
    out_dir=model_path,
    device='cuda',
    init_from="resume" if os.path.exists(model_path) and len(os.listdir(model_path)) > 0 else "gpt2-medium",
)
# try:

started=datetime.datetime.utcnow()
prefix=generate_frame()+'{"channel":'

temp=random.uniform(
    float(settings.MIN_TEMP),
    float(settings.MAX_TEMP)
)
sample= generate_text_from_gpt_model(
    model=model,
    temperature=temp,
    device='cuda',
    start=prefix,
    max_new_tokens=10000,
)[0]
print("sample generated",sample)
finished=datetime.datetime.utcnow()

print("batch complete, saving samples")
sample_data=json.loads(sample)
is_valid=True
print(f"valid sample:{sample}")
generated_message_collection.insert_one({
    "sample_text":sample,
    "temp":temp,
    "started":started,
    "finished":finished,
    "model":model_path,
    "is_valid":is_valid,
    "sent":False
})
