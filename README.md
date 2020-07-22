# Custom Helper Bot

## General Info

This is a general custom made bot.

Features are:

1. Sending messages in channels and being able to edit them with commands. (pending)
2. Sending announcements. (pending)

## Installation 

1. Clone this repo
2. Make sure you have the latest version of python
3. Creating a discord application and a bot user at the [discord dev website](https://discord.com/developers/applications)
4. Setting up `.env`
5. Running `main.py` 
6. Inviting the bot to your server, there will be an invite link in the python shell after you run it.



## Config

Create a python environment

Install the required packages with `pip -r requirments.txt`

This bot uses [dotenv](https://pypi.org/project/python-dotenv/) for environment variables. 

### Setting up `.env`

1. Create an empty file named `.env`
2. Add `DISCORD_TOKEN=bot_token` replacing bot_token with the bot's token. 