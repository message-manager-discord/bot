# main.py
import os
import discord
import platform
import datetime
import logging
import asyncio
from discord.ext import commands
from src import helpers, checks

# Start up the discord logging module.
logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


# load all the enviromental variables 
config_vars = helpers.fetch_config()

token = config_vars["token"]
owner = config_vars["owner"]
prefix = config_vars["prefix"]
allowed_server = config_vars["allowed_server"]
management_role = config_vars["management_role"]
bypassed_users = config_vars["bypassed_users"]

# Creating the bot class
bot = commands.Bot(command_prefix = prefix, case_insensitive = True)

# Removing the default help command
bot.remove_command('help')

#creating the check that checks if the bot is being used the server that is specified in env.
        
@bot.check(checks.check_if_right_server)

# Defining the on_ready event
@bot.event
async def on_ready():
    # Print the bot invite link
    print(f"https://discord.com/api/oauth2/authorize?client_id={bot.user.id}&permissions=519232&scope=bot")
    print(f"Logged on as {bot.user}!")
    
    await bot.change_presence(
        activity = discord.Game(name="Watching our important messages!")
    )   # Change the presence of the bot

@bot.event
async def on_guild_join(guild):
    channel = guild.system_channel
    embed = helpers.create_embed(
        "Hi there!",
        16761035,
        [
            ["Startup!", "Thank you for inviting me to your server! \nMy prefix here is: `{prefix}`\nHead over to the (README)[https://github.com/AnotherCat/custom_helper_bot/blob/master/README.md] for setup instructions!"]
        ]
    )
    channel.send(embed=embed)

extensions = [
    'cogs.maincog',
    'cogs.messages',
    'cogs.admin'
]
for extension in extensions:
    bot.load_extension(extension)
"""
bot.load_extension('cogs.maincog')
bot.load_extension('cogs.messages')
bot.load_extension('cogs.admin')
"""
bot.run(token)

