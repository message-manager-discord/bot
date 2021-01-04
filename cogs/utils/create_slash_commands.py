# File used to manage commands that are in beta, rest are managed by the library

import logging

from typing import Any, Dict, List, Optional, Tuple, Union

import aiohttp

from config import client_id, token
from main import Bot

logger = logging.getLogger("slash_cmds_manager")


base_url = "https://discord.com/api/v8/applications"
commands: Dict[str, List[Dict[str, Any]]] = {  # No commands that are in the beta phase
    "fake_global": [],
}

headers = {"Authorization": f"Bot {token}", "Content-Type": "application/json"}


async def global_commands(session: aiohttp.ClientSession) -> None:
    # Global Commands - Delete all
    global_url = f"{base_url}/{client_id}/commands"
    r = await session.get(global_url, headers=headers)
    existing_global_commands = await r.json()
    if r.status != 200:
        logging.warning(f"Error in fetching global commands; Response: {await r.text()}")  # type: ignore
    commands_deleted = 0
    for command in existing_global_commands:
        command_id = command["id"]
        r = await session.delete(f"{global_url}/{command_id}", headers=headers)
        if not r.status == 204:
            logger.warning(
                f"Global command delete failed; Response: {await r.text()}, Command: {command}"  # type: ignore
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
                f"Failed to create global command; Response: {await r.text()}, Command: {command}"  # type: ignore
            )
    logger.info(f"Created {succeeded_commands} global commands")


async def sync_guild_commands(
    guild_id: int, session: aiohttp.ClientSession
) -> Optional[Union[None, Tuple[int, int, str]]]:
    guild_url = f"{base_url}/{client_id}/guilds/{guild_id}/commands"
    r = await session.get(guild_url, headers=headers)
    existing_guild_commands = await r.json()
    if r.status != 200:
        logging.warning(
            f"Error in fetching guild commands; Guild: {guild_id}, Response: {await r.text()}"  # type: ignore
        )
        return (r.status, guild_id, await r.text())
    commands_deleted = 0
    for command in existing_guild_commands:
        command_id = command["id"]
        r = await session.delete(f"{guild_url}/{command_id}", headers=headers)
        if r.status == 204:
            commands_deleted = commands_deleted + 1
        else:
            logger.warning(
                f"Failed to delete guild command; Guild: {guild_id}, Response: {await r.text()}, Command: {command}"  # type: ignore
            )
            return (r.status, guild_id, await r.text())
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
                f"Failed to create guild command; Guild: {guild_id}, Response: {await r.text()}, Command: {command}"  # type: ignore
            )
            return (r.status, guild_id, await r.text())
    logger.info(
        f"Created {commands_created} guild commands; Guild: {guild_id}, Commands: {guild_commands}"
    )
    return None


async def sync_commands(
    fake_global: List[int], session: aiohttp.ClientSession
) -> Optional[Union[None, Tuple[int, int, str]]]:
    await global_commands(session)

    # Fake Global Commands - Delete all
    for guild in fake_global:
        gc = await sync_guild_commands(guild, session)
        if gc is not None:
            return gc
    return None


async def sync_all(bot: Bot) -> Optional[Union[None, Tuple[int, int, str]]]:
    guilds = await bot.db.get_all_slash_servers()
    async with aiohttp.ClientSession() as session:
        sc = await sync_commands(guilds, session)
        if sc is not None:
            return sc
    return None
