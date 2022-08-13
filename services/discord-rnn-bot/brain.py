"""It is where we define the model stuff"""
from textgenrnn.textgenrnn import textgenrnn
from .data import messages, labels, replies
from .main import client
# from .model import load_model, save_model

import json
import os
import time
import random
MODEL_PATH=os.environ['MODEL_PATH']
model=textgenrnn(MODEL_PATH,name=os.environ['MODEL_NAME'])

def get_messages_for_training():

    from bot_src.database import get_database
    db=get_database()
    message_collection=db[f'discord_messages']
    results = message_collection.find({
        "recipient":client.user.id,
        "recipient_name":client.user.name
    })
    training_data=[]
    for message in results:
        training_data.append({
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
        })
    return training_data



# This is for training on
def save_message_strings(m):
    message_json = json.dumps(m , separators=(",",":"))
    messages.append(message_json)

def generate():
    # We load this model in to not conflict with anything happening in training.
    # This is the model as of now, training could finish and there is another model available
    temp=random.uniform(float(os.environ['MIN_TEMP']),float(os.environ['MAX_TEMP']))
    string=model.generate(
        max_gen_length=4096,
        progress=False,
        n=1,prefix='{"',temperature=temp,return_as_list=True)[0]
    print(f"generated a new string with temp of {temp}: {string}")

    return string

def speak():
    while True:
        try:

            reply = generate()

            replies.append(reply)
        except Exception as e:
            # __import__('traceback').print_exc()
            pass

def train():
    try:

        if messages.data:
            epochs=int(os.environ.get('TRAINING_EPOCHS',5))
            print(f'Epochs:{epochs}')
            print("training on data")


            model.train_on_texts(
                new_model=True,
                via_new_model=True,
                texts=get_messages_for_training(),
                train_size=0.8,
                dropout=0.1,
                batch_size=int(os.environ.get('BATCH_SIZE',128)),
                num_epochs=epochs,
                base_lr=float(os.environ.get('BASE_LEARNING_RATE',0.1)),
                verbose=2,
                gen_epochs=1)
            model.save(MODEL_PATH)

    except Exception as e:
        print("An error was caught and this is what happened:")
        __import__('traceback').print_exc()
        print("The process will try again")
        pass

def _ml():
    while True:
        train()

