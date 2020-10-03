import aiohttp


class Del:
    def __init__(self, token, bot):
        self.base_url = "https://api.discordextremelist.xyz/v2"
        self.bot = bot
        self.token = token
        self.session = aiohttp.ClientSession(loop=bot.loop)

    async def _request(self, method, url, **kwargs):
        url = f"{self.base_url}{url}"
        headers = {"Authorization": self.token, "Content-Type": "application/json"}
        async with session.request(
            method=method, url=url, headers=headers, **kwargs
        ) as r:
            return r.status

    async def post_guild_stats(self):
        url = f"bots/{self.bot.user.id}/stats"
        guild_count = len(self.bot.guilds)
        payload = {"guildCount": guild_count}
        await self._request(url=url, method="POST", json=payload)
