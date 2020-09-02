import discord, asyncio
from discord.ext import commands
from src import helpers, checks

member_channel = helpers.fetch_config('member_channel')
bot_channel = helpers.fetch_config('bot_channel')

class StatsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot 
    
    async def update_stats(self, ctx):
        member_channel_obj = self.bot.get_channel(int(member_channel))
        bot_channel_obj = self.bot.get_channel(int(bot_channel))
        member_count = len([m for m in ctx.guild.members if not m.bot])
        bot_count = len([m for m in ctx.guild.members if m.bot])
        if not member_channel_obj.name[12:] == str(member_count):
            await member_channel_obj.edit(name = f'User Count: {int(member_count)}')
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
    
    @commands.command(name='stats-force-update')
    async def stats_force_update(self, ctx):
        await self.update_stats(ctx)
        await ctx.send("Stats updated!")



def setup(bot):
    bot.add_cog(StatsCog(bot))