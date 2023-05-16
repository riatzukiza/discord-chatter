"""It is where we define the model stuff"""
from shared.textgenrnn.textgenrnn import textgenrnn
from shared.mongodb import discord_message_collection

import shared.settings as settings

import json

model=textgenrnn(
    settings.MODEL_PATH,name=settings.MODEL_NAME,
    train_size=settings.TEXTGEN_TRAIN_SIZE,
    batch_size=settings.TEXTGEN_BATCH_SIZE,
    num_epochs=settings.TEXTGEN_NUM_EPOCHS,
    base_lr=settings.TEXTGEN_BASE_LR,
    verbose=settings.TEXTGEN_VERBOSE,
    gen_epochs=settings.TEXTGEN_GEN_EPOCHS,
    dropout=settings.TEXTGEN_DROPOUT,
    allow_growth=True,
    config={
        'rnn_layers': settings.TEXTGEN_RNN_LAYERS,
        'rnn_size': settings.TEXTGEN_RNN_SIZE,
        'rnn_bidirectional': settings.TEXTGEN_RNN_BIDIRECTIONAL,
        'max_length': settings.TEXTGEN_MAX_LENGTH,
        'max_words': settings.TEXTGEN_MAX_WORDS,
        'dim_embeddings': settings.TEXTGEN_DIM_EMBEDDINGS,
        'word_level': settings.TEXTGEN_WORD_LEVEL,
        'single_text': settings.TEXTGEN_SINGLE_TEXT
    })
def extract_hashtags_from_string(string):
    return [hashtag.lower() for hashtag in string.split() if hashtag.startswith("#")]

def remove_hashtag_from_string(string):
    return " ".join(word for word in string.split() if not word.startswith("#"))

def extract_mentions_from_string(string):
    return [mention.lower() for mention in string.split() if mention.startswith("@")]

def remove_mention_from_string(string):
    return " ".join(word for word in string.split() if not word.startswith("@"))

def extract_urls_from_string(string):
    return [url.lower() for url in string.split() if url.startswith("http")]

def remove_url_from_string(string):
    return " ".join(word for word in string.split() if not word.startswith("http"))

# def extract_parts_of_speech(string):
#     """
#     Tokenize and extract part of speech using NLTK library
#     """
#     from nltk import word_tokenize, pos_tag
#     return pos_tag(word_tokenize(string))

def encode_sample(message, channels, channel_names):
    return {
        "recipient":message['recipient'],
        "channel":message['channel'],
        "channel_name": message['channel_name'],
        "content":remove_hashtag_from_string(
            remove_mention_from_string(
                remove_url_from_string(
                    message['content']
                )
            )
        )
    }

def get_messages_for_training():
    results = discord_message_collection.aggregate([
        { "$match": { "recipient":settings.DISCORD_CLIENT_USER_ID,
                        "author":{"$nin":[settings.DISCORD_CLIENT_USER_ID]}
                     } },
        {"$sample":{"size":1000}},
    ], allowDiskUse=True)
    # Collect all channels first
    channels = []
    channel_names = []
    messages=[]
    training_data=[]
    for result in results:
        messages.append(result)
        if result["channel"] not in channels:
            channels.append(result["channel"])
            channel_names.append(result["channel_name"])


    for message in messages:
        training_data.append(json.dumps(
            encode_sample(message, channels, channel_names) , separators=(",",":")))
    return training_data

while True:
    print(settings.TEXTGEN_BATCH_SIZE)
    try:
        messages=get_messages_for_training()
        if messages:
            model.train_on_texts(
                texts=messages,
            )
        else:
            print("no messages to train on")
            continue
    except Exception as e:
        print("An error was caught and this is what happened:")
        __import__('traceback').print_exc()
        print("The process will try again")
