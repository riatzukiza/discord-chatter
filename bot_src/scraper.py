import requests
from datetime import datetime
import json
import argparse

def change_date_format(x):
    x['timestamp'] = datetime.strptime(x['timestamp'][:19], '%Y-%m-%dT%H:%M:%S')
    return x

def enrich(m):
    m = change_date_format(m)
    m['created_date'] =  datetime.now()
    return m

def retrive_messages(token, chanel_id, limit=50, before_id=None, after_id=None):
    headers = {
        "authorization": token
    }
    if before_id:
        r =  requests.get(f"https://discord.com/api/v8/channels/{chanel_id}/messages?limit={limit}&before={before_id}", headers=headers)
    elif after_id:
        r =  requests.get(f"https://discord.com/api/v8/channels/{chanel_id}/messages?limit={limit}&after={after_id}", headers=headers)
    else:
        r =  requests.get(f"https://discord.com/api/v8/channels/{chanel_id}/messages?limit={limit}", headers=headers)
    data = json.loads(r.text)
    return data

def create_fill_up_data(token, chanel_id, last_message_id=None, collector_limit=20000):
    print(f"create_fill_up_data, last id: {last_message_id}")
    collector = []
    while True:
        data = retrive_messages(token, chanel_id, limit=100, before_id=last_message_id)
        if len(data) > 0:
            data = [enrich(x) for x in data]
            for c in data:
                print(c['timestamp'], c['id'])
            collector += data
            if len(collector) > collector_limit:
                break
            last_message_id = data[-1]["id"]
            # time.sleep(2)
            print(f"last message id {last_message_id} collected messages {len(collector)}")
        else:
            print("This is the end!")
            break
    return collector

if __name__ == "__main__":
    
    # here put your token
    token = ""
    
    # here put your channel ids
    input_channels = [
    ]
    
    for channel_id in input_channels:
        channel_data = create_fill_up_data(token, channel_id, last_message_id=None, collector_limit=20000)
        print(f"Got {len(channel_data)} messages from channel {channel_id}")
        
        with open(f"discord_channel_{channel_id}_data.json", "w") as f:
            json.dump(channel_data, f)
