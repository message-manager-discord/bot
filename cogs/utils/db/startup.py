# utils/db/startup.py

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

import asyncio

from typing import Dict, Union

import asyncpg

# This file is to create, and maintain databases
# It will check if the tables are created, if not create them
# Also the version number is stored in it's own table
# If the bot gets updated then this is bumped along with any queries to update the tables
# SQL queries will not be changed, only added to with each version

queries: Dict[str, Dict[str, Union[str, None]]] = {
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
    "v1.1.1": {"query": None, "new_version": "v1.2.0"},
    "v1.2.0": {"query": None, "new_version": "v1.3.0"},
    "v1.3.0": {
        "query": """ALTER TABLE servers
    DROP COLUMN bot_channel,
    DROP COLUMN member_channel;""",
        "new_version": "v1.3.1",
    },
    "v1.3.1": {
        "query": """ALTER TABLE servers
    ADD COLUMN slash_enabled BOOLEAN DEFAULT FALSE NOT NULL;""",
        "new_version": "v1.4.0",
    },
    "v1.4.0": {
        "query": """
    ALTER TABLE servers RENAME COLUMN server_id TO id;
    ALTER TABLE servers ADD PRIMARY KEY (id);
    CREATE TABLE channels (
        id BIGINT PRIMARY KEY,
        webhook_id BIGINT,
        webhook_token VARCHAR(255)
    );
    CREATE TABLE logging_channels (
        guild_id BIGINT NOT NULL REFERENCES servers ON DELETE CASCADE,
        channel_id BIGINT NOT NULL REFERENCES channels ON DELETE CASCADE,
        logger_type VARCHAR(20) NOT NULL,
        CONSTRAINT unique_type UNIQUE(guild_id, logger_type)
    );
    """,
        "new_version": "v1.5.0",
    },
    "v1.5.0": {
        "query": "ALTER TABLE servers DROP COLUMN slash_enabled;",
        "new_version": "v1.5.1",
    },
    "v1.5.1": {"query": None, "new_version": "v1.6"},
    "v1.6": {"query": None, "new_version": None},
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


async def init_db(pool: asyncpg.pool.Pool) -> None:
    async with pool.acquire() as conn:
        await conn.execute(create_db)
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
        if version_action["new_version"] is not None:

            current_query = version_action
            next_version = current_query["new_version"]
            for i in range(0, len(queries) * 2):
                if current_query["new_version"] is None:
                    break
                else:
                    if current_query["query"] is not None:
                        await conn.execute(current_query["query"])
                    next_version = current_query["new_version"]
                    current_query = queries[next_version]
            await conn.execute("truncate table version;")
            await conn.execute(
                """
                INSERT INTO version Values(0, $1)
                """,
                next_version,
            )
            print(f"Database updated to {next_version}")

            await asyncio.sleep(1)
