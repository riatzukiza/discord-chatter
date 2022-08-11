import os
from pymongo import MongoClient

from . import settings


def get_database():

    CONNECTION_STRING = f"mongodb+srv://{settings.MONGODB_ADMIN_USER_NAME}:{settings.MONGODB_ADMIN_USER_PASSWORD}@{settings.MONGODB_HOST_NAME}/{settings.MONGODB_ADMIN_DATABASE_NAME}"
    client = MongoClient(CONNECTION_STRING)
    return client[settings.MONGODB_ADMIN_DATABASE_NAME]

# This is added so that many files can reuse the function get_database()
if __name__ == "__main__":
    # Get the database
    dbname = get_database()

db=get_database()
discord_message_collection=db[f'discord_messages']
generated_message_collection=db[f'generated_messages']
