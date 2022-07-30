require('dotenv').config()
const Discord = require('discord.js');
const Twitter = require('twitter')

const discord = new Discord.Client({
    intents:[Discord.GatewayIntentBits.Guilds]
});

const filter = "AI"

discord.on('ready', async () => {
    const channel_id = "451788481140752384"
    console.log({channel_id})
    const twitterChannel = await discord.channels.fetch(channel_id)

    var twitter = new Twitter({
        consumer_key: process.env.TWITTER_CONSUMER_KEY,
        consumer_secret: process.env.TWITTER_CONSUMER_SECRET,
        access_token_key: process.env.TWITTER_ACCESS_TOKEN_KEY,
        access_token_secret: process.env.TWITTER_ACCESS_TOKEN_SECRET

    });

    var stream = twitter.stream('statuses/filter', {track: filter});
    stream.on('data', (event) => {
        if(event.lang === 'en' ) {
            let text = event?.extended_tweet?.full_text || event.text
            console.log("text",text)
            twitterChannel.send(text)
        }

    });

    stream.on('error', (error) => console.error(error));
});


discord.login(process.env.DISCORD_KEY);
