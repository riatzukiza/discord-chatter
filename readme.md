# Discord Duck 

keeps memory of the last n messages in each channel, and who sent them.

each channel, and each user has its own models

each channel, group chat, and PM session represents a conversation.
each conversation has its own model.

The frequency with which messages occur in a conversation, influences the overall weight that
model has on the final output.

the speaking model takes as input the result of each conversations model


# Some important commands 

```
docker build --tag discord-rnn-gpu . # This sets everything up
docker run -it --gpus=all --rm --volume ${PWD}:/app discord-rnn-gpu # Runs it if Nvidia container framework is present.
docker run -it --gpus=all --volume ${PWD}:/app discord-rnn-gpu # So you can have a state that will persist
```
