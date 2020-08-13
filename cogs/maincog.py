import discord
from discord.ext import commands
from src import helpers
# from main import prefix

prefix = '`'

class MainCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    
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

    
def setup(bot):
    bot.add_cog(MainCog(bot))