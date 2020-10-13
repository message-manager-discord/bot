import json

import aiohttp
import discord

from discord.ext import commands, tasks

from src import list_wrappers


class ListingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.stats_post_loop.start()
        self.session = aiohttp.ClientSession(loop=bot.loop)
        self.de_list = list_wrappers.Del(
            token=self.bot.del_token, bot=self.bot, session=self.session
        )
        self.dbl = list_wrappers.Dbl(
            token=self.bot.dbl_token, bot=self.bot, session=self.session
        )
        self.dboats = list_wrappers.DBoats(
            token=self.bot.dboats_token, bot=self.bot, session=self.session
        )
        self.dbgg = list_wrappers.Dbgg(
            token=self.bot.dbgg_token, bot=self.bot, session=self.session
        )

    def cog_unload(self):
        self.stats_post_loop.cancel()

    @tasks.loop(minutes=30)
    async def stats_post_loop(self):
        await self.bot.wait_until_ready()
        await self.de_list.post_guild_stats()
        await self.dbl.post_guild_stats()
        await self.dboats.post_guild_stats()
        await self.dbgg.post_guild_stats()


def setup(bot):
    bot.add_cog(ListingCog(bot))
    print("    Listing cog!")
