from textgenrnn.textgenrnn import textgenrnn
import os

MODEL_PATH=os.environ['MODEL_PATH']

def load_model():
    model = textgenrnn(MODEL_PATH, name=os.environ['MODEL_NAME'])
    model.config['base_lr'] = os.environ.get('BASE_LEARNING_RATE', 4e-3)
    return model

textgen = load_model()
def save_model(): textgen.save(MODEL_PATH)

