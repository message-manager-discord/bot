import asyncio

import asyncpg

# This file is to create, and maintain databases
# It will check if the tables are created, if not create them
# Also the version number is stored in it's own table
# If the bot gets updated then this is bumped along with any queries to update the tables
# SQL queries will not be changed, only added to with each version

queries = {
    "v0.0.0": {
        "query": """CREATE TABLE IF NOT EXISTS version (
        id INT,
        version VARCHAR(18)
        );
        INSERT INTO version VALUES(0, 'v1.0.0');
        """,
        "new_version": "v1.0.0",
    },
    "v1.0.0": None,
}

create_db = """
    CREATE TABLE IF NOT EXISTS servers (
        server_id bigint NOT NULL UNIQUE,
        management_role_id bigint,
        prefix VARCHAR(3) DEFAULT '~',
        bot_channel bigint,
        member_channel bigint
    );
"""


async def init_db(pool):
    async with pool.acquire() as conn:
        await conn.execute(create_db)
        loop_value = True
        while loop_value:
            try:
                version = await conn.fetch(
                    """
                    SELECT version
                    FROM version;
                    """
                )
                version = version[0].get("version")
            except asyncpg.exceptions.UndefinedTableError:
                version = "v0.0.0"
            print(f"Current database version: {version}")
            version_action = queries[version]
            if version_action is not None:
                print(
                    f"Updating database from {version} to {version_action['new_version']}"
                )
                await conn.execute(version_action["query"])
                print(f"Database updated to {version_action['new_version']}")
            else:
                loop_value = False

            await asyncio.sleep(1)
