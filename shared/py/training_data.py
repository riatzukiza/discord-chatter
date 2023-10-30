from shared.mongodb import discord_message_collection, duck_gpt
import pymongo
import shared.settings as settings
import os

import json
import re

discord_message_collection.create_index([("id", pymongo.ASCENDING)])
discord_message_collection.create_index([("id", pymongo.DESCENDING)])

FILTER_DICT = {
    "recipient": settings.DISCORD_CLIENT_USER_ID,
    "author_name": {
        "$nin": [
            settings.DISCORD_CLIENT_USER_NAME,
            "mr thing",
            "Jim",
            "Hivemind",
            "Timmy",
            "MEE6",
        ]
    },
    "channel_name": {
        "$not": {
            "$regex": re.compile("hemp|bot|spam|playground|brain|training|twitter")
        }
    },
}


def aggregate_messages(size, aggrigation_rules=[]):
    return discord_message_collection.aggregate(
        aggrigation_rules
        + [
            {"$limit": size},
        ]
    )


def encode_message(message):
    return {
        "channel": message["channel"],
        "channel_name": message["channel_name"],
        "author_name": message["author_name"],
        # "content":re.sub( "(?:http[s]*\S+|[@#]\w+)(?:\s+|\s*)", '', message['content'] )
        "content": message["content"],
    }


def collect_messages(size=100):
    return aggregate_messages(
        size, [{"$match": FILTER_DICT}, {"$message": {"size": size}}]
    )


def collect_messages_from_pointer(size=100, current_message_id=0):
    return aggregate_messages(
        size,
        [
            {"$match": {"id": {"$gte": current_message_id}}},
            {"$match": FILTER_DICT},
            {"$sort": {"id": pymongo.ASCENDING}},
        ],
    )
    # Collect all channels first


def get_most_recent_messages(count=100):
    return aggregate_messages(
        count,
        [
            {"$sort": {"id": pymongo.DESCENDING}},
            {"$match": FILTER_DICT},
            {"$sort": {"id": pymongo.ASCENDING}},
        ],
    )


def get_messages_for_inference(count):
    return list(map(encode_message, get_most_recent_messages(count)))


def get_messages_for_training(frames=1000, size=100):
    training_data = []
    for _ in range(frames):
        frame = list(map(encode_message, collect_messages(size)))
        training_data.append(json.dumps(frame, separators=(",", ":")))
    return training_data


# def aggrigate_messages(frames=1000, size=100,fn=lambda s:s):
#     data=[]
#     for _ in range(frames):
#         frame=list(map(encode_message,collect_messages(size)))
#         training_data.append(json.dumps(frame, separators=(",",":")))
#     return training_data


def get_json_file(path, default_value):
    return json.load(open(path)) if os.path.exists(path) else default_value


def get_random_frame(size, id_limit):
    list(collect_messages_from_pointer(size, current_message_id=current_message_id))


def get_messages_for_in_order_training(
    frames, size, training_pointer_file="current_message.json"
):
    current_message = get_json_file(training_pointer_file, {"id":0})
    current_message_id = current_message["id"] if current_message is not None else 0

    training_data = []

    for _ in range(frames):
        docs = list(
            collect_messages_from_pointer(size, current_message_id=current_message_id)
        )
        current_message = docs[-1] if len(docs) > 0 else latest_message
        current_message_id = current_message.get("id", current_message_id)

        messages = list(map(encode_message, docs))
        with open("training_pointer.json", "w") as message_pointer:
            message_pointer.write(json.dumps({"current_id": current_message_id}))

        training_data.append(json.dumps(list(map(encode_message, messages))))
    return training_data
