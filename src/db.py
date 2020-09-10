import asyncpg

from src import helpers


create_db = """CREATE TABLE IF NOT EXISTS servers (
    server_id INTEGER NOT NULL UNIQUE,
    management_role_id INTEGER,
    prefix VARCHAR(3) DEFAULT '~',
    bot_channel INTEGER,
    member_channel INTEGER
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
        print("tables created")