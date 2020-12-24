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

import asyncio
import datetime
import logging

from typing import TYPE_CHECKING, Any, List

import asyncpg
import discord

from discord.ext import commands
from discord_slash.client import SlashCommand

import config

from cogs.src.db import db

starttime = datetime.datetime.utcnow()

__version__ = "v1.3.1"

if TYPE_CHECKING:
    BotBase = commands.Bot[commands.Context]
else:
    BotBase = commands.Bot


class Bot(BotBase):
    def __init__(
        self, default_prefix: str, self_hosted: bool = False, **kwargs: Any
    ) -> None:
        super().__init__(case_insensitive=True, **kwargs)
        self.default_prefix = default_prefix
        self.self_hosted = self_hosted
        self.version = __version__
        self.db: asyncpg.pool.Pool
        self.start_time: datetime.datetime
        self.load_time: datetime.datetime
        self.join_log_channel: int
        self.dbl_token: str
        self.dboats_token: str
        self.del_token: str
        self.dbgg_token: str
        self.topgg_token: str
        self.slash: SlashCommand

    def command_with_prefix(self, ctx: commands.Context, command_name: str) -> str:
        if str(self.user.id) in ctx.prefix:
            if isinstance(ctx.me, discord.Member):
                return f"`@{ctx.me.nick or ctx.me.name} {command_name}`"
            else:
                return f"`@{ctx.me.name} {command_name}`"
        else:
            return f"`{ctx.prefix}{command_name}`"


async def run() -> None:
    database = db.DatabasePool(config.uri, bot)
    await database._init()
    bot.db = database

    bot.start_time = starttime

    bot.remove_command("help")

    extensions = [
        "cogs.maincog",
        "cogs.messages",
        "cogs.stats",
        "cogs.admin",
        "cogs.setup",
        "cogs.slash_cmds",
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

    try:
        await bot.start(config.token)
    except KeyboardInterrupt:
        await database.close()
        await bot.logout()


logging.basicConfig(filename="discord.log", filemode="w", level=logging.INFO)

logging.info("Started logging!")

intents = discord.Intents(guilds=True, members=False, messages=True)


async def get_prefix(bot: Bot, message: discord.Message) -> List[str]:
    prefix = await bot.db.get_prefix(
        message.guild
    )  # Fetch current server prefix from database
    if message.guild is None:
        prefix = [prefix, ""]

    return commands.when_mentioned_or(*prefix)(bot, message)


bot = Bot(
    owner_ids=config.owners,
    activity=discord.Game(name="Watching our important messages!"),
    intents=intents,
    default_prefix=config.default_prefix,
    self_hosted=config.self_host,
    command_prefix=get_prefix,
)
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
