# main.py
import json
import os
import discord
import platform
import datetime
import src.helpers
import logging
from discord.ext import commands

# Start up the discord logging module.
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='a')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

with open('config.json') as f:
    config_vars = json.load(f)


# load all the enviromental variables 
token = config_vars["token"]
owner = config_vars["owner"]
prefix = config_vars["prefix"]
allowed_server = config_vars["allowed_server"]
management_role = config_vars["management_role"]
emojis = config_vars["emojis"]

# Creating the bot class
bot = commands.Bot(command_prefix = prefix, case_insensitive = True)

# Removing the default help command
bot.remove_command('help')

#creating the check that checks if the bot is being used the server that is specified in env.
def check_if_right_server(ctx):
    if allowed_server == 'None':
        return True
    elif ctx.message.guild.id == int(allowed_server):
        return True
    elif ctx.author.id = int(owner):
        return True
    else:
        return False

# Creating the check for the management role.
def check_if_manage_role(ctx):
    if management_role == "None":
        return True
    elif True:
        for role in ctx.author.roles:
            if int(management_role) == role.id:
                return True
                
    elif ctx.author.id == int(owner):
        return True
    else:
        return False

# Defining the on_ready event
@bot.event
async def on_ready():
    # Print the bot invite link
    print(f"https://discord.com/api/oauth2/authorize?client_id={bot.user.id}&permissions=519232&scope=bot")
    print(f"Logged on as {bot.user}!")
    
    await bot.change_presence(
        activity = discord.Game(name="Watching our important messages!")
    ) # Change the presence of the bot

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


# Create the bot command help. 
@bot.command(name='help', help='Responds with an embed with all the commands and options')
@commands.check(check_if_right_server)
async def help(ctx):
    embed=helpers.create_embed(
    "Help with commands for the bot",
    16761035,
        [
            [f"`{prefix}ping`", "Replys with the latency of the bot", True],
            [f"`{prefix}help`", "Displays this view.", True],
            [f'`{prefix}info`', 'Displays info about the bot', True],
            [
                f"`{prefix}send channel_id content`",
                "Sends a message from the bot in the specificed channel",
                True
            ],
            [
                f'`{prefix}edit channel_id message_id new_content`',
                'Edits a message, message **must** be from the bot for it to work',
                True
            ],
            [
                f"`{prefix}delete channel_id message_id`",
                "[DISABLED, in development] Deletes the message from the bot. **Must** be from the bot",
                True
            ],            
            [
                f"`{prefix}list_emojis`",
                "Lists all the emojis that the bot can access and that have been set in config.",
                True
            ],

        ]
    )    
    await ctx.send(embed=embed)

# Create the info command.
@bot.command(name = 'info')
@commands.check(check_if_right_server)
async def info(ctx):
    embed_content = [
         ["Username", bot.user, True],
         ["Prefix", prefix, True],
         ["Version", "0.0.0 (in development)", True],
         ["Developer",'<@684964314234618044>', True], # The developer (me), Must not be changed, as per the LICENSE
         ["Discord.py Version", discord.__version__, True],
         ["Python Version", platform.python_version(), True],
         ["Number of Servers",len(bot.guilds), True]
     ]
    if owner != 'None':
        embed_content.insert(4,["Owner", f"<@{owner}>", True]) # Check if the config variable owner is not "None", then if not adding the field to the embed.

    embed=helpers.create_embed(
        "Info about the Bot",
        discord.Colour(0xc387c1),
        embed_content
    )    
    embed.set_thumbnail(url=f"{bot.user.avatar_url}")
    embed.set_footer(text = datetime.datetime.now())
    await ctx.send(embed=embed)

# Create the send command. This command will send a message in the specificed channel.
@bot.command(name="send", rest_is_raw = True)
@commands.check(check_if_right_server)
@commands.check(check_if_manage_role)
async def send(ctx, channel_id, *, content):
    channel = bot.get_channel(int(channel_id)) # Get the channel.
    content = content[4:-3]
    msg = await channel.send(content)
    embed = helpers.create_message_info_embed('Send', ctx.author, content, msg)
    await ctx.send(embed=embed)

# Create the edit command. This command will edit the specificed message. (Message must be from the bot)
@bot.command(name="edit", rest_is_raw=True)  # rest_is_raw so that the white space will not be cut from the content.
@commands.check(check_if_right_server)
@commands.check(check_if_manage_role)
async def edit(ctx, channel_id, message_id, *, content):
    content = content[4:-3]
    #ctx.rest_is_raw = True
    msg = await helpers.get_message(bot, channel_id, message_id)
    #if msg.author != bot.user:
     #   raise SyntaxError # Checks if the author of the message is the bot, if not raises an error (will customise error later)

    original_content = msg.content    
    embed = helpers.create_message_info_embed('edit', ctx.author, content, msg)
    await msg.edit(content=content)
    await ctx.send(embed=embed)

# Create the command delete. This will delete a message from the bot. 
@bot.command(name = 'disabled_delete')
async def delete(ctx, channel_id, message_id):
    msg = helpers.get_message(channel_id, message_id)

    if msg.author != bot.user: # Check if the message author is the bot. 
        await ctx.send("That message was not from me! Try again.")
        
    else:
        await ctx.send(
            embed = helpers.create_embed(
                "Are you sure you want to delete this message?",
                'red',
                [
                    ["Channel", msg.channel.mention, False],
                    ["Content", msg.content, False]
                ]
            )
        )
        def is_correct(m):
            return m.author == ctx.author
        try:
            choice = await bot.wait_for('message', check=is_correct, timeout=20.0)
        except asyncio.TimeoutError:
            return await ctx.send('Timedout, Please re-do the command.')

        if choice.content.lower() == 'yes':
            embed = helpers.create_message_info_embed('delete', ctx.author, msg.content, msg)
            await msg.delete()
            await ctx.send(embed=embed)
        else:
            ctx.send(embed = helpers.create_embed(
                "Message deletion exited.",
                'red',
                [
                    ['', f'{ctx.author.mention}chose not to delete the message', False]
                ]
            )
            )
@bot.command(name="list_emojis")
@commands.check(check_if_right_server)
@commands.check(check_if_manage_role)
async def list_emojis(ctx):
    message = ''
    emojis_all = ''
    for emoji_id in emojis:
        if len(message) >1700:
            message = message + ' \n <:discordbackground1:737583861281718363>'
            await ctx.send(message)
            message = ''
        emoji = bot.get_emoji(int(emoji_id))
        
        message = message + f'\n\n`{str(emoji)}`, `:{emoji.name}:`, {str(emoji)}'
        emojis_all = emojis_all + str(emoji)
    if message != '':
        await ctx.send(message)
        await ctx.send(emojis_all)
    else:
        await ctx.send("There do not seem to be any emojis to list. Make sure you have config set up correctly!")

#  Returns the bot side latency
@bot.command (name = "ping")
@commands.check(check_if_right_server)
async def ping(ctx):
    await ctx.send(f"**ping** {round(bot.latency*100)}ms")   # get the bot latency in seconds then conver it into milli seconds.

bot.run(token)
