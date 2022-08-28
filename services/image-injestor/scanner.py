import discord
import asyncio
class Scanner:

    def __init__(self, client):
        self.client=client
    def scan_all_channels(self):
        for channel in self.client.get_all_channels():
            try:
                if isinstance(channel, discord.TextChannel):
                    print(f"Indexing channel {channel}")
                    await asyncio.sleep(1)
                    await index_channel( channel )
            except Exception as e:
                await asyncio.sleep(10)
                print("something happened:")
                print(e)
                traceback.print_exc()
