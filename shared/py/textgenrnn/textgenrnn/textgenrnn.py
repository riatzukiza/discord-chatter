import json
import re

import numpy as np
import tensorflow as tf
import tqdm
from pkg_resources import resource_filename
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import LabelBinarizer
from tensorflow import config as config
from tensorflow.compat.v1.keras.backend import set_session
from tensorflow.keras.callbacks import LearningRateScheduler
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.preprocessing.text import Tokenizer, text_to_word_sequence
from tensorflow import keras

from .model import textgenrnn_model
from .model_training import generate_sequences_from_texts
from .utils import (
    generate_after_epoch,
    save_model_weights,
    textgenrnn_encode_sequence,
    textgenrnn_generate,
    LossHistory
)


class textgenrnn:
    META_TOKEN = '<s>'
    config = {
        'rnn_layers': 2,
        'rnn_size': 128,
        'rnn_bidirectional': False,
        'max_length': 40,
        'max_words': 10000,
        'dim_embeddings': 100,
        'word_level': False,
        'single_text': False
    }
    default_config = config.copy()

    def __init__(self,
                 weights_path=None,
                 vocab_path=None,
                 train_size=0.8,
                 batch_size=32 ,
                 base_lr=0.001,
                 verbose=0,
                 gen_epochs=10,
                 num_epochs=10,
                 max_gen_length=300,
                 dropout=0.0,
                 config=None,
                 save_epochs=1,
                 validation=True,
                 name="textgenrnn",
                 allow_growth=None):

        self.gen_val = None
        self.val_steps = None
        self.validation = validation
        self.save_epochs = save_epochs
        self.max_gen_length = max_gen_length
        self.train_size = train_size
        self.batch_size = batch_size
        self.base_lr = base_lr
        self.verbose = verbose
        self.gen_epochs = gen_epochs
        self.num_epochs = num_epochs
        self.dropout = dropout
        self.loss_history = LossHistory()
        self.allow_growth = allow_growth

        if weights_path is None: weights_path = resource_filename(__name__, 'textgenrnn_weights.hdf5')
        self.weights_path = weights_path

        if vocab_path is None: self.vocab_path = resource_filename(__name__, 'textgenrnn_vocab.json')
        print(f"vocab path {self.vocab_path}")

        if self.allow_growth is not None:
            c = tf.compat.v1.ConfigProto()
            c.gpu_options.allow_growth = True
            set_session(tf.compat.v1.Session(config=c))

        if config is not None: self.config = config

        self.config.update({'name': name})
        self.default_config.update({'name': name})

        with open(self.vocab_path, 'r', encoding='utf8', errors='ignore') as json_file:
            self.vocab = json.load(json_file)

        self.tokenizer = Tokenizer(filters='', lower=False, char_level=True)
        self.tokenizer.word_index = self.vocab
        self.num_classes = len(self.vocab) + 1

        self.model = textgenrnn_model(
            self.num_classes,
            cfg=self.config,
            dropout=self.dropout,
            weights_path=self.weights_path
        )
        self.indices_char = dict((self.vocab[c], c) for c in self.vocab)

    def generate(self, n=1, return_as_list=False, prefix='', temperature=[1.0, 0.5, 0.2, 0.2], progress=True):
        gen_texts = []
        iterable = tqdm.trange(n) if progress and n > 1 else range(n)
        for _ in iterable:
            gen_text, _ = textgenrnn_generate(
                self.model,
                self.vocab,
                self.indices_char,
                temperature,
                self.config['max_length'],
                self.META_TOKEN,
                self.max_gen_length,
                prefix)
            if not return_as_list:
                print("{}\n".format(gen_text))
            gen_texts.append(gen_text)
        if return_as_list:
            return gen_texts

    def generate_samples(self, n=3, temperatures=[0.2, 0.5, 1.0], **kwargs):
        for temperature in temperatures:
            print('#'*20 + '\nTemperature: {}\n'.format(temperature) +
                  '#'*20)
            self.generate(n, temperature=temperature, progress=False, **kwargs)

    def generate_indicies_list(self,texts):

        # calculate all combinations of text indices + token indices
        self.indices_list = [np.meshgrid(np.array(i), np.arange(len(text) + 1)) for i, text in enumerate(texts)]
        # self.indices_list = np.block(self.indices_list) # this hangs when indices_list is large enough
        self.indices_list_o = np.block(self.indices_list[0])
        for i in range(len(self.indices_list)-1):
            tmp = np.block(self.indices_list[i+1])
            self.indices_list_o = np.concatenate([self.indices_list_o, tmp])
        self.indices_list = self.indices_list_o


        indices_mask = np.random.rand(self.indices_list.shape[0]) < self.train_size
        self.indices_list = self.indices_list[indices_mask, :]

        self.num_tokens = self.indices_list.shape[0]
        assert self.num_tokens >= self.batch_size, "Fewer tokens than batch_size."

        print("Training on {:,} {} sequences.".format(self.num_tokens, "Character level"))

        if self.train_size < 1.0 and self.validation:
            indices_mask = np.random.rand(self.indices_list.shape[0]) < self.train_size
            self.indices_list_val = self.indices_list[~indices_mask, :]
            self.val_steps = max(int(np.floor(self.indices_list_val.shape[0] / self.batch_size)), 1)
            self.gen_val = generate_sequences_from_texts(
                texts,
                self.indices_list_val,
                self,
                self.batch_size
            )

    def get_learning_rate(self):
        """
        Learning rate is a function of the history
        """
        if self.loss_history is not None and self.loss_history.loss:
            return min(
                self.loss_history.loss *
                self.base_lr *
                self.loss_history.loss_max *
                self.loss_history.loss_min *
                self.loss_history.val_loss *
                self.loss_history.val_loss_min *
                self.loss_history.val_loss_max,
                self.base_lr
            )
        else:
            return self.base_lr

    def train_on_texts(self, texts):

        self.generate_indicies_list(texts )
        self.model.compile(
            loss='categorical_crossentropy',
            optimizer=Adam(lr=self.base_lr)
        )

        steps_per_epoch = max(int(np.floor(self.num_tokens / self.batch_size)), 1)
        gen = generate_sequences_from_texts(texts, self.indices_list, self, self.batch_size)

        def learn_from_history(epoch): return self.get_learning_rate()

        self.model.fit(
            gen,
            steps_per_epoch=steps_per_epoch,
            epochs=self.num_epochs,
            callbacks=[
                self.loss_history,
                LearningRateScheduler(learn_from_history),
                generate_after_epoch(self, self.gen_epochs, self.max_gen_length),
                save_model_weights(self, self.num_epochs, self.save_epochs)
            ],
            verbose=self.verbose,
            max_queue_size=10,
            validation_data=self.gen_val,
            validation_steps=self.val_steps
        )


    def save(self, weights_path="textgenrnn_weights_saved.hdf5"):
        self.model.save_weights(weights_path)

    def load(self, weights_path):
        self.model = textgenrnn_model(self.num_classes,
                                      cfg=self.config,
                                      weights_path=weights_path)

    def reset(self):
        self.config = self.default_config.copy()
        self.__init__(name=self.config['name'])

    def encode_text_vectors(self, texts, pca_dims=50, tsne_dims=None,
                            tsne_seed=None, return_pca=False,
                            return_tsne=False):

        # if a single text, force it into a list:
        if isinstance(texts, str):
            texts = [texts]

        vector_output = Model(inputs=self.model.input, outputs=self.model.get_layer('attention').output)
        encoded_vectors = []
        maxlen = self.config['max_length']
        for text in texts:
            text_aug = [self.META_TOKEN] + list(text[0:maxlen])
            encoded_text = textgenrnn_encode_sequence(text_aug, self.vocab,
                                                      maxlen)
            encoded_vector = vector_output.predict(encoded_text)
            encoded_vectors.append(encoded_vector)

        encoded_vectors = np.squeeze(np.array(encoded_vectors), axis=1)
        if pca_dims is not None:
            assert len(texts) > 1, "Must use more than 1 text for PCA"
            pca = PCA(pca_dims)
            encoded_vectors = pca.fit_transform(encoded_vectors)

        if tsne_dims is not None:
            tsne = TSNE(tsne_dims, random_state=tsne_seed)
            encoded_vectors = tsne.fit_transform(encoded_vectors)

        return_objects = encoded_vectors
        if return_pca or return_tsne:
            return_objects = [return_objects]
        if return_pca:
            return_objects.append(pca)
        if return_tsne:
            return_objects.append(tsne)

        return return_objects

    def similarity(self, text, texts, use_pca=True):
        text_encoded = self.encode_text_vectors(text, pca_dims=None)
        if use_pca:
            texts_encoded, pca = self.encode_text_vectors(texts,
                                                          return_pca=True)
            text_encoded = pca.transform(text_encoded)
        else:
            texts_encoded = self.encode_text_vectors(texts, pca_dims=None)

        cos_similairity = cosine_similarity(text_encoded, texts_encoded)[0]
        text_sim_pairs = list(zip(texts, cos_similairity))
        text_sim_pairs = sorted(text_sim_pairs, key=lambda x: -x[1])
        return text_sim_pairs
