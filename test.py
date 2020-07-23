import os
import discord
import platform
import datetime
import embeds
from dotenv import load_dotenv
from discord.ext import commands

embed = discord.Embed(title="Help with commands for the bot", colour = 16761035)
embed.add_field(
    name="`!ping`",
    value="Replys with the latency of the bot.",
    inline=True
)
embed.add_field(
    name="`!help`",
    value="Displays this view.",
    inline=True
)
embed.add_field(
    name = "`!info`",
    value = "Displays info about the bot.",
    inline = True
)
print(embed,False)
embed1=embeds.create_embed(
    "Help with commands for the bot",
    16761035,
     [
         ["!ping", "Replys with the latency of the bot", True],
         ["!help", "Displays this view.", True],
         ['!info', 'Displays info about the bot', True],
     ]
)
print(embed1)