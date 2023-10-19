import os
from pymongo import MongoClient

from . import settings


def get_database():

    CONNECTION_STRING = f"mongodb://{settings.MONGODB_HOST_NAME}/{settings.MONGODB_ADMIN_DATABASE_NAME}"
    client = MongoClient(CONNECTION_STRING)
    return client[settings.MONGODB_ADMIN_DATABASE_NAME]

# This is added so that many files can reuse the function get_database()
if __name__ == "__main__":
    # Get the database
    dbname = get_database()

db=get_database()
discord_message_collection=db['discord_messages']

generated_message_collection=db['generated_messages']
discord_channel_collection=db['discord_channels']
discord_user_collection=db['discord_users']
discord_server_collection=db['discord_servers']
duck_gpt=db['duck_gpt']
