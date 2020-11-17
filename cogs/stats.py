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

from discord.ext import commands


class StatsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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
        else:
            await ctx.send("There was an unknown error!\n" f"Error: {error}")
            raise error

    @commands.group()
    async def stats(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.invoke(self.bot.get_command("stats update"))

    @stats.command(name="update", aliases=["_update"])
    @commands.guild_only()
    async def stats_force_update(self, ctx: commands.Context):
        await ctx.send(
            "Unfortunately this function had to be removed.\nSee https://github.com/AnotherCat/message-bot/blob/master/CHANGELOG.md/#v110 for more info."
        )


def setup(bot):
    bot.add_cog(StatsCog(bot))
    print("    Stats cog!")
