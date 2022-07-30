
import asyncio
import tensorflow as tf

from multiprocessing import Process,Pipe
from threading import Thread
from textgenrnn.textgenrnn import textgenrnn

import discord
import sys
import os
import random
import json

from pathlib import Path
# contents = Path(file_path).read_text()

ml_loop = asyncio.get_event_loop()
client = discord.Client(loop=ml_loop)


messages = json.load(open('./messages.json'))
replies = json.load(open('./replies.json'))
incomeing = json.load(open('./log.json'))

textgen = textgenrnn("./json_message_model.hdf5")
logging=False

def log(m):
    if logging:
        replies.append({
            "channel":781732734229020672 ,
            "content":m
        })

def generate():
    log ("generating message")
    textgen = textgenrnn("./json_message_model.hdf5")
    return textgen.generate(
        progress=False,
        n=1,prefix="",temperature=random.uniform(float(os.environ['MIN_TEMP']),float(os.environ['MAX_TEMP'])),return_as_list=True)[0]

# parent_conn,ml_conn = Pipe()


# gpus = tf.config.list_logical_devices('GPU')
# strategy = tf.distribute.MirroredStrategy(gpus)
# def _ml(conn):
def speak():
    while True:
        txt = generate()
        # log("I have something to say")
        # log(txt)
        reply = json.loads(txt)
        replies.append(reply)
        with open('replies.json','w') as f:
            json.dump(replies,f)

for i in range(int(os.environ['SPEECH_THREADS'])):
    speak_process = Thread(target=speak)
    speak_process.start()

def train(d,e,sample_size=0):
    # with strategy.scope():
    textgen.train_on_texts(d, None, int(os.environ['BATCH_SIZE']), e,gen_epochs=sample_size,
                           # verbose=0,
                           # verbose=1,
                           multi_gpu=True
                            # , multi_gpu=bool(random.getrandbits(1))
                            )
    textgen.save("./json_message_model.hdf5")
def think(m):
    try:
        log(m)
        message_json = json.dumps(m , sort_keys=True, separators=(",",":"))
        messages.append(message_json)
        if len(messages) > int(os.environ['MAX_MESSAGES']):
            replies.append({
                "channel":781732734229020672 ,
                "content": f'forgetting a message {messages.pop(0)}'
            })

        with open('messages.json','w') as f:
            json.dump(messages,f)

        # error log logs
        # replies.append({
        #     "channel":781732734229020672 ,
        #     "content":"Training..."
        # })

        train(messages, int(os.environ['EPOCHS_PER_MESSAGE']))


    except Exception as e:
        try:
            # error log bot channel
            replies.append({
                "channel":483860795575238657,
                "content":"&talk Quack quack quack..."

            })
            # error log logs
            replies.append({
                "channel":781732734229020672 ,
                "content":str(e)
            })

            # chocos duck fun
            replies.append({
                "channel":343299242963763200,
                "content":"!randomsentence"
            })
            __import__('traceback').print_exc()
        except:
            __import__('traceback').print_exc()
            log('Failed to print traceback')
def _ml():
    while True:
        #think(conn.recv())
        if incomeing:
            log("bout to think about this...")
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

    if message.channel.id == int(os.environ['LOG_CHANNEL']):
        print("not responding to self.")
        return

    log(message.channel.id)
    log(f"Got a message from {message.author.name} in {message.channel.name}: {message.content}")

    incomeing.append(formatMessage(message))
    with open('log.json','w') as f:
        json.dump(incomeing,f)
    # parent_conn.send(formatMessage(message))

async def handle_recent_replies():
    while replies:
        # logs("handling replies",replies)
        reply = replies.pop(0)
        with open('replies.json','w') as f:
            json.dump(replies,f)
        await client.get_channel(reply["channel"]).send(reply["content"])

async def handle_replies():
    while True:
        log("Checking for replies")
        await asyncio.sleep(5)
        await handle_recent_replies()

@client.event
async def on_ready():
    log('Logged in as')
    log(client.user.name)
    log(client.user.id)
    log('------')
    await handle_replies()

client.run(os.environ['DISCORD_TOKEN'])
