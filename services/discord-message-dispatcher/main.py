from shared.mongodb import generated_message_collection
client = Bot(command_prefix=f"ok {os.environ['MODEL_NAME']}")
from  discord.ext.commands import Bot
while True:
    unsent_messages = generated_message_collection.find({"sent":False, "is_valid":True})
