import chromadb
import json
from shared.training_data import collect_samples_from_pointer, encode_sample
# setup Chroma in-memory, for easy prototyping. Can add persistence easily!
client = chromadb.PersistentClient(path="./chroma")

# Create collection. get_collection, get_or_create_collection, delete_collection also available!
collection = client.create_collection("discord-messages")


def get_messages_for_indexing(size,training_pointer_file='embedding_pointer.json'):
    current_message_id=json.load(open(training_pointer_file)).get('id',0) if os.path.exists(training_pointer_file) else 0
    training_data=[]
    docs=list(collect_samples_from_pointer(size,current_message_id=current_message_id))
    current_message=(docs[-1] if len(docs) > 0 else latest_message)
    current_message_id=current_message.get('id',current_message_id)

    messages=list(map(encode_sample,docs))
    with open("training_pointer.json",'w') as message_pointer:
        message_pointer.write(json.dumps({'current_id':current_message_id}))

    for message in messages: training_data.append(json.dumps(message))
    return training_data
while True:

    # Add docs to the collection. Can also update and delete. Row-based API coming soon!
    collection.add(
        documents=get_messages_for_indexing(10), # we handle tokenization, embedding, and indexing automatically. You can skip that and add your own embeddings as well
    )

