
import os
from pymongo import MongoClient

MONGODB_HOST_NAME= os.environ['MONGODB_HOST_NAME']
MONGODB_ADMIN_DATABASE_NAME=os.environ['MONGODB_ADMIN_DATABASE_NAME']
MONGODB_ADMIN_USER_NAME=os.environ['MONGODB_ADMIN_USER_NAME']
MONGODB_ADMIN_USER_PASSWORD=os.environ['MONGODB_ADMIN_USER_PASSWORD']

def get_database():

    CONNECTION_STRING = f"mongodb+srv://{MONGODB_ADMIN_USER_NAME}:{MONGODB_ADMIN_USER_PASSWORD}@{MONGODB_HOST_NAME}/{MONGODB_ADMIN_DATABASE_NAME}"
    client = MongoClient(CONNECTION_STRING)
    return client[MONGODB_ADMIN_DATABASE_NAME]

# This is added so that many files can reuse the function get_database()
if __name__ == "__main__":
    # Get the database
    dbname = get_database()
