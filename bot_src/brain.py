from textgenrnn.textgenrnn import textgenrnn
from .data import messages, labels, replies
# from .model import load_model, save_model

import json
import os
import time
import random
MODEL_PATH=os.environ['MODEL_PATH']
model=textgenrnn(MODEL_PATH,name=os.environ['MODEL_NAME'])

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
    if messages.data:
        epochs=int(os.environ.get('TRAINING_EPOCHS',5))
        print(f'Epochs:{epochs}')
        print("training on data")
        model.train_on_texts(
            # new_model=True,
            # via_new_model=True,
            texts=messages.data,
            # context_labels=labels.data,
            batch_size=int(os.environ.get('BATCH_SIZE',128)),
            num_epochs=epochs,
            base_lr=float(os.environ.get('BASE_LEARNING_RATE',0.1)),
            verbose=2,
            gen_epochs=1
            )
        model.save(MODEL_PATH)

def _ml():
    while True:
        train()

