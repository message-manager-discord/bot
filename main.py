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

import discord

from discord.ext import commands

import config

from src import checks, errors
from src.db import db

starttime = datetime.datetime.utcnow()

__version__ = "v1.2.0"


class Bot(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(
            command_prefix=self.get_prefix, case_insensitive=True, **kwargs
        )
        self.logger = kwargs.pop("logger")
        self.checks = kwargs.pop("checks")
        self.errors = kwargs.pop("errors")
        self.default_prefix = kwargs.pop("default_prefix")
        self.self_hosted = kwargs.pop("self_hosted")
        self.version = kwargs.pop("version")
        self.load_time = None

    async def get_prefix(self, message):
        prefix = await self.db.get_prefix(
            message.guild
        )  # Fetch current server prefix from database
        if message.guild is None:
            prefix = [prefix, ""]
        return commands.when_mentioned_or(*prefix)(self, message)


async def run():
    database = db.DatabasePool(config.uri, bot)
    await database._init()
    bot.db = database

    bot.start_time = starttime

    bot.remove_command("help")

    extensions = [
        "cogs.maincog",
        "cogs.messages",
        "cogs.admin",
        "cogs.stats",
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

    try:
        await bot.start(config.token)
    except KeyboardInterrupt:
        await database.close()
        await bot.logout()


logging.basicConfig(filename="discord.log", filemode="w", level=logging.INFO)

logging.info("Started logging!")

intents = discord.Intents(guilds=True, members=False, messages=True)

bot = Bot(
    owner_ids=config.owners,
    activity=discord.Game(name="Watching our important messages!"),
    intents=intents,
    logger=logging,
    checks=checks,
    errors=errors,
    default_prefix=config.default_prefix,
    self_hosted=config.self_host,
    version=__version__,
)
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
