# admin.py

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
import datetime
import logging
import random
import string

from math import floor
from typing import TYPE_CHECKING

import discord

from discord.ext import commands

from main import Bot
from src import Context, errors

if TYPE_CHECKING:
    Cog = commands.Cog[Context]
else:
    Cog = commands.Cog

logger = logging.getLogger(__name__)


class AdminCog(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    async def cog_check(self, ctx: Context) -> bool:
        if await self.bot.is_owner(ctx.author):
            return True
        else:
            raise errors.MissingPermission("You need to be a bot dev to do that!")

    async def cog_command_error(
        self, ctx: Context, error: discord.DiscordException
    ) -> None:
        if isinstance(
            error,
            (
                errors.MissingPermission,
                commands.errors.MissingRequiredArgument,
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

    @commands.command(hidden=True)
    async def load(self, ctx: Context, *, module: str) -> None:
        try:
            self.bot.load_extension(module)
        except Exception as error:
            await ctx.send(f"{type(error).__name__}: {error}")
        else:
            await ctx.send(f"The module {module} was loaded!")

    @commands.command(hidden=True)
    async def unload(self, ctx: Context, *, module: str) -> None:
        """Unloads a module."""
        try:
            self.bot.unload_extension(module)
        except Exception as error:
            await ctx.send(f"{type(error).__name__}: {error}")
        else:
            await ctx.send(f"The module {module} was unloaded!")

    @commands.command(name="reload", hidden=True)
    async def _reload(self, ctx: Context, *, module: str) -> None:
        """Reloads a module."""
        try:
            self.bot.unload_extension(module)
            self.bot.load_extension(module)
        except Exception as error:
            await ctx.send(f"{type(error).__name__}: {error}")
        else:
            await ctx.send(f"The module {module} was reloaded!")

    @commands.command(aliases=["restart"])
    async def stop(self, ctx: Context) -> None:
        message = await ctx.send("Are you sure you want to stop the current process?")

        def is_correct(m: discord.Message) -> bool:
            return m.author == ctx.author

        try:
            choice = await self.bot.wait_for("message", check=is_correct)
        except asyncio.TimeoutError:
            await ctx.send("Timedout, Please re-do the command.")
            return

        if choice.content.lower() == "yes":
            try:
                await choice.delete()
                await message.delete()
            except discord.errors.Forbidden:
                pass
            verify_message = "".join(
                random.SystemRandom().choice(string.ascii_letters + string.digits)
                for _ in range(6)
            )
            message = await ctx.send(
                "Are you still **absolutely** sure you want to log the bot out?\n"
                "**WARNING:** This will disconnect the bot. Depending on the process manager it may have to be started from the console.\n"
                "This could potentally cause to bot to be offline for a significant amount to time, depending on how the script is run.\n"
                f"If you are absolutely sure then reply with the following code: `{verify_message}`"
            )
            try:
                choice = await self.bot.wait_for(
                    "message", check=is_correct, timeout=280.0
                )
            except asyncio.TimeoutError:
                await ctx.send("Timedout, Please re-do the command.")
                return

            if choice.content == verify_message:
                await ctx.send("Logging out")
                try:
                    await self.bot.logout()
                except Exception as error:
                    await ctx.send(f"{type(error).__name__}: {error}")

    @commands.command()
    async def loadtime(self, ctx: Context) -> None:
        diff = self.bot.load_time - self.bot.start_time
        hours = floor(diff.seconds / 3600)
        minutes = floor((diff.seconds - (hours * 3600)) / 60)
        seconds = floor(diff.seconds - (hours * 3600 + minutes * 60))
        milliseconds = floor(diff.microseconds / 1000)
        microseconds = diff.microseconds - (milliseconds * 1000)
        await ctx.send(
            embed=discord.Embed(
                title="Time it took to load",
                description=f"{hours} Hours, {minutes} Minutes, {seconds} Seconds, {milliseconds} Milliseconds, {microseconds} Microseconds",
                colour=discord.Colour(16761035),
                timestamp=datetime.datetime.now(datetime.timezone.utc),
            )
        )


def setup(bot: Bot) -> None:
    bot.add_cog(AdminCog(bot))
    logger.info("Admin cog!")
