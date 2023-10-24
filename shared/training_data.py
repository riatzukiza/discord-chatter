from shared.mongodb import discord_message_collection, duck_gpt
import pymongo
import shared.settings as settings
import os

import json
import re

discord_message_collection.create_index([("id",pymongo.ASCENDING)])

def encode_sample(message):
    return {
        "channel":message['channel'],
        "channel_name": message['channel_name'],
        "author_name":message['author_name'],
        "content":re.sub( "(?:http[s]*\S+|[@#]\w+)(?:\s+|\s*)", '', message['content'] )
    }

def collect_samples(size=100):
    return discord_message_collection.aggregate([
        { "$match": { "recipient":settings.DISCORD_CLIENT_USER_ID,
                        "author":{"$nin":[settings.DISCORD_CLIENT_USER_ID]}
                     } },
        {"$sample":{"size":size}},
    ])

def collect_samples_from_pointer(size=100, current_message_id=0):
    return discord_message_collection.aggregate([
        { "$match": { "recipient":settings.DISCORD_CLIENT_USER_ID,
                      "id":{"$gte": current_message_id},
                      "channel_name":{"$not":{"$regex":re.compile("hemp|bot|spam|playground|brain|training|twitter")}},
                      "author_name":{"$nin":[settings.DISCORD_CLIENT_USER_NAME,"mr thing", "Jim","Hivemind","Timmy"]}
                     } },
        {"$sort":{"id":pymongo.ASCENDING}},
        {"$limit":size}
    ])
    # Collect all channels first



def get_most_recent_messages(count):
    return discord_message_collection.aggregate([
        {"$sort":{"id":pymongo.DESCENDING}},
        { "$match": { "recipient":settings.DISCORD_CLIENT_USER_ID,
                      "author_name":{"$nin":[settings.DISCORD_CLIENT_USER_NAME,"mr thing", "Jim","Hivemind","Timmy"]},
                      "channel_name":{"$not":{"$regex":re.compile("hemp")}},
                     } },
        {"$limit":count},
        {"$sort":{"id":pymongo.ASCENDING}},
    ])

def get_messages_for_inference(count):
    return list(map(encode_sample,get_most_recent_messages(count)))

def get_messages_for_training(frames=1000, size=100):
    training_data=[]
    for _ in range(frames):
        frame=list(map(encode_sample,collect_samples(size)))
        training_data.append(json.dumps(frame, separators=(",",":")))
    return training_data

def get_messages_for_in_order_training(frames, size,training_pointer_file='training_pointer.json'):
    current_message_id=json.load(open(training_pointer_file)).get('id',0) if os.path.exists(training_pointer_file) else 0
    training_data=[]
    for _ in range(frames):
        docs=list(collect_samples_from_pointer(size,current_message_id=current_message_id))
        current_message=(docs[-1] if len(docs) > 0 else latest_message)
        current_message_id=current_message.get('id',current_message_id)

        messages=list(map(encode_sample,docs))
        with open("training_pointer.json",'w') as message_pointer:
            message_pointer.write(json.dumps({'current_id':current_message_id}))

        training_data.append(json.dumps(list(map(encode_sample, messages))))
    return training_data
