from tensorflow.keras.optimizers import Adam
from tensorflow.keras.layers import Input, Embedding, Dense, LSTM, Bidirectional
from tensorflow.keras.layers import concatenate, Reshape, SpatialDropout1D
from tensorflow.keras.models import Model
from tensorflow.keras import backend as K
from tensorflow import config as config
from .AttentionWeightedAverage import AttentionWeightedAverage


def textgenrnn_model(num_classes, cfg,
                     weights_path=None,
                     dropout=0.0,
                     optimizer=Adam(lr=4e-3)):
    '''
    Builds the model architecture for textgenrnn and
    loads the specified weights for the model.
    '''

    input = Input(shape=(cfg['max_length'],), name='input')
    embedded = Embedding(num_classes, cfg['dim_embeddings'],
                         input_length=cfg['max_length'],
                         name='embedding')(input)

    if dropout > 0.0:
        embedded = SpatialDropout1D(dropout, name='dropout')(embedded)

    rnn_layer_list = []
    for i in range(cfg['rnn_layers']):
        prev_layer = embedded if i == 0 else rnn_layer_list[-1]
        rnn_layer_list.append(new_rnn(cfg, i+1)(prev_layer))

    seq_concat = concatenate([embedded] + rnn_layer_list, name='rnn_concat')
    attention = AttentionWeightedAverage(name='attention')(seq_concat)
    output = Dense(num_classes, name='output', activation='softmax')(attention)

    model = Model(inputs=[input], outputs=[output])
    try:
        if weights_path is not None:
            model.load_weights(weights_path, by_name=True)
    except:
        pass
    model.compile(loss='categorical_crossentropy', optimizer=optimizer)
    return model


def new_rnn(cfg, layer_num):
    if cfg['rnn_bidirectional']:
        return Bidirectional(LSTM(cfg['rnn_size'],
                                    return_sequences=True,
                                    recurrent_activation='sigmoid'),
                                name='rnn_{}'.format(layer_num))

    return LSTM(cfg['rnn_size'],
                return_sequences=True,
                recurrent_activation='sigmoid',
                name='rnn_{}'.format(layer_num))
