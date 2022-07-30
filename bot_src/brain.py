from textgenrnn.textgenrnn import textgenrnn
from .data import messages, replies, incomeing
from .model import load_model, save_model

import json
import os
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
    return model.generate(
        progress=False,
        n=1,prefix="",temperature=random.uniform(float(os.environ['MIN_TEMP']),float(os.environ['MAX_TEMP'])),return_as_list=True)[0]

def speak():
    while True:
        txt = generate()
        reply = json.loads(txt)
        replies.append(reply)
        with open(os.environ['REPLIES_JSON'], 'w') as f:
            json.dump(replies,f)

def train(d,e,sample_size=0):
    model.train_on_texts(d, None, int(os.environ['BATCH_SIZE']), e,

        verbose=0,
                         gen_epochs=int(os.environ['GEN_EPOCHS']),)
    save_model()

def trim_message_list(messages):
    if len(messages) > int(os.environ['MAX_MESSAGES']):
        return messages.pop(0)

def think(m):
    try:
        save_message_strings(m)
        with open(os.environ['MESSAGES_JSON'],'w') as f:
            json.dump(messages,f)
        train(messages, int(os.environ['EPOCHS_PER_MESSAGE']))
    except Exception as e:
        __import__('traceback').print_exc()

def _ml():
    while True:
        if incomeing:
            think(incomeing.pop(0))
