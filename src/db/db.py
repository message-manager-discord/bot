# src/db/db.py

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

import asyncpg

from config import default_prefix
from config import uri as default_uri
from src.db.startup import init_db


class IncorrectVersion(Exception):
    pass


class DatabasePool:
    def __init__(self, uri, bot):
        self.pool = None
        self.uri = uri
        self.bot = bot

    async def _init(self):
        await self._create_pool(self.uri)
        await init_db(self.pool)
        await self._check_version()

    async def _check_version(self):
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
                await self.bot.logout()

    async def _create_pool(self, uri):
        self.pool = await asyncpg.create_pool(dsn=uri)

    async def close(self):
        await self.pool.close()

    async def get_prefix(self, guild):
        if guild is None:
            return default_prefix
        async with self.pool.acquire() as conn:

            prefix = await conn.fetch(
                """
                SELECT prefix 
                FROM servers 
                WHERE server_id=$1
                """,
                guild.id,
            )
            if prefix == []:
                return default_prefix
            prefix = prefix[0].get("prefix")
            if prefix is None:
                return default_prefix
            else:
                return prefix

    async def get_management_role(self, guild):
        async with self.pool.acquire() as conn:
            management_role = await conn.fetch(
                """
                SELECT management_role_id
                FROM servers 
                WHERE server_id=$1
                """,
                guild.id,
            )
            if management_role == []:
                return None
            return management_role[0].get("management_role_id")

    async def update_prefix(self, guild, prefix):
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

    async def update_admin_role(self, guild, role_id):
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
