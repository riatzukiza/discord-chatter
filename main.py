
import asyncio

from multiprocessing import Process,Pipe
from threading import Thread

from  functools import reduce

import discord
import sys
import os
import random
import json

from pathlib import Path
# contents = Path(file_path).read_text()

ml_loop = asyncio.get_event_loop()
client = discord.Client(loop=ml_loop)

replies = []
incomeing = []

# parent_conn,ml_conn = Pipe()

# def _ml(conn):
def _ml():

    from textgenrnn import textgenrnn
    print ("ML")

    textgen = textgenrnn("./json_message_model.hdf5")

    messages = []

    def generate():
        print ("generating message")
        return textgen.generate(n=1,prefix="",temperature=random.uniform(0.4,0.6),return_as_list=True)[0]

    def train(d,e,sample_size=0):

        def count (l,m):
            return l+len(m)

        l = reduce(count,d,0)
        print("length",l)
        textgen.train_on_texts(d, None,  l if l < 128 else 128, e,gen_epochs=sample_size)
        textgen.save("./json_message_model.hdf5")

    def think(m):
        def train_til_valid():
            try:
                print("messages",messages)
                train(messages, 10)

                txt = generate()

                reply = json.loads(txt)

                replies.append(reply)
            except:
                try:
                    __import__('traceback').print_exc()
                    train_til_valid()
                except:
                    __import__('traceback').print_exc()

        message_json = json.dumps(m , sort_keys=True, separators=(",",":"))
        messages.append(message_json)
        if len(messages) > 50:
            print ( "forgetting a message",messages.pop(0))
        train_til_valid()

    while True:
        #think(conn.recv())
        if incomeing:
            think(incomeing.pop(0))



# asyncio.ensure_future(ml_loop.run_in_executor(None,handle_replies))

# ml_process = Process(target=_ml,args=(ml_conn,))

ml_process = Thread(target=_ml)
ml_process.start()


def formatMessage(message):

    channel = message.channel
    author = message.author
    # server = channel.server

    return {
        "content":message.content,
        "author":author.id,
        # "server":server.id,
        "channel":channel.id
    }
# current_message_id = 0
@client.event
async def on_message(message):

    if message.author.id == client.user.id:
        print ("not responding to self.")
        return

    incomeing.append(formatMessage(message))
    # parent_conn.send(formatMessage(message))
    await handle_recent_replies()

async def handle_recent_replies():
    while replies:
        print("handling replies",replies)
        reply = replies.pop(0)
        await client.get_channel(reply["channel"]).send(reply_json["content"])

async def handle_replies():
    while True:
        await handle_recent_replies()

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

client.run('NDQ5Mjc5NTcwNDQ1NzI5Nzkz.DmZ69A.V-ro5Sy7z2fB8OsSdGCvYcTtC2E')
