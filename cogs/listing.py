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
    
    @tasks.loop(minutes=30)
    async def stats_post_loop(self):
        await self.bot.wait_until_ready()
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url = f'https://discordbotlist.com/api/v1/bots/{self.bot.user.id}/stats',
                headers = {
                    'Authorization' : self.bot.dbl_token,
                    'Content-Type' : 'application/json'
                },
                json = {
                    'guilds' : len(self.bot.guilds)
                }
            ) as r:
                returned = await r.json()
                if not returned['success']:
                    print('Posting to discordbotlist.com failed!')
                else:
                    print('Posting to discordbotlist.com successful!')
        
        """
        Not currently approved on discord boats
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url = f'https://discord.boats/api/bot/{self.bot.user.id}',
                headers = {
                    'Authorization' : self.bot.dboats_token,
                    'Content-Type' : 'application/json'
                },
                json = {
                    'server_count' : len(self.bot.guilds)
                }
            ) as r:
                returned = await r.json()
                if returned['error']:
                    print('Posting to discord.boats failed!' +returned['message'])
                else:
                    print('Posting to discord.boats successful!')""" 
        


def setup(bot):
    bot.add_cog(ListingCog(bot))
    print('    Listing cog!')