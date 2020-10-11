import aiohttp


class Del:
    def __init__(self, token, bot):
        self.base_url = "https://api.discordextremelist.xyz/v2/"
        self.bot = bot
        self.token = token
        self.session = aiohttp.ClientSession(loop=bot.loop)

    async def _request(self, method, url, json):
        url = f"{self.base_url}{url}"
        headers = {"Authorization": self.token, "Content-Type": "application/json"}
        async with self.session.request(
            method=method, url=url, headers=headers, json=json
        ) as r:
            return r.status

    async def post_guild_stats(self):
        url = f"bot/{self.bot.user.id}/stats"
        guild_count = len(self.bot.guilds)
        payload = {"guildCount": guild_count}
        r = await self._request(url=url, method="POST", json=payload)


class Dbl:
    def __init__(self, token, bot):
        self.base_url = "https://discordbotlist.com/api/v1/"
        self.bot = bot
        self.token = token
        self.session = aiohttp.ClientSession(loop=bot.loop)

    async def _request(self, method, url, json):
        url = f"{self.base_url}{url}"
        headers = {"Authorization": self.token, "Content-Type": "application/json"}
        async with self.session.request(
            method=method, url=url, headers=headers, json=json
        ) as r:
            return r.status

    async def post_guild_stats(self):
        url = f"/bots/{self.bot.user.id}/stats"
        guild_count = len(self.bot.guilds)
        payload = {"guilds": guild_count}
        r = await self._request(url=url, method="POST", json=payload)


class DBoats:
    def __init__(self, token, bot):
        self.base_url = "https://discord.boats/api/"
        self.bot = bot
        self.token = token
        self.session = aiohttp.ClientSession(loop=bot.loop)

    async def _request(self, method, url, json):
        url = f"{self.base_url}{url}"
        headers = {"Authorization": self.token, "Content-Type": "application/json"}
        async with self.session.request(
            method=method, url=url, headers=headers, json=json
        ) as r:
            return r.status

    async def post_guild_stats(self):
        url = f"bot/{self.bot.user.id}"
        guild_count = len(self.bot.guilds)
        payload = {"server_count": guild_count}
        r = await self._request(url=url, method="POST", json=payload)
        print(r)
