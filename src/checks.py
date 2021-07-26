# cogs/utils/checks.py

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

import logging

import discord

from main import Bot
from src import Context, errors

logger = logging.getLogger(__name__)


async def check_if_manage_role(bot: Bot, ctx: Context) -> bool:
    if guild_only(bot, ctx):
        assert isinstance(ctx.author, discord.Member)
        assert ctx.guild is not None
        assert (
            ctx.guild_data is not None
        )  # fetch_data is called on processing commands if guild is not None
        management_role_id = ctx.guild_data.management_role_id
        if ctx.author.id == ctx.guild.owner_id:
            return True
        elif management_role_id is None:
            raise errors.ConfigNotSet(
                f"You have not set the management role!\nDo this with the `{ctx.prefix}setup` command"
            )
        elif await bot.is_owner(ctx.author):
            return True
        else:
            for role in ctx.author.roles:
                if int(management_role_id) == role.id:
                    return True
            raise errors.MissingPermission(
                "You need the management role to do that!\n"
                "Contact your server admin if you think you should be able to do this"
            )
    return False


def guild_only(bot: Bot, ctx: Context) -> bool:
    if ctx.guild is None:
        raise discord.ext.commands.NoPrivateMessage(
            "That command can only be used in guilds!"
        )
    else:
        return True


def setup(bot: Bot) -> None:
    logger.info("Checks!")
