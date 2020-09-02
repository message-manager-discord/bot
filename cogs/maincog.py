import discord, platform, datetime
from discord.ext import commands
from src import helpers
# from main import prefix

prefix = helpers.fetch_config('prefix')
owner = helpers.fetch_config('owner')

class MainCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = datetime.datetime.utcnow()

    @commands.Cog.listener()
    async def on_ready(self):
        self.start_time = datetime.datetime.utcnow()

    @commands.command(name='help', help='Responds with an embed with all the commands and options')
    async def help(self, ctx):
        embed=helpers.create_embed(
        "Help with commands for the bot",
        16761035,
            [
                [f"`{prefix}ping`", "Replys with the latency of the bot", True],
                [f"`{prefix}help`", "Displays this view.", True],
                [f'`{prefix}info`', 'Displays info about the bot', True],
                [
                    f"`{prefix}send [channel_id] [content]`",
                    "Sends a message from the bot in the specificed channel",
                    True
                ],
                [
                    f'`{prefix}edit [channel_id] [message_id] [new_content]`',
                    'Edits a message, message **must** be from the bot',
                    True
                ],
                [
                    f"`{prefix}delete [channel_id] [message_id]`",
                    "Deletes the message from the bot. **Must** be from the bot",
                    True
                ],    
                [
                    f"`{prefix}stats-force-update`",
                    "Update the stats channels",
                    True
                ]        

            ]
        )    
        await ctx.send(embed=embed)

    # Create the info command.
    @commands.command(name = 'info')
    async def info(self, ctx):
        total_seconds = (datetime.datetime.utcnow() - self.start_time).total_seconds()
        days = total_seconds // 86400
        hours = (total_seconds - (days * 86400)) // 3600
        minutes = (total_seconds - (days * 86400) - (hours * 3600)) // 60
        seconds = total_seconds - (days * 86400) - (hours * 3600) - (minutes * 60)
        embed_content = [
            ["Username", self.bot.user, True],
            ["Prefix", f'`{prefix}`', True],
            ["Version", "v0.1.0-alpha", True],
            ["Docs", "[The Docs](https://anothercat.github.io/custom_helper_bot/)", True],
            ["Developer",'[Another Cat](https://github.com/AnotherCat)', True], # The developer (me), Must not be changed, as per the LICENSE
            ["Discord.py Version", discord.__version__, True],
            ["Python Version", platform.python_version(), True],
            ["System", platform.system(), True],
            ["Uptime", f"{int(days)} days {int(hours)} hours {int(minutes)} minutes {int(seconds)} seconds", True],
            ["Number of Servers",len(self.bot.guilds), True]
        ]
        if owner != 'None':
            embed_content.insert(5,["Owner", f"<@{owner}>", True]) # Check if the config variable owner is not "None", then if not adding the field to the embed.

        embed=helpers.create_embed(
            "Info about the Bot",
            discord.Colour(0xc387c1),
            embed_content
        )    
        embed.set_thumbnail(url=f"{self.bot.user.avatar_url}")
        embed.set_footer(text = datetime.datetime.utcnow())
        await ctx.send(embed=embed)

    @commands.command (name = "ping")
    async def ping(self, ctx):
        message = await ctx.send('Pong!')
        ping_time = (message.created_at-ctx.message.created_at).total_seconds() * 1000
        await message.edit(content=f'Ping! Took: {int(ping_time)}ms')


    
def setup(bot):
    bot.add_cog(MainCog(bot))