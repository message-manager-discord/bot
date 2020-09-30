import discord
import aiohttp
import json
from discord.ext import commands, tasks

class ListingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot 
        self.stats_post_loop.start()

    def cog_unload(self):
        self.stats_post_loop.cancel()

    async def post_guild_stats(
        self,
        session,
        url,
        name_of_param,
        token,
        error_name,
        expected_returned_value):
        async with session.post(
            url = url,
            headers = {
                'Authorization' : token,
                'Content-Type' : 'application/json'
            },
            json = {
                name_of_param : len(self.bot.guilds)
            }
        ) as r:
            returned = await r.json()
            if not returned[error_name] is expected_returned_value:
                print(f'Error posting to {url}\n{returned}')
            else:
                print(f'Posted to {url}\n{returned}')


    
    @tasks.loop(minutes=30)
    async def stats_post_loop(self):
        await self.bot.wait_until_ready()
        async with aiohttp.ClientSession() as session:
            await self.post_guild_stats(
                session,
                f'https://discordbotlist.com/api/v1/bots/{self.bot.user.id}/stats',
                'guilds',
                self.bot.dbl_token,
                'success',
                True
            )
            await self.post_guild_stats(
                session,
                f'https://discord.boats/api/bot/{self.bot.user.id}',
                'server_count',
                self.bot.dboats_token,
                'error',
                False
            )

            
            await self.post_guild_stats(
                session,
                f'https://api.discordextremelist.xyz/v2/bot/{self.bot.user.id}/stats',
                'guildCount',
                self.bot.del_token,
                'error',
                False
            )
            await self.post_guild_stats(
                session,
                f'https://discord.bots.gg/api/v1/bots/{self.bot.user.id}/stats',
                'guildCount',
                self.bot.dbgg_token,
                'guildCount',
                len(self.bot.guilds)

            )
        

def setup(bot):
    bot.add_cog(ListingCog(bot))
    print('    Listing cog!')