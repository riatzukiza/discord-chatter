from textgenrnn.textgenrnn import textgenrnn
from data import messages, replies, incomeing
import os

MODEL_PATH=os.environ['MODEL_PATH']

def load_model():
    return textgenrnn(MODEL_PATH)

def save_model():
    textgen.save(MODEL_PATH)

def save_message_strings(m):
    message_json = json.dumps(m , sort_keys=True, separators=(",",":"))
    messages.append(message_json)

def generate():
    textgen = load_model()
    return textgen.generate(
        progress=False,
        n=1,prefix="",temperature=random.uniform(float(os.environ['MIN_TEMP']),float(os.environ['MAX_TEMP'])),return_as_list=True)[0]

def speak():
    while True:
        txt = generate()
        reply = json.loads(txt)
        replies.append(reply)
        with open('replies.json','w') as f:
            json.dump(replies,f)


def train(d,e,sample_size=0):
    textgen.train_on_texts(d, None, int(os.environ['BATCH_SIZE']), e,gen_epochs=int(os.environ['GEN_EPOCHS']),)
    save_model()


def trim_message_list(messages):
    if len(messages) > int(os.environ['MAX_MESSAGES']):
        return messages.pop(0)

def think(m):
    try:
        log(m)
        save_message_strings(m)
        # trim_message_list()

        with open('messages.json','w') as f:
            json.dump(messages,f)

        train(messages, int(os.environ['EPOCHS_PER_MESSAGE']))
    except Exception as e:

        __import__('traceback').print_exc()

def _ml():
    while True:
        if incomeing:
            log("bout to think about this...")
            think(incomeing.pop(0))
