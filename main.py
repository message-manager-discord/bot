# main.py
import os
import discord
import platform
import datetime
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix = 'h!', case_insensitive = True)

bot.remove_command('help')

@bot.event
async def on_ready():
    print(https://discord.com/api/oauth2/authorize?client_id={0}&permissions=519232&scope=bot".format(bot.user.id))
    print("Logged on as {0}!".format(bot.user))
    
    await bot.change_presence(
        activity = discord.Game(name="Watching for messages!")
    )

@bot.command(name='help', help='Responds with an embed with all the commands and options')
async def help(ctx, help_type = None):
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
        
    await ctx.send(embed=embed)


@bot.command(name = 'info')
async def info(ctx):
    embed = discord.Embed(title="Info about the Bot", colour=discord.Colour(0xc387c1))

    embed.set_thumbnail(url=f"{bot.user.avatar_url}")
    embed.set_footer(text="hi", icon_url=f"{bot.user.avatar_url}")

    embed.add_field(name="Username", value=bot.user, inline=True)
    embed.add_field(name="Owner", value=f'<@{684964314234618044}>', inline=True)
    embed.add_field(name="Discord.py Version", value="1.4.0", inline=True)
    embed.add_field(name="Python Version", value=platform.python_version(), inline=True)
    embed.add_field(name="Number of Servers", value=len(bot.guilds), inline=True)
    # embed.add_field(name="Uptime", value=get_uptime(), inline=True)
    embed.set_footer(text = datetime.datetime.now())
    await ctx.send(embed=embed)

#  Returns the bot side latency
@bot.command (name = "ping")
async def ping(ctx):
    await ctx.send(f"**ping** {round(bot.latency*100)}ms")   # get the bot latency in seconds then conver it into milli seconds.

bot.run(TOKEN)