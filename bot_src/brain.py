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
    print(message_json)
    messages.append(message_json)

def generate():
    # We load this model in to not conflict with anything happening in training.
    # This is the model as of now, training could finish and there is another model available
    return model.generate(
        n=1,prefix="",
        temperature=random.uniform(float(os.environ['MIN_TEMP']),float(os.environ['MAX_TEMP'])),return_as_list=True)[0]

def speak():
    while True:
        try:
            txt = generate()
            # print(f"attempting a message:{txt}")
            print(txt)
            reply = json.loads(txt)
            replies.append(reply)
            # with open(os.environ['REPLIES_JSON'], 'w') as f:
            #     json.dump(replies,f)
        except Exception as e:
            __import__('traceback').print_exc()
            pass


def train(d,e,sample_size=0):

    try:
        model.train_on_texts(d, None, int(os.environ['BATCH_SIZE']), e,
                            verbose=2,
                            train_size=0.8,
                            # dropout=0.1,
                            gen_epochs=int(os.environ['GEN_EPOCHS']),)

    except Exception as e:
        # print(f'Failed with {txt}')
        __import__('traceback').print_exc()
        pass
    # save_model()

def trim_message_list(messages):
    if len(messages) > int(os.environ['MAX_MESSAGES']):
        return messages.pop(0)

def think(m):
    try:
        save_message_strings(m)
        # with open(os.environ['MESSAGES_JSON'],'w') as f:
        #     json.dump(messages,f)
        train(messages, int(os.environ['EPOCHS_PER_MESSAGE']))
    except Exception as e:
        __import__('traceback').print_exc()

def _ml():
    while True:
        if incomeing:
            think(incomeing.pop(0))
