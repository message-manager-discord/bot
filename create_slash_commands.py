import asyncio
import logging
import typing

import aiohttp

from config import client_id, token

logger = logging.getLogger("slash_cmds_manager")


base_url = "https://discord.com/api/v8/applications"
commands: typing.Dict[str, typing.List[typing.Dict[str, typing.Any]]] = {
    "global": [],
    "fake_global": [
        {
            "name": "info",
            "description": "Information commands",
            "options": [
                {
                    "name": "ping",
                    "description": "Returns the current gateway latency",
                    "type": 1,
                },
                {"name": "privacy", "description": "Privacy information", "type": 1},
                {"name": "info", "description": "Bot information", "type": 1},
                {"name": "invite", "description": "Bot invite", "type": 1},
                {"name": "docs", "description": "Bot documentation", "type": 1},
                {"name": "source", "description": "Bot's source code", "type": 1},
                {
                    "name": "support",
                    "description": "Join my support server!",
                    "type": 1,
                },
            ],
        },
    ],
}

headers = {"Authorization": f"Bot {token}", "Content-Type": "application/json"}


async def global_commands(session: aiohttp.ClientSession) -> None:
    # Global Commands - Delete all
    global_url = f"{base_url}/{client_id}/commands"
    r = await session.get(global_url, headers=headers)
    existing_global_commands = await r.json()
    if r.status != 200:
        logging.warning(f"Error in fetching global commands; Response: {await r.text}")  # type: ignore
    commands_deleted = 0
    for command in existing_global_commands:
        command_id = command["id"]
        r = await session.delete(f"{global_url}/{command_id}", headers=headers)
        if not r.status == 204:
            logger.warning(
                f"Global command delete failed; Response: {await r.text}, Command: {command}"  # type: ignore
            )
            return
        else:
            commands_deleted = commands_deleted + 1
    logger.info(
        f"Deleted {commands_deleted} global commands {existing_global_commands}"
    )
    # Global Commands - Add all
    global_commands = commands["global"]
    succeeded_commands = 0
    for command in global_commands:
        r = await session.post(f"{global_url}", headers=headers, json=command)
        if r.status == 201:
            succeeded_commands = succeeded_commands + 1
        else:
            logger.warning(
                f"Failed to create global command; Response: {await r.text}, Command: {command}"  # type: ignore
            )
    logger.info(f"Created {succeeded_commands} global commands")


async def sync_guild_commands(guild_id: int, session: aiohttp.ClientSession) -> None:
    guild_url = f"{base_url}/{client_id}/guilds/{guild_id}/commands"
    r = await session.get(guild_url, headers=headers)
    existing_guild_commands = await r.json()
    if r.status != 200:
        logging.warning(
            f"Error in fetching guild commands; Guild: {guild_id}, Response: {await r.text}"  # type: ignore
        )
        return
    commands_deleted = 0
    for command in existing_guild_commands:
        command_id = command["id"]
        r = await session.delete(f"{guild_url}/{command_id}", headers=headers)
        if r.status == 204:
            commands_deleted = commands_deleted + 1
        else:
            logger.warning(
                f"Failed to delete guild command; Guild: {guild_id}, Response: {await r.text}, Command: {command}"  # type: ignore
            )
    logger.info(
        f"Deleted {commands_deleted} guild commands; Guild: {guild_id}, Commands: {existing_guild_commands}"
    )
    guild_commands = commands["fake_global"]
    commands_created = 0
    for command in guild_commands:
        r = await session.post(f"{guild_url}", headers=headers, json=command)
        if r.status == 201:
            commands_created = commands_created + 1
        else:
            logger.warning(
                f"Failed to create guild command; Guild: {guild_id}, Response: {await r.text}, Command: {command}"  # type: ignore
            )
    logger.info(
        f"Created {commands_created} guild commands; Guild: {guild_id}, Commands: {guild_commands}"
    )


async def sync_commands(
    fake_global: typing.List[int], session: aiohttp.ClientSession
) -> None:
    await global_commands(session)

    # Fake Global Commands - Delete all
    for guild in fake_global:
        await sync_guild_commands(guild, session)


async def main() -> None:
    async with aiohttp.ClientSession() as session:
        await sync_commands([742373263593963614], session)


if __name__ == "__main__":
    logging.basicConfig(
        filename="discord_slash_sync.log", filemode="w", level=logging.INFO
    )
    asyncio.run(main())
