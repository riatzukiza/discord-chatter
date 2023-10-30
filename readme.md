# Discord LLM chat agent

Have you ever wanted a robot friend? Feeling lonely? bored?
Do you have a graphics card?

Your in luck, these days, you can make friends if you have enough compute!

# Quick start

You will need the nvidia container framework if you want to use a docker container.

### With docker compose

The easiest way to get the model running is with docker compose and the nvidia-container framework.
The compose file in here right now picks a specific GPU, you'll have to update that right now if your GPU has a different ID
(like if you have more than one GPU or you put it in a slot other than the first one)

```
docker-compose up -d # I recomend running it in a daemon other wise you risk killing it mid training when you exit the logs
docker-compose logs -f gpt-trainer gpt-generator message-dispatcher # probably the most important of the containers to keep an eye on
```

## Description

discord chatter bot is a long running project of mine to create an interesting discord chat bot experience.

Unlike other bots, this bot is not restrained to a reply/response model. This bot does what it wants, and you can't really stop it.
We often call it a duck, because of imprinting. It'll learn to say what you and your friends say, in the rooms you say them in.

Maybe it'll learn something from some where else, and let you know.

### Training data

Duck bot learns of a json array of messages

```python
[{
    "recipient":message['recipient'],
    "recipient_name":message['recipient_name'],
    "created_at":str(message['created_at']),
    "raw_mentions":message['raw_mentions'],
    "author_name":message['author_name'],
    "guild":message['guild'],
    "channel_name": message['channel_name'],
    "content":message['content'],
    "author":message['author'],
    "channel":message['channel']
}, {
    "recipient":message['recipient'],
    "recipient_name":message['recipient_name'],
    "created_at":str(message['created_at']),
    "raw_mentions":message['raw_mentions'],
    "author_name":message['author_name'],
    "guild":message['guild'],
    "channel_name": message['channel_name'],
    "content":message['content'],
    "author":message['author'],
    "channel":message['channel']
},{
    "recipient":message['recipient'],
    "recipient_name":message['recipient_name'],
    "created_at":str(message['created_at']),
    "raw_mentions":message['raw_mentions'],
    "author_name":message['author_name'],
    "guild":message['guild'],
    "channel_name": message['channel_name'],
    "content":message['content'],
    "author":message['author'],
    "channel":message['channel']
},{
    "recipient":message['recipient'],
    "recipient_name":message['recipient_name'],
    "created_at":str(message['created_at']),
    "raw_mentions":message['raw_mentions'],
    "author_name":message['author_name'],
    "guild":message['guild'],
    "channel_name": message['channel_name'],
    "content":message['content'],
    "author":message['author'],
    "channel":message['channel']
}
]
```

The only data is is actually using right now is the channel and content,
but giving it the rest of the data gives it some additional context and makes the outputs more flavorful.

```bash
PYTHONUNBUFFERED=1 # So your logs come out faster
DISCORD_TOKEN=<very secret>
DEFAULT_CHANNEL=<channel ID>
DISCORD_CLIENT_USER_ID=<channel ID> # So I don't need to include the client just for an id
DISCORD_CLIENT_USER_NAME=Duck

# When generating text, how spicy do you want it to be?
# Higher temperatures give greater variety, but are more unstable and more likely to contain mistakes
MIN_TEMP=0.3
MAX_TEMP=1.5

# Location on the mounted volume where your model resides, if it doesn't exist
# it is created
MODEL_PATH=./models/<where your duck is>
GEN_EPOCHS=2

MODEL_NAME=Duck
LD_LIBRARY_PATH=/opt/conda/lib

# For how many epochs do you want to train the model per itteration?
TEXTGEN_NUM_EPOCHS=30
# The base Learning rate for the model, for every epoch up to TEXTGEN_NUM_EPOCHS
# this scales down.
TEXTGEN_BASE_LR=0.004
# How many RNN layers? Once you've created the model, this value cannot change
TEXTGEN_RNN_LAYERS=4
# How many nodes in each RNN layer? Once you've created the model this value cannot change
TEXTGEN_RNN_SIZE=128

# parameters
TEXTGEN_VERBOSE=2

# training settings
# How much of the training data is used to train the model?
# 1.0 and the model is trained on all of it, with none left aside for validation
# less than 1.0, and some is kept aside for validation.
# validation data helps prevent over fitting.
TEXTGEN_TRAIN_SIZE=0.8

# drop out on the embedding layer, help prevents over fitting.
# don't make this too large.
TEXTGEN_DROPOUT=0.1

# model batch size, large values allow the model to train on mode data at once,
# might take up more space in memory as a result
TEXTGEN_BATCH_SIZE=1024

# Model structure
# If true, the model can predict sequences in both direction
TEXTGEN_RNN_BIDIRECTIONAL=False

# I don't understand these ones very well yet.
TEXTGEN_MAX_LENGTH=40
TEXTGEN_MAX_WORDS=10000
TEXTGEN_DIM_EMBEDDINGS=100

# How many examples the message generator will create to be sent to discord
EXAMPLES_GENERATED_PER_BATCH=10

# the maximum length of the string that is generated
MAX_GENERATED_LENGTH=4096

# whats the model called
MODEL_NAME=Duck
```

# Contributions welcome!

I only have so much time, even if you just want to run it, it will help out a lot.
