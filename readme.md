# Discord Duck 

+ Speaking model
+ Thought Model
+ Emotional model
+ Semantic model
+ user models
+ channel models

keeps memory of the last n messages in each channel, and who sent them.

each channel, and each user has its own models

each channel, group chat, and PM session represents a conversation.
each conversation has its own model.

The frequency with which messages occur in a conversation, influences the overall weight that
model has on the final output.

the speaking model takes as input the result of each conversations model


# Questions

+ How do we decide when and where to send messages?

We should take into consideration the topic of conversation.
What is the bot currently interested in?
https://discordapp.com/oauth2/authorize?&client_id=449279570445729793&scope=bot&permissions=0
