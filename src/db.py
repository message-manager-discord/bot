import asyncpg

from src import helpers
from config import default_prefix

create_db = """CREATE TABLE IF NOT EXISTS servers (
    server_id bigint NOT NULL UNIQUE,
    management_role_id bigint,
    prefix VARCHAR(3) DEFAULT '~',
    bot_channel bigint,
    member_channel bigint
);"""

async def create_pool(uri):
    pool = DatabasePool(uri)
    await pool._init()
    return pool

class DatabasePool():
    def __init__(self, uri):
        self.pool = None
        self.uri = uri

    async def _init(self):
        await self._create_pool(self.uri)
        await self._create_tables()

    async def _create_pool(self, uri):
        self.pool = await asyncpg.create_pool(dsn=uri)

    async def _create_tables(self):
        conn = await self.pool.acquire()
        await conn.execute(create_db)

    async def get_prefix(self, server_id):
        conn = await self.pool.acquire()
        prefix = await conn.fetch(
            """
            SELECT prefix 
            FROM servers 
            WHERE server_id=$1
            """,
            server_id
        )
        if prefix == []:
            return default_prefix
        prefix = prefix[0].get('prefix')
        if prefix is None:
            return default_prefix
        else:
            return prefix

    async def get_member_channel(self, server_id):
        conn = await self.pool.acquire()
        member_channel = await conn.fetch(
            """
            SELECT member_channel 
            FROM servers 
            WHERE server_id=$1
            """,
            server_id
        )
        if member_channel == []:
            return None
        return member_channel[0].get('member_channel')

    async def get_bot_channel(self, server_id):
        conn = await self.pool.acquire()
        bot_channel = await conn.fetch(
            """
            SELECT bot_channel 
            FROM servers 
            WHERE server_id=$1
            """,
            server_id
        )
        if bot_channel == []:
            return None
        return bot_channel[0].get('bot_channel')
    
    async def get_management_role(self, server_id):
        conn = await self.pool.acquire()
        management_role = await conn.fetch(
            """
            SELECT management_role_id
            FROM servers 
            WHERE server_id=$1
            """,
            server_id
        )
        if management_role == []:
            return None
        return management_role[0].get('management_role_id')

    async def update_prefix(self, server_id, prefix):
        conn = await self.pool.acquire()
        await conn.execute(
            """
            INSERT INTO servers 
                (server_id, prefix)
                VALUES($1, $2)
                ON CONFLICT (server_id)
                DO UPDATE SET prefix = $2;
            """, server_id, prefix
        )

    async def update_admin_role(self, server_id, role_id):
        conn = await self.pool.acquire()
        await conn.execute(
            """
            INSERT INTO servers 
                (server_id, management_role_id)
                VALUES($1, $2)
                ON CONFLICT (server_id)
                DO UPDATE SET management_role_id = $2;
            """, server_id, role_id
        )
    
    async def update_bot_channel(self, server_id, channel_id):
        conn = await self.pool.acquire()
        await conn.execute(
            """
            INSERT INTO servers 
                (server_id, bot_channel)
                VALUES($1, $2)
                ON CONFLICT (server_id)
                DO UPDATE SET bot_channel = $2;
            """, server_id, channel_id
        )

    async def update_user_channel(self, server_id, channel_id):
        conn = await self.pool.acquire()
        await conn.execute(
            """
            INSERT INTO servers 
                (server_id, member_channel)
                VALUES($1, $2)
                ON CONFLICT (server_id)
                DO UPDATE SET member_channel = $2;
            """, server_id, channel_id
        )

async def start_pool(uri):
    global pool
    pool = await create_pool(uri)

def setup(bot):
    print('    Database module!')