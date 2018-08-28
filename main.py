import discord
import asyncio
import sys
import os
import random
import json
from pathlib import Path
# contents = Path(file_path).read_text()

from textgenrnn import textgenrnn

client = discord.Client()

textgen = textgenrnn("./models/json_message_model.hdf5")
# textgen.save("./json_message_model.hdf5")

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


message_channels = dict()
messages = []

# HISTORY_LIMIT = 100

# def add_message (c,message):
#     channel = c.name

#     print(channel)
#     if  channel in message_channels:
#         message_channels[channel].append(message)

#         if len(message_channels[channel]) >= HISTORY_LIMIT:
#             message_channels[channel].pop(0)

#     else: message_channels[channel] = [message]

# def add_message(channel,message):


txt = ""
current_message_id = 0
# message_log_path = os.path.join(os.getcwd(),"log.txt")
# print (message_log_path)

def train(d,e,sample_size=0):
    textgen.train_on_texts(d, None, 128, e,gen_epochs=sample_size)
    textgen.save("./json_message_model.hdf5")
# message_log_text = Path(message_log_path).read_text()

# print(message_log_text)

try: textgen.train_from_file("./log.txt",num_epochs=5);
except ValueError:print ("not training from logs")


def save_message(content):
    with open(message_log_path,"a+") as message_log:
        message_log.write(content+"</m>\n")


messages = json.load(open("./log.json"))

train(messages, 3)
@client.event
async def on_message(message):
    global txt
    global current_message_id
    channel = message.channel
    author = message.author
    server = channel.server
    # add_message(channel,message)
    i = current_message_id + 1
    current_message_id = i


    if message.author.id == client.user.id:
        print ("not responding to self.")
        return

    print(message)
    m = {
        "content":message.content,
        "author":author.id,
        "server":server.id,
        "channel":channel.id
    }
    try:

        message_json = json.dumps(m , sort_keys=True, separators=(",",":"))
        messages.append(message_json)
        # json.dump(messages,open("./log.json","w"))

        # save_message(message_json+",")
        if i % 100 == 0: train(messages[len(messages) - 500:], 3)

        print ("generating message")
        txt = textgen.generate(n=1,prefix="",temperature=random.uniform(0.4,0.6),return_as_list=True)[0]
        print (txt)
        reply_json = json.loads(txt)

        await client.send_message(client.get_channel(reply_json["channel"]),reply_json["content"])

        # new_message = txt.split("</m>")

        # if len(new_message) > 1:
        #     txt = "".join(new_message[1:])
        #     await client.send_message(channel,new_message[0])
        # else:
        #     txt = "".join(new_message)

        print ("generated message,sending:")
        print(txt)

    except Exception as e:
        print("fail",e)


client.run('NDQ5Mjc5NTcwNDQ1NzI5Nzkz.DeiaGQ.Fd7sBa0WSu_15utvWYDjEFy5HtY')
