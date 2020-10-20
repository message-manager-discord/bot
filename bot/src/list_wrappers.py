# src/list_wrappers.py

"""
Message Manager - A bot for discord
Copyright (C) 2020  AnotherCat

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

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
