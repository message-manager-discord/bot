import asyncpg

from config import default_prefix
from config import uri as default_uri
from src.db.startup import init_db


async def create_pool(uri):
    pool = DatabasePool(uri)
    await pool._init()
    return pool


class DatabasePool:
    def __init__(self, uri):
        self.pool = None
        self.uri = uri

    async def _init(self):
        await self._create_pool(self.uri)
        await init_db(self.pool)

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

    async def get_member_channel(self, guild):
        async with self.pool.acquire() as conn:
            member_channel = await conn.fetch(
                """
                SELECT member_channel 
                FROM servers 
                WHERE server_id=$1
                """,
                guild.id,
            )
            if member_channel == []:
                return None
            return member_channel[0].get("member_channel")

    async def get_bot_channel(self, guild):
        async with self.pool.acquire() as conn:
            bot_channel = await conn.fetch(
                """
                SELECT bot_channel 
                FROM servers 
                WHERE server_id=$1
                """,
                guild.id,
            )
            if bot_channel == []:
                return None
            return bot_channel[0].get("bot_channel")

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

    async def update_bot_channel(self, guild, channel_id):
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO servers 
                    (server_id, bot_channel)
                    VALUES($1, $2)
                    ON CONFLICT (server_id)
                    DO UPDATE SET bot_channel = $2;
                """,
                guild.id,
                channel_id,
            )

    async def update_user_channel(self, guild, channel_id):
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO servers 
                    (server_id, member_channel)
                    VALUES($1, $2)
                    ON CONFLICT (server_id)
                    DO UPDATE SET member_channel = $2;
                """,
                guild.id,
                channel_id,
            )


def setup(bot):
    print("    Database module!")
