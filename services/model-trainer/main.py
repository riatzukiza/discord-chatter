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
        "recipient_name":message['recipient_name'],
        "created_at":str(message['created_at']),
        "raw_mentions":message['raw_mentions'],
        "author_name":message['author_name'],
        "guild":message['guild'],
        "hashtags":extract_hashtags_from_string(message['content']),
        "extracted_mentions":extract_mentions_from_string(message['content']),
        "channel_name": message['channel_name'],
        "original_content":message['content'],
        "urls":extract_urls_from_string(message['content']),
        "content":remove_hashtag_from_string(
            remove_mention_from_string(
                remove_url_from_string(
                    message['content']
                )
            )
        ),
        # "parts_of_speech":extract_parts_of_speech(message['content']),
        # "attachments":message.get('attachments',[]),
        "author":message['author'],
        # "channels":channels,
        # "channel_names":channel_names,
        "channel":message['channel']
    }

def get_messages_for_training():
    results = discord_message_collection.aggregate([
        { "$match": { "recipient":settings.DISCORD_CLIENT_USER_ID,
                        "author":{"$nin":[settings.DISCORD_CLIENT_USER_ID]}
                     } },
        {"$sample":{"size":100}},
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
#     print("getting training data")
#     channels=discord_channel_collection.find({})
    try:
#         for channel in channels:
#             print("training channel",channel)
        messages=get_messages_for_training()
        print(messages)
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
