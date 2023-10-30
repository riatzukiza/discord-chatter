import chromadb
import json
import random
from shared.training_data import collect_samples, encode_sample,get_most_recent_messages, get_messages_for_inference
from shared.mongodb import duck_gpt
# setup Chroma in-memory, for easy prototyping. Can add persistence easily!
client = chromadb.PersistentClient(path="./chroma")
duck_gpt.create_index([("timestamp",pymongo.ASCENDING)])

# Create collection. get_collection, get_or_create_collection, delete_collection also available!
collection = client.create_collection("discord-messages")

frame=list(get_messages_for_inference(10))

while True:

    if len(frame) > 30: frame=frame[-30:]

    raw_docs=list(map(lambda m: json.dumps(m),frame))

    related_messages=collection.query(
        query_texts=list(raw_docs),
        n_results=len(frame)
    )

    frame.extend(map(lambda s: json.loads(s),related_messages))
    duck_gpt.insert(frame)


