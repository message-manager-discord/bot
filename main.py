# main.py
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

import datetime
import logging

from typing import TYPE_CHECKING, Any, List

import aiohttp
import discord

from discord.ext import commands
from discord_slash.client import SlashCommand

import config

from cogs.utils import Context, PartialGuildCache
from cogs.utils.db import db

__version__ = "v1.5.1"

if TYPE_CHECKING:
    BotBase = commands.Bot[Context]
else:
    BotBase = commands.Bot


class Bot(BotBase):
    def __init__(
        self, default_prefix: str, self_hosted: bool = False, **kwargs: Any
    ) -> None:

        super().__init__(
            case_insensitive=True,
            chunk_guilds_on_startup=False,
            intents=discord.Intents(guilds=True, members=False, messages=True),
            activity=discord.Game(name="Watching our important messages!"),
            help_command=None,
            **kwargs,
        )
        self.default_prefix = default_prefix
        self.self_hosted = self_hosted
        self.start_time = datetime.datetime.utcnow()
        self.session: aiohttp.ClientSession
        self.version = __version__
        self.db: db.DatabasePool
        self.guild_cache: PartialGuildCache
        self.load_time: datetime.datetime
        self.join_log_channel: int
        self.dbl_token: str
        self.dboats_token: str
        self.del_token: str
        self.dbgg_token: str
        self.topgg_token: str
        SlashCommand(self, sync_commands=True)

    async def init_db(self) -> None:
        database = db.DatabasePool(config.uri, self)
        await database._init()
        self.db = database
        self.guild_cache = PartialGuildCache(
            capacity=config.guild_cache_max,
            db=self.db,
            drop_amount=config.guild_cache_drop,
        )

    async def start(self, *args, **kwargs) -> None:  # type: ignore
        self.session = aiohttp.ClientSession()
        await self.init_db()
        await super().start(*args, **kwargs)

    async def close(self) -> None:
        await self.db.close()
        await super().close()

    def command_with_prefix(self, ctx: Context, command_name: str) -> str:
        if str(self.user.id) in ctx.prefix:
            if isinstance(ctx.me, discord.Member):
                return f"`@{ctx.me.nick or ctx.me.name} {command_name}`"
            else:
                return f"`@{ctx.me.name} {command_name}`"
        else:
            return f"`{ctx.prefix}{command_name}`"

    async def process_commands(self, message: discord.Message) -> None:
        if message.author.bot:
            return
        ctx = await self.get_context(message, cls=Context)
        if ctx.command is None:
            return
        if message.guild is not None:
            await ctx.fetch_guild_data()
        await self.invoke(ctx)


logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
handler.setFormatter(
    logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
)
logger.addHandler(handler)


async def get_custom_prefix(bot: Bot, message: discord.Message) -> List[str]:

    if message.guild is not None:
        guild = await bot.guild_cache.get(
            message.guild.id
        )  # Fetch current server prefix from database
        prefix = [guild.prefix]
    else:
        prefix = [config.default_prefix, ""]

    return commands.when_mentioned_or(*prefix)(bot, message)


def run() -> None:
    bot = Bot(
        owner_ids=config.owners,
        default_prefix=config.default_prefix,
        self_hosted=config.self_host,
        command_prefix=get_custom_prefix,
    )

    extensions = [
        "cogs.maincog",
        "cogs.messages",
        "cogs.stats",
        "cogs.admin",
        "cogs.setup",
    ]
    if not config.self_host:
        bot.join_log_channel = config.join_logs
        bot.dbl_token = config.dbl_token
        bot.dboats_token = config.dboats_token
        bot.del_token = config.def_token
        bot.dbgg_token = config.dbgg_token
        bot.topgg_token = config.topgg_token
        extensions.append("jishaku")
        extensions.append("cogs.listing")
    print("Loading extensions...")
    for extension in extensions:
        bot.load_extension(extension)
    bot.run(config.token)


if __name__ == "__main__":
    run()
