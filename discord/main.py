import discord
import os
import

client = discord.Client()

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
@client.event
async def on_ready():
    # log('Logged in as')
    # log(client.user.name)
    # log(client.user.id)
    # log('------')
    await handle_replies()

@client.event
async def on_message(message):

    if message.author.id == client.user.id:
        print ("not responding to self.")
        return

    if message.channel.id == int(os.environ['LOG_CHANNEL']):
        print("not responding to log.")
        return

    log(message.channel.id)

    incomeing.append(formatMessage(message))
    with open('log.json','w') as f:
        json.dump(incomeing,f)


### Reply handler##############
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

client.run(os.environ['DISCORD_TOKEN'])
