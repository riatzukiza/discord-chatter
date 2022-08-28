from ..mongodb import discord_channel_collection
class ChannelManager:
    def __init__(self):
        self.collection = discord_channel_collection
        self.channels=client.get_all_channels()


    def get_channel(self, channel_id):
        return self.collection.find_one({'_id': channel_id})

    def get_channels(self):
        return self.collection.find()
