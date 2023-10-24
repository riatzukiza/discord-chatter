import os

MIN_TEMP=float(os.environ.get('MIN_TEMP',0.5))
MAX_TEMP=float(os.environ.get('MAX_TEMP',1.2))

MONGODB_HOST_NAME= os.environ.get('MONGODB_HOST_NAME', 'mongo')
MONGODB_ADMIN_DATABASE_NAME=os.environ.get('MONGODB_ADMIN_DATABASE_NAME','database')
MONGODB_ADMIN_USER_NAME=os.environ.get('MONGODB_ADMIN_USER_NAME','root')
MONGODB_ADMIN_USER_PASSWORD=os.environ.get('MONGODB_ADMIN_USER_PASSWORD','example')

DISCORD_TOKEN=os.environ['DISCORD_TOKEN']

DISCORD_CLIENT_USER_ID = os.environ.get('DISCORD_CLIENT_USER_ID')
DISCORD_CLIENT_USER_NAME = os.environ.get('DISCORD_CLIENT_USER_NAME')

DEFAULT_CHANNEL=os.environ['DEFAULT_CHANNEL']

model_path="/app/models/duck_gpt.v0.2.0/"
