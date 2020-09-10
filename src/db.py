import asyncpg

from src import helpers



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
        prefix = await conn.fetch("SELECT prefix FROM servers WHERE server_id=$1", server_id)
        return prefix[0].get('prefix')

async def start_pool(uri):
    global pool
    pool = await create_pool(uri)

def return_pool():
    return pool