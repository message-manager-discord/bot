# cogs/utils/context.py
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

from typing import TYPE_CHECKING, Any, Dict, Optional

from discord.ext import commands

if TYPE_CHECKING:
    from cogs.utils.db.db import GuildTuple
    from main import Bot
else:
    # Avoid circlar imports
    Bot = None
    GuildTuple = None


class Context(commands.Context):
    bot: Bot

    def __init__(self, **kwargs: Dict[str, Any]) -> None:
        super().__init__(**kwargs)  # type: ignore
        self.guild_cache = self.bot.guild_cache
        self.guild_data: Optional[GuildTuple] = None

    async def fetch_guild_data(self) -> Optional[GuildTuple]:
        if self.guild is None:
            return None
        else:
            self.guild_data = await self.guild_cache.get(self.guild.id)
            return self.guild_data
