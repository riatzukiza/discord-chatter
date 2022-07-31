import json
import os

messages=[]
replies=[]
incomeing=[]
try:
    messages = json.load(open(os.environ['MESSAGES_JSON']))
    replies = json.load(open(os.environ['REPLIES_JSON']))
    incomeing = json.load(open(os.environ['INCOMEING_JSON']))
except IOError:
    pass
except json.decoder.JSONDecodeError:
    pass

