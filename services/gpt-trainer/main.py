"""It is where we define the model stuff"""
from shared.textgenrnn.textgenrnn import textgenrnn
from shared.mongodb import discord_message_collection

import shared.settings as settings

import json
import os

from tqdm import tqdm
import numpy as np
import tiktoken

from shared.mongodb import discord_message_collection
import shared.settings as settings

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

def encode_sample(message):
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

def get_messages_for_training(frames=1000):
    training_data=[]
    for _ in range(frames):
        frame=[]
        messages=collect_samples()
        for message in messages: frame.append(encode_sample(message))
        training_data.append(json.dumps(frame, separators=(",",":")))
    return training_data

def collect_samples(size=10):
    return discord_message_collection.aggregate([
        { "$match": { "recipient":settings.DISCORD_CLIENT_USER_ID} },
        {"$sample":{"size":size}},
    ], allowDiskUse=True)

if __name__ == '__main__':


    # we now want to tokenize the dataset. first define the encoding function (gpt2 bpe)
    enc = tiktoken.get_encoding("gpt2")
    samples=collect_samples(1000)
    def process(example):
        ids = enc.encode_ordinary(example['text']) # encode_ordinary ignores any special tokens
        ids.append(enc.eot_token) # add the end of text token, e.g. 50256 for gpt2 bpe
        # note: I think eot should be prepended not appended... hmm. it's called "eot" though...
        out = {'ids': ids, 'len': len(ids)}
        return out

    train_samples = samples[:int(n*0.9)]
    val_samples = samples[int(n*0.9):]

    # concatenate all the ids in each dataset into one large file we can use for training
    for split, dset in tokenized.items():
        arr_len = np.sum(dset['len'], dtype=np.uint64)
        filename = os.path.join(os.path.dirname(__file__), f'{split}.bin')
        dtype = np.uint16 # (can do since enc.max_token_value == 50256 is < 2**16)
        arr = np.memmap(filename, dtype=dtype, mode='w+', shape=(arr_len,))
        total_batches = 1024

        idx = 0
        for batch_idx in tqdm(range(total_batches), desc=f'writing {filename}'):
            # Batch together samples for faster write
            batch = dset.shard(num_shards=total_batches, index=batch_idx, contiguous=True).with_format('numpy')
            arr_batch = np.concatenate(batch['ids'])
            # Write into mmap
            arr[idx : idx + len(arr_batch)] = arr_batch
            idx += len(arr_batch)
        arr.flush()

    # train.bin is ~17GB, val.bin ~8.5MB
    # train has ~9B tokens (9,035,582,198)
    # val has ~4M tokens (4,434,897)

    # to read the bin files later, e.g. with numpy:
    # m = np.memmap('train.bin', dtype=np.uint16, mode='r')
