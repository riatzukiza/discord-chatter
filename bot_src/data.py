import json
import os

# messages=[]
# replies=[]
# incomeing=[]
class JSONFile:
    def __init__(self, path, data={}):
        self.path=path
        try:
            self.load()
        except:
            self.data=data

    def save(self):
        with open(self.path,'w') as f:
            json.dump(self.data,f)


    def load(self ):
        self.data = json.load(open(self.path))

class JSONArrayFile(JSONFile): 
    def __init__(self, path, data=[], limit=1000):
        super().__init__(path, data)
        self.limit = limit

    def append(self, data, save=False):
        self.data.append(data)
        if len(self.data) > self.limit:
            self.data = self.data[-self.limit:]
        if save:
            self.save()

    def pop(self,i, save=False):
        el = self.data.pop(i)
        if save:
            self.save()
        return el



messages=JSONArrayFile(os.environ.get('MESSAGES_JSON','./data/messages.json'),limit=int(os.environ.get("MAX_MESSAGES",10000)))
labels=JSONArrayFile(os.environ.get('LABELS_JSON','./data/labels.json'),limit=int(os.environ.get("MAX_MESSAGES",10000)))
replies=JSONArrayFile(os.environ.get('REPLIES_JSON','./data/replies.json'), limit=int(os.environ.get("MAX_REPLIES",10000)))
