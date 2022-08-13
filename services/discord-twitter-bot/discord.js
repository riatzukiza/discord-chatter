require('dotenv').config()

const Discord = require('discord.js');
const client = new Discord.Client();

client.on('ready', () => {
    console.log(`Logged in as ${client.user.tag}!`);
});

client.on('message', msg => {
    chatLogFile.write(msg.content + "\n")
});


client.login(process.env.DISCORD_KEY);
