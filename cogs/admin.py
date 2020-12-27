# admin.py

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
import datetime
import random
import string

from math import floor
from typing import TYPE_CHECKING, Optional

import aiohttp
import discord

from discord.ext import commands

from cogs.utils import errors
from cogs.utils.create_slash_commands import sync_all, sync_guild_commands
from main import Bot

if TYPE_CHECKING:
    Cog = commands.Cog[commands.Context]
else:
    Cog = commands.Cog


class AdminCog(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    async def cog_check(self, ctx: commands.Context) -> bool:
        if await self.bot.is_owner(ctx.author):
            return True
        else:
            raise errors.MissingPermission("You need to be a bot dev to do that!")

    async def cog_command_error(
        self, ctx: commands.Context, error: discord.DiscordException
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
            raise error

    @commands.command(hidden=True)
    async def load(self, ctx: commands.Context, *, module: str) -> None:
        try:
            self.bot.load_extension(module)
        except Exception as error:
            await ctx.send(f"{type(error).__name__}: {error}")
        else:
            await ctx.send(f"The module {module} was loaded!")

    @commands.command(hidden=True)
    async def unload(self, ctx: commands.Context, *, module: str) -> None:
        """Unloads a module."""
        try:
            self.bot.unload_extension(module)
        except Exception as error:
            await ctx.send(f"{type(error).__name__}: {error}")
        else:
            await ctx.send(f"The module {module} was unloaded!")

    @commands.command(name="reload", hidden=True)
    async def _reload(self, ctx: commands.Context, *, module: str) -> None:
        """Reloads a module."""
        try:
            self.bot.unload_extension(module)
            self.bot.load_extension(module)
        except Exception as error:
            await ctx.send(f"{type(error).__name__}: {error}")
        else:
            await ctx.send(f"The module {module} was reloaded!")

    @commands.command(aliases=["restart"])
    async def stop(self, ctx: commands.Context) -> None:
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
    async def loadtime(self, ctx: commands.Context) -> None:
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

    @commands.command(name="sync-slash")
    async def sync_slash(
        self, ctx: commands.Context, guild_id: Optional[int] = None
    ) -> None:
        status = await sync_all(self.bot)
        if status is None:
            await ctx.send("Success!")
        else:
            await ctx.send(
                f"Error! Status Code: {status[0]}, Guild: {status[1]}, Error Message: {status[2]}"
            )

    @commands.command(name="slash-beta")
    async def slash_beta(
        self, ctx: commands.Context, guild: int, owner_id: int
    ) -> None:
        guild = self.bot.get_guild(guild)
        if guild is None:
            await ctx.send("I am not in that guild!")
            return
        if guild.owner_id != owner_id:
            await ctx.send("That user is not the owner of that server!")

        else:
            msg = await ctx.send(f"Attempting to add slash commands to {guild.name}")
            await asyncio.sleep(1)
            async with aiohttp.ClientSession() as session:
                status = await sync_guild_commands(guild.id, session)
                if status is None:
                    await msg.edit(
                        content=f"Successfully added guild commands to {guild.name}\nAttempting to add to database"
                    )
                    await asyncio.sleep(1)
                    await self.bot.db.update_slash_enabled(guild, True)
                    await msg.edit(
                        content=f"Successfully added guild commands to {guild.name}, and updated the database.\nAttempting to refresh commands..."
                    )
                    await asyncio.sleep(1)
                    try:
                        self.bot.unload_extension("cogs.slash_cmds")
                        self.bot.slash_guilds = (
                            await self.bot.db.get_all_slash_servers()
                        )
                        self.bot.load_extension("cogs.slash_cmds")
                    except Exception as error:
                        await ctx.send(
                            f"Error with refreshing!!!!\n{type(error).__name__}: {error}"
                        )
                    else:
                        await msg.edit(
                            content=f"Successfully added guilds commands to {guild.name}, updated the database and refreshed the commands."
                        )
                        await ctx.send(
                            f"<@{owner_id}> The slash commands beta has been enabled in your server! "
                            f"Slash commands will now show up in {guild.name}"
                            "\nAll of the slash commands with have normal command equivalents (with the exception of `/slash`) "
                            "So if a slash command stops working, you can use that instead."
                            "\nPlease subscribe to <#759373390515011594>, all updates will be posted there."
                            "\nAs it's in the beta phase bugs and issues may happen, please report them here."
                            "\nThank you so much 🙂"
                        )
                elif status[0] == 403:
                    message = await ctx.send(
                        f"<@{owner_id}> It seems like I don't have the correct authorization in {guild.name}!"
                        f"\nPlease reauthorize me with this link: https://discord.com/api/oauth2/authorize?client_id={self.bot.user.id}&permissions=379968&scope=applications.commands%20bot"
                    )
                    await message.edit(suppress=True)
                else:
                    await ctx.send(
                        f"Error! Status Code: {status[0]}, Guild: {status[1]}, Error Message: {status[2]}"
                    )


def setup(bot: Bot) -> None:
    bot.add_cog(AdminCog(bot))
    print("    Admin cog!")
