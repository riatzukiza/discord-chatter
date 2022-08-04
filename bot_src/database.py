
import os

MONGODB_HOST_NAME= os.environ['MONGODB_HOST_NAME=']
MONGODB_ADMIN_DATABASE_NAME=os.environ['MONGODB_ADMIN_DATABASE_NAME']
MONGODB_ADMIN_USER_NAME=os.environ['MONGODB_ADMIN_USER_NAME']
MONGODB_ADMIN_USER_PASSWORD=os.environ['MONGODB_ADMIN_USER_PASSWORD']

def get_database():
    from pymongo import MongoClient
    import pymongo

    # Provide the mongodb atlas url to connect python to mongodb using pymongo
    CONNECTION_STRING = f"mongodb+srv://{MONGODB_ADMIN_USER_NAME}:{MONGODB_ADMIN_USER_PASSWORD}@{MONGODB_HOST_NAME}/{MONGODB_ADMIN_DATABASE_NAME}"

    # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
    from pymongo import MongoClient
    client = MongoClient(CONNECTION_STRING)

    # Create the database for our example (we will use the same database throughout the tutorial
    return client['admin']
    
# This is added so that many files can reuse the function get_database()
if __name__ == "__main__":    
    
    # Get the database
    dbname = get_database()
