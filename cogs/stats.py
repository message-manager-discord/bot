# cogs/stats.py

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

import discord

from discord.ext import commands, tasks


class StatsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.stats_update_loop.start()

    async def cog_check(self, ctx: commands.Context):
        return await self.bot.checks.check_if_manage_role(self.bot, ctx)

    async def cog_command_error(self, ctx: commands.Context, error):
        if isinstance(
            error,
            (
                self.bot.errors.MissingPermission,
                self.bot.errors.ContentError,
                self.bot.errors.ConfigNotSet,
                commands.NoPrivateMessage,
            ),
        ):
            await ctx.send(error)
        elif isinstance(error, commands.CommandOnCooldown):
            mins = int(error.retry_after / 60)
            sec = int(error.retry_after % 60)
            await ctx.send(
                f"That command is on cool down for another {mins} minutes and {sec} seconds!\n{error.retry_after}"
            )
        else:
            await ctx.send(
                "There was an unknown error! "
                "This has been reported to the devs."
                "\nIf by any chance this broke something, "
                "contact us through our support server"
            )
            raise error

    async def cog_unload(self):
        self.stats_update_loop.cancel()

    async def update_stats(self, guild):
        pool = self.bot.db
        member_channel = await pool.get_member_channel(guild)
        bot_channel = await pool.get_bot_channel(guild)
        if member_channel is not None:
            member_channel_obj = self.bot.get_channel(int(member_channel))
            member_count = len([m for m in guild.members if not m.bot])
            if not member_channel_obj.name[12:] == str(member_count):
                try:
                    await member_channel_obj.edit(
                        name=f"User Count: {int(member_count)}"
                    )
                except discord.Forbidden:
                    pass

        if bot_channel is not None:
            bot_channel_obj = self.bot.get_channel(int(bot_channel))
            bot_count = len([m for m in guild.members if m.bot])
            if not bot_channel_obj.name[11:] == str(bot_count):
                try:
                    await bot_channel_obj.edit(name=f"Bot Count: {int(bot_count)}")
                except discord.errors.Forbidden:
                    pass
        if bot_channel is None and member_channel is None:
            return False
        else:
            return True

    @commands.group()
    async def stats(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            pass

    @stats.command(name="update", aliases=["_update"])
    @commands.cooldown(1, 600, commands.BucketType.guild)
    @commands.guild_only()
    async def stats_force_update(self, ctx: commands.Context):
        pool = self.bot.db
        prefix = await pool.get_prefix(ctx.guild)
        updated = await self.update_stats(ctx.guild)
        if ctx.invoked_with == "update":
            if updated:
                await ctx.send("Stats updated!")
            else:
                raise self.bot.errors.ConfigNotSet(
                    f"You have not set any stats channels!\nDo this with the `{prefix}config` command"
                )

    @tasks.loop(minutes=30)
    async def stats_update_loop(self):
        time_to_wait = (30 * 0.5 * 60) / len(self.bot.guilds)
        for guild in self.bot.guilds:
            updated = await self.update_stats(guild)
            if updated:
                await asyncio.sleep(time_to_wait)

    @stats_update_loop.before_loop
    async def before_stats_update_loop(self):
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(StatsCog(bot))
    print("    Stats cog!")
