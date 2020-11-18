# src/db/startup.py

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
        """,
        "new_version": "v1.0.0",
    },
    "v1.0.0": {"query": None, "new_version": "v1.1.0"},
    "v1.1.0": {"query": None, "new_version": "v1.1.1"},
    "v1.1.1": None,
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
                if version_action["query"] is not None:
                    await conn.execute(version_action["query"])
                await conn.execute("truncate table version;")
                await conn.execute(
                    """
                    INSERT INTO version Values(0, $1)
                    """,
                    version_action["new_version"],
                )
                print(f"Database updated to {version_action['new_version']}")
            else:
                loop_value = False

            await asyncio.sleep(1)
