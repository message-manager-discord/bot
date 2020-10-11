import discord
import aiohttp
import json
from discord.ext import commands, tasks
from src import list_wrappers


class ListingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.stats_post_loop.start()
        self.de_list = list_wrappers.Del(self.bot.del_token, self.bot)
        self.dbl = list_wrappers.Dbl(self.bot.dbl_token, self.bot)
        self.dboats = list_wrappers.DBoats(self.bot.dboats_token, self.bot)

    def cog_unload(self):
        self.stats_post_loop.cancel()

    async def post_guild_stats(
        self, session, url, name_of_param, token, error_name, expected_returned_value
    ):
        async with session.post(
            url=url,
            headers={"Authorization": token, "Content-Type": "application/json"},
            json={name_of_param: len(self.bot.guilds)},
        ) as r:
            returned = await r.json()
            try:
                if not returned[error_name] is expected_returned_value:
                    print(f"Error posting to {url}\nError:\n\n{returned}\n")
                else:
                    print(f"Posted to {url}\n{returned}\n")
            except Exception as e:
                print(
                    f"An error has occured in posting to {url}!\nError:\n\n"
                    + str(e)
                    + f"\n\nReturned data:\n{returned}"
                )

    @tasks.loop(minutes=30)
    async def stats_post_loop(self):
        await self.bot.wait_until_ready()
        await self.de_list.post_guild_stats()
        await self.dbl.post_guild_stats()
        await self.dboats.post_guild_stats()
        async with aiohttp.ClientSession() as session:

            await self.post_guild_stats(
                session,
                f"https://discord.bots.gg/api/v1/bots/{self.bot.user.id}/stats",
                "guildCount",
                self.bot.dbgg_token,
                "guildCount",
                len(self.bot.guilds),
            )


def setup(bot):
    bot.add_cog(ListingCog(bot))
    print("    Listing cog!")
