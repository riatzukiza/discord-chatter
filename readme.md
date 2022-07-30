# Discord Duck 

```

DISCORD_TOKEN=<VERY SECRET>
LOG_CHANNEL=<CHANNEL ID>
MAX_MESSAGES=100
BATCH_SIZE=2048
SPEECH_THREADS=2
EPOCHS_PER_MESSAGE=20
MIN_TEMP=0.4
MAX_TEMP=0.6
```




# Some important commands 

```
docker build --tag discord-rnn-gpu . # This sets everything up
docker run -it --gpus all --rm --volume ${PWD}:/app discord-rnn-gpu # Runs it if Nvidia container framework is present.
docker run -it --gpus all --volume ${PWD}:/app discord-rnn-gpu # So you can have a state that will persist
docker run -it --gpus all --env-file .env --volume ${PWD}:/app discord-rnn-gpu # So you can have a state that will persist with an environment file
```
