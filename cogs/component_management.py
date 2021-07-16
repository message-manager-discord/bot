# cogs/component_management.py

"""
Message Manager - A bot for discord
Copyright (C) 2020-2021 AnotherCat

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

import logging

from typing import TYPE_CHECKING

from discord.ext import commands, tasks

from main import Bot
from src import Context

if TYPE_CHECKING:
    Cog = commands.Cog[Context]
else:
    Cog = commands.Cog


class ComponentChecking(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.check_components.start()

    def cog_unload(self) -> None:
        self.check_components.cancel()

    @tasks.loop(minutes=120)
    async def check_components(self) -> None:
        logging.debug(f"Checking component listeners: {self.bot.component_listeners}")
        await self.bot.clean_component_listeners()
        logging.debug(f"Finished checking: {self.bot.component_listeners}")


def setup(bot: Bot) -> None:
    bot.add_cog(ComponentChecking(bot))
    print("    Listing cog!")
