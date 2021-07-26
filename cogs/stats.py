# cogs/stats.py
# type: ignore
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


from discord.ext import commands

from src import Context, errors

logger = logging.getLogger(__name__)


class StatsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_command_error(self, ctx: Context, error):
        if isinstance(
            error,
            (
                errors.MissingPermission,
                errors.ContentError,
                errors.ConfigNotSet,
                commands.NoPrivateMessage,
            ),
        ):
            await ctx.send(error)
        else:
            await ctx.send(
                "There was an unknown error!\n"
                f"Report a bug or get support from the support server at {self.bot.command_with_prefix(ctx, 'support')}\n"
                f"Error: {error}"
            )
            logger.error(
                f"Ignoring exception in interaction {ctx.command}:", exc_info=error
            )

    @commands.group()
    async def stats(self, ctx: Context):
        if ctx.invoked_subcommand is None:
            await ctx.invoke(self.bot.get_command("stats update"))

    @stats.command(name="update", aliases=["_update"])
    @commands.guild_only()
    async def stats_force_update(self, ctx: Context):
        await ctx.send(
            "Unfortunately this function had to be removed.\nSee https://github.com/AnotherCat/message-manager/blob/master/CHANGELOG.md/#v110 for more info."
        )


def setup(bot):
    bot.add_cog(StatsCog(bot))
    logger.info("Stats cog!")
