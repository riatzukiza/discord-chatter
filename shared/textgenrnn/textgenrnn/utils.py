import csv
import re
from random import shuffle

import numpy as np
from tensorflow.keras import backend as K
from tensorflow.keras.callbacks import Callback
from tensorflow.keras.models import Model
from tensorflow.keras.preprocessing import sequence
from tqdm import trange
from tensorflow import keras


def textgenrnn_sample(preds, temperature, interactive=False, top_n=3):
    '''
    Samples predicted probabilities of the next character to allow
    for the network to show "creativity."
    '''

    preds = np.asarray(preds).astype('float64')

    if temperature is None or temperature == 0.0:
        return np.argmax(preds)

    preds = np.log(preds + K.epsilon()) / temperature
    exp_preds = np.exp(preds)
    preds = exp_preds / np.sum(exp_preds)
    probas = np.random.multinomial(1, preds, 1)

    if not interactive:
        index = np.argmax(probas)

        # prevent function from being able to choose 0 (placeholder)
        # choose 2nd best index from preds
        if index == 0:
            index = np.argsort(preds)[-2]
    else:
        # return list of top N chars/words
        # descending order, based on probability
        index = (-preds).argsort()[:top_n]

    return index


def textgenrnn_generate(model,
                        vocab,
                        indices_char,
                        temperature=0.5,
                        maxlen=40,
                        meta_token='<s>',
                        max_gen_length=300,
                        prefix=''
                        ):
    '''
    Generates and returns a single text.
    '''

    collapse_char = ''
    end = False

    prefix_t = list(prefix)

    text = [meta_token] + prefix_t if prefix else [meta_token]

    if not isinstance(temperature, list):
        temperature = [temperature]

    if len(model.inputs) > 1:
        model = Model(inputs=model.inputs[0], outputs=model.outputs[1])
    while not end and len(text) < max_gen_length:
        encoded_text = textgenrnn_encode_sequence(text[-maxlen:], vocab, maxlen)
        next_temperature = temperature[(len(text) - 1) % len(temperature)]

        # auto-generate text without user intervention
        next_index = textgenrnn_sample(
            model.predict(encoded_text, verbose=0, batch_size=1)[0],
            next_temperature
        )
        next_char = indices_char[next_index]
        text += [next_char]
        if next_char == meta_token or len(text) >= max_gen_length:
            end = True
    text = text[1:]
    if meta_token in text:
        text.remove(meta_token)

    text_joined = collapse_char.join(text)


    return text_joined, end


def textgenrnn_encode_sequence(text, vocab, maxlen):
    '''
    Encodes a text into the corresponding encoding for prediction with
    the model.
    '''

    encoded = np.array([vocab.get(x, 0) for x in text])
    return sequence.pad_sequences([encoded], maxlen=maxlen)

def textgenrnn_encode_cat(chars, vocab):
    '''
    One-hot encodes values at given chars efficiently by preallocating
    a zeros matrix.
    '''

    a = np.float32(np.zeros((len(chars), len(vocab) + 1)))
    rows, cols = zip(*[(i, vocab.get(char, 0))
                       for i, char in enumerate(chars)])
    a[rows, cols] = 1
    return a


def synthesize(textgens, n=1, return_as_list=False, prefix='',
               temperature=[0.5, 0.2, 0.2], max_gen_length=300,
               stop_tokens=[' ', '\n']):
    """Synthesizes texts using an ensemble of input models.
    """

    gen_texts = []
    iterable = range(n) #trange(n,leave=False) if progress and n > 1 else range(n)
    for _ in iterable:
        shuffle(textgens)
        gen_text = prefix
        end = False
        textgen_i = 0
        while not end:
            textgen = textgens[textgen_i % len(textgens)]
            gen_text, end = textgenrnn_generate(
                textgen.model,
                textgen.vocab,
                textgen.indices_char,
                temperature,
                textgen.config['max_length'],
                textgen.META_TOKEN,
                max_gen_length,
                prefix=gen_text
            )

            textgen_i += 1
        if not return_as_list:
            print("{}\n".format(gen_text))
        gen_texts.append(gen_text)
    if return_as_list:
        return gen_texts


def synthesize_to_file(textgens, destination_path, **kwargs):
    texts = synthesize(textgens, return_as_list=True, **kwargs)
    with open(destination_path, 'w') as f:
        for text in texts:
            f.write("{}\n".format(text))


class generate_after_epoch(Callback):
    def __init__(self, textgenrnn, gen_epochs, max_gen_length):
        super().__init__()
        self.textgenrnn = textgenrnn
        self.gen_epochs = gen_epochs
        self.max_gen_length = max_gen_length

    def on_epoch_end(self, epoch, logs={}):
        if self.gen_epochs > 0 and (epoch+1) % self.gen_epochs == 0:
            self.textgenrnn.generate_samples()


class save_model_weights(Callback):
    def __init__(self, textgenrnn, num_epochs, save_epochs):
        super().__init__()
        self.textgenrnn = textgenrnn
        self.weights_name = textgenrnn.config['name']
        self.weights_path = textgenrnn.weights_path
        self.num_epochs = num_epochs
        self.save_epochs = save_epochs

    def on_epoch_end(self, epoch, logs={}):
        if len(self.textgenrnn.model.inputs) > 1:
            self.textgenrnn.model = Model(inputs=self.model.input[0],
                                          outputs=self.model.output[1])
        if self.save_epochs > 0 and (epoch+1) % self.save_epochs == 0 and self.num_epochs != (epoch+1):
            print("Saving Model Weights — Epoch #{}".format(epoch+1))
            self.textgenrnn.model.save_weights(
                "{}_weights_epoch_{}.hdf5".format(self.weights_name, epoch+1))
        else:
            self.textgenrnn.model.save_weights(self.weights_path)

class LossHistory(keras.callbacks.Callback):
    def __init__(self):
        self.loss = None
        self.loss_min = None
        self.loss_max = None

        self.val_loss = None
        self.val_loss_min = None
        self.val_loss_max = None

    def on_train_begin(self, logs={}):
        self.losses = []
        self.losses_min = []

    def on_epoch_end(self, epoch, logs={}):
        self.loss = logs.get('loss')
        self.val_loss = logs.get('val_loss')

        if self.loss_min is not None:
            self.loss_min = min(self.loss_min, self.loss)
        else:
            self.loss_min = self.loss

        if self.loss_max is not None:
            self.loss_max = max(self.loss_max, self.loss)
        else:
            self.loss_max = self.loss

        if self.val_loss_min is not None:
            self.val_loss_min = min(self.val_loss_min, self.val_loss)
        else:
            self.val_loss_min = self.val_loss

        if self.val_loss_max is not None:
            self.val_loss_max = max(self.val_loss_max, self.val_loss)
        else:
            self.val_loss_max = self.val_loss
