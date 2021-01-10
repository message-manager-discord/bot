# cogs/setup.py

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

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

import discord

from discord.ext import commands

from cogs.utils import errors
from main import Bot

if TYPE_CHECKING:
    Cog = commands.Cog[commands.Context]
else:
    Cog = commands.Cog


class SetupCog(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    async def cog_command_error(
        self, ctx: commands.Context, error: discord.DiscordException
    ) -> None:
        if isinstance(
            error,
            (
                errors.MissingPermission,
                errors.InputContentIncorrect,
                errors.ConfigNotSet,
                errors.ConfigError,
                commands.errors.MissingPermissions,
                commands.errors.NoPrivateMessage,
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

    @commands.has_guild_permissions(administrator=True)
    @commands.group()
    async def setup(self, ctx: commands.Context) -> None:
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                title="Setup!",
                description="Setup values for your server!",
                timestamp=datetime.now(timezone.utc),
                colour=discord.Colour(15653155),
            )
            embed.add_field(
                name=self.bot.command_with_prefix(ctx, "setup admin {role}"),
                value="This is the role that allows admin access to admin commands.",
                inline=False,
            )
            embed.add_field(
                name=self.bot.command_with_prefix(ctx, "setup prefix {prefix}"),
                value="Sets the prefix for this server.",
                inline=False,
            )
            embed.add_field(
                name=self.bot.command_with_prefix(ctx, "setup logging {channel}"),
                value="Sets the logging channel. Requires the Manage Webhooks permission",
                inline=False,
            )
            await ctx.send(embed=embed)

    @commands.has_guild_permissions(administrator=True)
    @setup.command(name="prefix")
    async def return_prefix(
        self, ctx: commands.Context, new_prefix: Optional[str] = None
    ) -> None:
        prefix = await self.bot.db.get_prefix(ctx.guild)
        if new_prefix is None:
            await ctx.send(f"My prefix for this server is: `{prefix}`")
        elif new_prefix.lower() == "none":
            await self.bot.db.update_prefix(ctx.guild, self.bot.default_prefix)
            await ctx.send(
                embed=discord.Embed(
                    title="Config updated!",
                    description=f"Server prefix updated from `{prefix}` to `{self.bot.default_prefix}`",
                    timestamp=datetime.now(timezone.utc),
                    colour=discord.Colour(15653155),
                )
            )
        else:
            if len(new_prefix) > 1:
                raise errors.InputContentIncorrect(
                    "Prefix's can only be 1 character long!"
                )
            else:
                await self.bot.db.update_prefix(ctx.guild, new_prefix)
                await ctx.send(
                    embed=discord.Embed(
                        title="Config updated!",
                        description=f"Server prefix updated from `{prefix}` to `{new_prefix}`",
                        timestamp=datetime.now(timezone.utc),
                        colour=discord.Colour(15653155),
                    )
                )

    @commands.has_guild_permissions(administrator=True)
    @setup.command()
    async def admin(
        self, ctx: commands.Context, role_id_input: Optional[str] = None
    ) -> None:
        assert ctx.guild is not None
        original_role_id = await self.bot.db.get_management_role(ctx.guild)
        if original_role_id is None and role_id_input is None:
            raise errors.ConfigNotSet("The admin role has not been set yet!")
        original_role = ctx.guild.get_role(original_role_id)
        if role_id_input is None:

            if original_role is None:
                raise errors.ConfigNotSet("The role could not be found!")
            else:
                await ctx.send(
                    embed=discord.Embed(
                        title="Current management role",
                        description=original_role.mention,
                        colour=discord.Colour(15653155),
                        timestamp=datetime.now(timezone.utc),
                    )
                )

        else:
            if role_id_input.lower() == "none":
                await self.bot.db.update_admin_role(ctx.guild, None)

                embed = discord.Embed(
                    title="Config updated!",
                    timestamp=datetime.now(timezone.utc),
                    colour=discord.Colour(15653155),
                )
                if original_role is None:
                    embed.description = "Management role updated to None"
                else:
                    embed.description = (
                        f"Management role updated from {original_role.mention} to None"
                    )
                await ctx.send(
                    embed=embed, allowed_mentions=discord.AllowedMentions(roles=False)
                )
            else:
                if role_id_input[:3] == "<@&":
                    role_id_input = role_id_input[3:-1]
                try:
                    role_id = int(role_id_input)
                    role = ctx.guild.get_role(role_id)
                    if role is None:
                        raise errors.InputContentIncorrect(
                            "I could not find that role! Please try again"
                        )
                except ValueError:
                    raise errors.InputContentIncorrect(
                        "I could not find that role! Please try again"
                    )
                await self.bot.db.update_admin_role(ctx.guild, role_id)

                embed = discord.Embed(
                    title="Config updated!",
                    timestamp=datetime.now(timezone.utc),
                    colour=discord.Colour(15653155),
                )
                if original_role is None:
                    embed.description = f"Management role updated to {role.mention}"
                else:
                    embed.description = f"Management role updated from {original_role.mention} to {role.mention}"
                await ctx.send(
                    embed=embed, allowed_mentions=discord.AllowedMentions(roles=False)
                )

    @setup.command(name="logging")
    async def set_logging(
        self, ctx: commands.Context, channel_input: Optional[str] = None
    ) -> None:
        if ctx.guild is None:
            raise commands.CheckFailure("Internal error: ctx.guild was None")
        original_logging_channel = await self.bot.db.get_loggers(ctx.guild.id, "main")
        if channel_input is None:
            if original_logging_channel is None:
                await ctx.send("Nothing has been set yet for logging!")
            else:
                await ctx.send(
                    embed=discord.Embed(
                        title="Current logging channel",
                        description=f"<#{original_logging_channel.channel_id}>",
                        colour=discord.Colour(15653155),
                        timestamp=datetime.now(timezone.utc),
                    )
                )
        else:
            embed = discord.Embed(
                title="Config updated!",
                timestamp=datetime.now(timezone.utc),
                colour=discord.Colour(15653155),
            )
            if channel_input.lower() == "none":
                await self.bot.db.remove_logger(ctx.guild, "main")
                embed.description = f"Logging channel updated from <#{original_logging_channel.channel_id}> to None"
                await ctx.send(embed=embed)
            else:
                if channel_input[:2] == "<#":
                    channel_input = channel_input[2:-1]
                try:
                    channel_id = int(channel_input)
                    channel = ctx.guild.get_channel(channel_id)
                    if channel is None:
                        raise errors.InputContentIncorrect(
                            "I could not find that channel! Please try again"
                        )
                except ValueError:
                    raise errors.InputContentIncorrect(
                        "I could not find that channel! Please try again"
                    )
                await self.bot.db.update_logger(ctx.guild, channel.id, "main")

                if original_logging_channel is None:
                    embed.description = f"Logging channel updated to {channel.mention}"
                else:
                    embed.description = f"Logging channel updated from <#{original_logging_channel.channel_id}> to {channel.mention}"
                await ctx.send(
                    embed=embed, allowed_mentions=discord.AllowedMentions(roles=False)
                )

    @commands.command(name="prefix")
    async def prefix(self, ctx: commands.Context) -> None:
        prefix = await self.bot.db.get_prefix(ctx.guild)
        await ctx.send(f"My prefix for this server is: `{prefix}`")


def setup(bot: Bot) -> None:
    bot.add_cog(SetupCog(bot))
    print("    Setup cog!")
