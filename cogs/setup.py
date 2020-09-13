import discord, platform, datetime, asyncio, random, string
from discord.ext import commands
from src import helpers, checks, errors, db
from main import logger


class SetupCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_command_error(self, ctx, error):
        if isinstance(
            error,
            (
                errors.MissingPermission,
                errors.InputContentIncorrect
            )
        ):
            await ctx.send(error)
        else:
            raise error
    
    @commands.has_guild_permissions(administrator=True)
    @commands.group()
    async def setup(self, ctx):
        if ctx.invoked_subcommand is None:
            prefix = await db.pool.get_prefix(ctx.guild.id)
            embed = discord.Embed(title = "Setup!", description = "Setup values for your server!")
            embed.add_field(
                name=f"`{prefix}setup admin <role>`",
                value="This is the role that allows admin access to admin commands.",
                inline = False
            )
            embed.add_field(
                name=f"`{prefix}setup prefix <prefix>`",
                value="Sets the prefix for this server.",
                inline = False
            )
            embed.add_field(
                name=f"`{prefix}setup bot-stats <channel>`",
                value="Sets the voice channel for the bot count",
                inline = False
            )
            embed.add_field(
                name=f"`{prefix}setup user-stats <channel>",
                value="Sets the voice channel for the user count",
                inline = False
            )
            await ctx.send(embed=embed)

    @setup.command(name='prefix')
    async def return_prefix(self, ctx, new_prefix = None):
        prefix = await db.pool.get_prefix(ctx.guild.id)
        if new_prefix == None:
            await ctx.send(f"My prefix for this server is: `{prefix}`")
        else:
            if len(new_prefix) >1:
                raise errors.InputContentIncorrect(
                "Prefix's can only be 1 character long!"
            )
            else:
                await db.pool.update_prefix(ctx.guild.id, new_prefix)
                await ctx.send(
                    embed = discord.Embed(
                        title = 'Config updated!',
                        description = f"Server prefex updated from `{prefix}` to `{new_prefix}`"
                    )
                )


    @commands.command(name='prefix')
    async def prefix(self, ctx):
        prefix = await db.pool.get_prefix(ctx.guild.id)
        await ctx.send(f"My prefix for this server is: `{prefix}`")
        


def setup(bot):
    bot.add_cog(SetupCog(bot))
    print('    Setup cog!')