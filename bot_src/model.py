from textgenrnn.textgenrnn import textgenrnn
import os

MODEL_PATH=os.environ['MODEL_PATH']

def load_model(): return textgenrnn(MODEL_PATH, name=os.environ['MODEL_NAME'])

textgen = load_model()
def save_model(): textgen.save(MODEL_PATH)

