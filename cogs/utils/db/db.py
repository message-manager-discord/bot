# cogs/utils/db/db.py

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

from typing import TYPE_CHECKING, List, NamedTuple, Optional, Union

import asyncpg
import discord

from cogs.utils import errors
from cogs.utils.db.startup import init_db

if TYPE_CHECKING:
    from main import Bot
else:

    class Bot:
        pass


def process_guild_id(guild: Union[discord.Guild, int]) -> int:
    if isinstance(guild, discord.Guild):
        return guild.id
    else:
        return guild


class IncorrectVersion(Exception):
    pass


class LoggerTuple(NamedTuple):
    channel_id: int
    webhook_id: Optional[int]
    webhook_token: Optional[str]
    logger_type: str


class ChannelTuple(NamedTuple):
    id: int
    webhook_id: Optional[int]
    webhook_token: Optional[str]


class GuildTuple(NamedTuple):
    id: int
    management_role: Optional[int]
    prefix: str


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

    async def get_guild(self, guild: Union[discord.Guild, int]) -> GuildTuple:
        guild_id = process_guild_id(guild)
        async with self.pool.acquire() as conn:

            query = await conn.fetch(
                """
                SELECT *
                FROM servers
                WHERE id=$1
                """,
                guild_id,
            )
            if query == []:
                return GuildTuple(guild_id, None, self.bot.default_prefix)
            prefix: str = query[0].get("prefix")
            role: int = query[0].get("management_role_id")
            if prefix is None:
                prefix = self.bot.default_prefix
            return GuildTuple(guild_id, role, prefix)

    async def update_prefix(
        self, guild: Union[discord.Guild, int], prefix: str
    ) -> None:
        guild_id = process_guild_id(guild)
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO servers
                    (id, prefix)
                    VALUES($1, $2)
                    ON CONFLICT (id)
                    DO UPDATE SET prefix = $2;
                """,
                guild_id,
                prefix,
            )

    async def update_admin_role(
        self, guild: Union[discord.Guild, int], role_id: Optional[int]
    ) -> None:
        guild_id = process_guild_id(guild)
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO servers
                    (id, management_role_id)
                    VALUES($1, $2)
                    ON CONFLICT (id)
                    DO UPDATE SET management_role_id = $2;
                """,
                guild_id,
                role_id,
            )

    async def get_loggers(
        self, guild: Union[discord.Guild, int]
    ) -> Optional[List[LoggerTuple]]:
        guild_id = process_guild_id(guild)
        async with self.pool.acquire() as conn:
            loggers_query = await conn.fetch(
                """
                SELECT channels.id AS channel_id, channels.webhook_id, channels.webhook_token, logging_channels.logger_type
                FROM logging_channels
                INNER JOIN channels ON channels.id = logging_channels.channel_id
                WHERE logging_channels.guild_id = $1;
                """,
                guild_id,
            )

            if len(loggers_query) == 0:
                return None
            else:
                loggers: List[LoggerTuple] = []
                for logger in loggers_query:
                    logger_tuple = LoggerTuple(
                        channel_id=logger.get("channel_id"),
                        webhook_id=logger.get("webhook_id"),
                        webhook_token=logger.get("webhook_token"),
                        logger_type=logger.get("logger_type"),
                    )
                    loggers.append(logger_tuple)
                return loggers

    async def get_logger(
        self, guild: Union[discord.Guild, int], logger_type: str
    ) -> Optional[LoggerTuple]:
        guild_id = process_guild_id(guild)
        async with self.pool.acquire() as conn:
            loggers_query = await conn.fetch(
                """
                SELECT channels.id AS channel_id, channels.webhook_id, channels.webhook_token, logging_channels.logger_type
                FROM logging_channels
                INNER JOIN channels ON channels.id = logging_channels.channel_id
                WHERE logging_channels.guild_id = $1 AND logging_channels.logger_type = $2;
                """,
                guild_id,
                logger_type,
            )

            if len(loggers_query) == 0:
                return None
            if len(loggers_query) == 1:
                logger_data = loggers_query[0]
                return LoggerTuple(
                    channel_id=logger_data.get("channel_id"),
                    webhook_id=logger_data.get("webhook_id"),
                    webhook_token=logger_data.get("webhook_token"),
                    logger_type=logger_data.get("logger_type"),
                )
            else:
                raise errors.DatabaseError(
                    "Internal error occurred, please contact the devs\n"
                    "Error: More than one logger when returning 'main' logger"
                )

    async def remove_logger(
        self, guild: Union[discord.Guild, int], logger_type: str
    ) -> None:
        guild_id = process_guild_id(guild)
        async with self.pool.acquire() as conn:
            await conn.execute(
                "DELETE FROM logging_channels WHERE guild_id = $1 AND logger_type = $2",
                guild_id,
                logger_type,
            )

    async def update_logger(
        self, guild: Union[discord.Guild, int], channel_id: int, logger_type: str
    ) -> None:
        guild_id = process_guild_id(guild)
        loggers = await self.get_loggers(guild)
        if isinstance(loggers, LoggerTuple):
            loggers = [loggers]
        existing_channel = await self.get_channel(channel_id)
        if existing_channel is None:
            await self.update_channel(channel_id)
        async with self.pool.acquire() as conn:
            guild_stored = await conn.fetch(
                "SELECT id FROM servers WHERE id = $1", guild_id
            )
            if len(guild_stored) == 0:
                await conn.execute(
                    """
                INSERT INTO servers
                (id)
                VALUES ($1)""",
                    guild_id,
                )

            if loggers is not None:
                for logger in loggers:
                    if logger.logger_type == logger_type:
                        if logger.channel_id != channel_id:  # if channel changed
                            await conn.execute(
                                """
                                UPDATE logging_channels
                                SET channel_id = $1
                                WHERE guild_id = $2 AND logger_type = $3;
                            """,
                                channel_id,
                                guild_id,
                                logger_type,
                            )
                            return
                        else:
                            return
            # If still executing the new type was not in the existing loggers
            await conn.execute(
                """
            INSERT INTO logging_channels
            (guild_id, channel_id, logger_type)
            VALUES ($1, $2, $3);""",
                guild_id,
                channel_id,
                logger_type,
            )

    async def get_channel(self, channel_id: int) -> Optional[ChannelTuple]:
        async with self.pool.acquire() as conn:
            channel_query = await conn.fetch(
                "SELECT * FROM channels WHERE id = $1", channel_id
            )
            if len(channel_query) == 0:
                return None
            elif len(channel_query) > 1:
                raise errors.DatabaseError()
            else:
                channel = channel_query[0]
                channel_tuple = ChannelTuple(
                    id=channel.get("id"),
                    webhook_id=channel.get("webhook_id"),
                    webhook_token=channel.get("webhook_token"),
                )
                return channel_tuple

    async def update_channel(
        self,
        channel_id: int,
        wipe: bool = False,
        webhook_id: Optional[int] = None,
        webhook_token: Optional[str] = None,
    ) -> None:
        if (webhook_token is None or webhook_id is None) and not (
            webhook_token is None and webhook_id is None
        ):
            raise errors.DatabaseError(
                "Both webhook_id and webhook_token need to be set!"
            )
        async with self.pool.acquire() as conn:
            existing_channel = await self.get_channel(channel_id)
            if existing_channel is None:
                await conn.execute(
                    """
                INSERT INTO channels
                (id, webhook_token, webhook_id)
                VALUES ($1, $2, $3);""",
                    channel_id,
                    webhook_token,
                    webhook_id,
                )
            else:
                if wipe:
                    await conn.execute(
                        """
                    UPDATE channels
                    SET webhook_token = $1, webhook_id = $2
                    WHERE id = $3;""",
                        webhook_token,
                        webhook_id,
                        channel_id,
                    )
                else:
                    if webhook_token is None and webhook_id is None:
                        pass
                    else:
                        existing_webhook_token = existing_channel.webhook_token
                        existing_webhook_id = existing_channel.webhook_id
                        if (
                            existing_webhook_token == webhook_token
                            and existing_webhook_id == webhook_id
                        ):
                            pass
                        else:
                            raise errors.DatabaseError(
                                "Webhook token and id were passed but wipe was false!"
                            )
