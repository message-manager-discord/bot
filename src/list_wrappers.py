import aiohttp


class HttpClient:
    def __init__(self, bot, **kwargs):
        self.token = kwargs.pop("token")
        self.session = kwargs.get("session") or aiohttp.ClientSession(loop=bot.loop)

    async def _request(self, method, url, json):
        url = f"{self.base_url}{url}"
        headers = {"Authorization": self.token, "Content-Type": "application/json"}
        async with self.session.request(
            method=method, url=url, headers=headers, json=json
        ) as r:
            return r.status


class Del(HttpClient):
    def __init__(self, bot, **kwargs):
        self.base_url = "https://api.discordextremelist.xyz/v2/"
        self.bot = bot
        super().__init__(bot, **kwargs)

    async def post_guild_stats(self):
        url = f"bot/{self.bot.user.id}/stats"
        guild_count = len(self.bot.guilds)
        payload = {"guildCount": guild_count}
        r = await self._request(url=url, method="POST", json=payload)


class Dbl(HttpClient):
    def __init__(self, bot, **kwargs):
        self.base_url = "https://discordbotlist.com/api/v1/"
        self.bot = bot
        super().__init__(bot, **kwargs)

    async def post_guild_stats(self):
        url = f"/bots/{self.bot.user.id}/stats"
        guild_count = len(self.bot.guilds)
        payload = {"guilds": guild_count}
        r = await self._request(url=url, method="POST", json=payload)


class DBoats(HttpClient):
    def __init__(self, bot, **kwargs):
        self.base_url = "https://discord.boats/api/"
        self.bot = bot
        super().__init__(bot, **kwargs)

    async def post_guild_stats(self):
        url = f"bot/{self.bot.user.id}"
        guild_count = len(self.bot.guilds)
        payload = {"server_count": guild_count}
        r = await self._request(url=url, method="POST", json=payload)


class Dbgg(HttpClient):
    def __init__(self, bot, **kwargs):
        self.base_url = "https://discord.bots.gg/api/v1/"
        self.bot = bot
        super().__init__(bot, **kwargs)

    async def post_guild_stats(self):
        url = f"bots/{self.bot.user.id}/stats"
        guild_count = len(self.bot.guilds)
        payload = {"guildCount": guild_count}
        r = await self._request(url=url, method="POST", json=payload)
