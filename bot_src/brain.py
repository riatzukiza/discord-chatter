from textgenrnn.textgenrnn import textgenrnn
from .data import messages, replies, incomeing
from .model import load_model, save_model

import json
import os
import time
import random

# This is for training on
model = load_model()
def save_message_strings(m):
    message_json = json.dumps(m , sort_keys=True, separators=(",",":"))
    messages.append(message_json)

def generate():
    # We load this model in to not conflict with anything happening in training.
    # This is the model as of now, training could finish and there is another model available
    model = load_model()
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
            txt = generate()
            reply = json.loads(txt)
            replies.append(reply)
            with open(os.environ['REPLIES_JSON'], 'w') as f:
                json.dump(replies,f)
        except Exception as e:
            # __import__('traceback').print_exc()
            pass

def train(d,e,sample_size=0):
    model.train_on_texts(d, None, int(os.environ['BATCH_SIZE']), e, verbose=2,
                         gen_epochs=int(os.environ['GEN_EPOCHS']),)
    save_model()

def trim_message_list(messages):
    if len(messages) > int(os.environ['MAX_MESSAGES']):
        return messages[-int(os.environ['MAX_MESSAGES'])]

def think(m):
    save_message_strings(m)
    with open(os.environ['MESSAGES_JSON'],'w') as f:
        json.dump(messages,f)
    train(messages, int(os.environ['EPOCHS_PER_MESSAGE']))

def think_really_hard(incomeing_messages):
    for message in incomeing_messages:
        save_message_strings(message)

    with open(os.environ['MESSAGES_JSON'],'w') as f:
        json.dump(trim_message_list(messages),f)

    train(messages, int(os.environ['EPOCHS_PER_MESSAGE']))

def _ml():
    while True:

        new_training_data=[]
        if incomeing:
            while incomeing:
                new_training_data.append(incomeing.pop(0))
            think_really_hard(incomeing)

