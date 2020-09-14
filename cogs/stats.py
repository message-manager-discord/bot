import discord, asyncio
from discord.ext import commands
from src import helpers, checks, errors, db
from main import logger

class StatsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot 

    def cog_check(self, ctx):
        return checks.check_if_manage_role(ctx)
    
    async def cog_command_error(self, ctx, error):
        if isinstance(error, errors.MissingPermission) or isinstance(error, errors.ContentError) or isinstance(error, errors.ConfigNotSet):
            await ctx.send(error)
        else:
            raise error
    
    async def update_stats(self, ctx):
        member_channel = await db.pool.get_member_channel(ctx.guild.id)
        bot_channel = await db.pool.get_bot_channel(ctx.guild.id)
        if member_channel is not None:
            member_channel_obj = self.bot.get_channel(int(member_channel))
            member_count = len([m for m in ctx.guild.members if not m.bot])
            if not member_channel_obj.name[12:] == str(member_count):
                await member_channel_obj.edit(name = f'User Count: {int(member_count)}')
        
        if bot_channel is not None:
            bot_channel_obj = self.bot.get_channel(int(bot_channel))
            bot_count = len([m for m in ctx.guild.members if m.bot])
            if not bot_channel_obj.name[11:] == str(bot_count):
                await bot_channel_obj.edit(name = f'Bot Count: {int(bot_count)}')
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        await asyncio.sleep(60)
        await self.update_stats(member)
    
    @commands.Cog.listener()
    async def on_member_leave(self, member):
        await asyncio.sleep(60)
        await self.update_stats(member)
    
    @commands.group()
    async def stats(self, ctx):
        if ctx.invoked_subcommand is None:
            pass
    
    
    @stats.command(name='update')
    async def stats_force_update(self, ctx):
        prefix = await db.pool.get_prefix(ctx.guild.id)
        await self.update_stats(ctx)
        if updated_something:
            await ctx.send("Stats updated!")
        else:
            raise errors.ConfigNotSet(f"You have not set any stats channels!\nDo this with the `{prefix}config` command")



def setup(bot):
    bot.add_cog(StatsCog(bot))
    print('    Stats cog!')