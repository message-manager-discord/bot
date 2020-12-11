# cogs/src/db/db.py

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

from typing import Optional, Union

import asyncpg
import discord

from cogs.src.db.startup import init_db
from main import Bot


class IncorrectVersion(Exception):
    pass


class DatabasePool:
    def __init__(self, uri: str, bot: Bot):
        self.pool: asyncpg.pool.Pool = None
        self.uri = uri
        self.bot = bot

    async def _init(self) -> None:
        await self._create_pool(self.uri)
        await init_db(self.pool)
        await self._check_version()

    async def _check_version(self) -> None:
        async with self.pool.acquire() as conn:
            version = await conn.fetch(
                """
                        SELECT version
                        FROM version;
                        """
            )
            version = version[0].get("version")
            if self.bot.version != version:
                raise IncorrectVersion(
                    f"Bot version {self.bot.version}, but database version {version}!"
                )

    async def _create_pool(self, uri: str) -> None:
        self.pool = await asyncpg.create_pool(dsn=uri)

    async def close(self) -> None:
        await self.pool.close()

    async def get_prefix(self, guild: discord.Guild) -> str:
        if guild is None:
            return self.bot.default_prefix
        async with self.pool.acquire() as conn:

            prefix_query = await conn.fetch(
                """
                SELECT prefix
                FROM servers
                WHERE server_id=$1
                """,
                guild.id,
            )
            if prefix_query == []:
                return self.bot.default_prefix
            prefix: str = prefix_query[0].get("prefix")
            if prefix is None:
                return self.bot.default_prefix
            else:
                return prefix

    async def get_management_role(
        self, guild: discord.Guild
    ) -> Optional[Union[int, None]]:
        async with self.pool.acquire() as conn:
            management_role_query = await conn.fetch(
                """
                SELECT management_role_id
                FROM servers
                WHERE server_id=$1
                """,
                guild.id,
            )
            if management_role_query == []:
                return None
            management_role: int = management_role_query[0].get("management_role_id")
            return management_role

    async def update_prefix(self, guild: discord.Guild, prefix: str) -> None:
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO servers
                    (server_id, prefix)
                    VALUES($1, $2)
                    ON CONFLICT (server_id)
                    DO UPDATE SET prefix = $2;
                """,
                guild.id,
                prefix,
            )

    async def update_admin_role(self, guild: discord.Guild, role_id: int) -> None:
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO servers
                    (server_id, management_role_id)
                    VALUES($1, $2)
                    ON CONFLICT (server_id)
                    DO UPDATE SET management_role_id = $2;
                """,
                guild.id,
                role_id,
            )
