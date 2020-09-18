import discord, asyncio
from discord.ext import commands, tasks
from src import helpers


class StatsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot 
        self.stats_update_loop.start()

    def cog_check(self, ctx):
        return self.bot.checks.check_if_manage_role(self.bot, ctx)
    
    async def cog_command_error(self, ctx, error):
        if isinstance(error, (
            self.bot.errors.MissingPermission,
            self.bot.errors.ContentError,
            self.bot.errors.ConfigNotSet
        )):
            await ctx.send(error)
        elif isinstance(error, commands.CommandOnCooldown):
            mins = int(error.retry_after / 60)
            sec = int(error.retry_after % 60)
            await ctx.send(f'That command is on cool down for another {mins} minutes and {sec} seconds!\n{error.retry_after}')
        else:
            raise error

    async def cog_unload(self):
        self.stats_update_loop.cancel()
    
    async def update_stats(self, guild):
        print(1)
        member_true = False
        bot_true = False
        pool = self.bot.db
        member_channel = await pool.get_member_channel(guild.id)
        bot_channel = await pool.get_bot_channel(guild.id)
        if member_channel is not None:
            member_true = True
            print(2)
            member_channel_obj = self.bot.get_channel(int(member_channel))
            print(member_channel_obj.name[:12])
            member_count = len([m for m in guild.members if not m.bot])
            if not member_channel_obj.name[12:] == str(member_count):
                print(3)
                try:
                    await member_channel_obj.edit(name = f'User Count: {int(member_count)}')
                    print(4)
                except Exception as a:
                    print(5)
                    print(e)
                    pass
        
        if bot_channel is not None:
            bot_true = True
            print(6)
            bot_channel_obj = self.bot.get_channel(int(bot_channel))
            bot_count = len([m for m in guild.members if m.bot])
            if not bot_channel_obj.name[11:] == str(bot_count):
                print(7)
                try:
                    print(8)
                    await bot_channel_obj.edit(name = f'Bot Count: {int(bot_count)}')
                except discord.errors.Forbidden:
                    print(9)
                    pass
        return member_true or bot_true
    
    
    @commands.group()
    async def stats(self, ctx):
        if ctx.invoked_subcommand is None:
            pass
    
    
    @stats.command(name='update')
    @commands.cooldown(1, 600, commands.BucketType.guild)
    async def stats_force_update(self, ctx):
        pool = self.bot.db
        prefix = await pool.get_prefix(ctx.guild.id)
        updated = await self.update_stats(ctx.guild)
        print(updated)
        print(1)
        if updated:
            await ctx.send("Stats updated!")
        else:
            raise self.bot.errors.ConfigNotSet(f"You have not set any stats channels!\nDo this with the `{prefix}config` command")
    
    @tasks.loop(minutes=30)
    async def stats_update_loop(self):
        for guild in self.bot.guilds:
            await self.update_stats(guild)
    
    @stats_update_loop.before_loop
    async def before_stats_update_loop(self):
        await self.bot.wait_until_ready()



def setup(bot):
    bot.add_cog(StatsCog(bot))
    print('    Stats cog!')