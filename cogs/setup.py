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
from typing import TYPE_CHECKING, Optional, Union

import discord

from discord.ext import commands
from discord_slash import SlashCommand, SlashContext, cog_ext
from discord_slash.utils import manage_commands

from cogs.utils import errors
from main import Bot

if TYPE_CHECKING:
    Cog = commands.Cog[commands.Context]
else:
    Cog = commands.Cog

settings_set_group_desc = "Set the values of settings"

settings_get_group_desc = "Gets the current value of the setting"

settings_base_desc = "Set and get values of settings"


class SetupCog(Cog):
    def __init__(self, bot: Bot) -> None:
        if not hasattr(bot, "slash"):
            # Creates new SlashCommand instance to bot if bot doesn't have.
            bot.slash = SlashCommand(
                bot, override_type=True, auto_register=True, auto_delete=True
            )
        self.bot = bot
        self.bot.slash.get_cog_commands(self)

    def cog_unload(self) -> None:
        self.bot.slash.remove_cog_commands(self)

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
                errors.WebhookChannelNotTextChannel,
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

    async def set_logging_logic(
        self,
        guild: discord.Guild,
        author: discord.Member,
        channel_input: Optional[str] = None,
    ) -> Union[discord.Embed, str]:
        if not author.guild_permissions.administrator:
            raise commands.MissingPermissions(["administrator"])  # type: ignore
        original_logging_channel = await self.bot.db.get_loggers(guild.id, "main")
        if channel_input is None:
            if original_logging_channel is None:
                return "Nothing has been set yet for logging!"
            else:
                return discord.Embed(
                    title="Current logging channel",
                    description=f"<#{original_logging_channel.channel_id}>",
                    colour=discord.Colour(15653155),
                    timestamp=datetime.now(timezone.utc),
                )
        else:
            embed = discord.Embed(
                title="Config updated!",
                timestamp=datetime.now(timezone.utc),
                colour=discord.Colour(15653155),
            )
            if channel_input.lower() == "none":
                await self.bot.db.remove_logger(guild, "main")
                embed.description = f"Logging channel updated from <#{original_logging_channel.channel_id}> to None"
                return embed
            else:
                if channel_input[:2] == "<#":
                    channel_input = channel_input[2:-1]
                try:
                    channel_id = int(channel_input)
                    channel = guild.get_channel(channel_id)
                    if channel is None:
                        raise errors.InputContentIncorrect(
                            "I could not find that channel! Please try again"
                        )
                except ValueError:
                    raise errors.InputContentIncorrect(
                        "I could not find that channel! Please try again"
                    )
                if not isinstance(channel, discord.TextChannel):
                    raise errors.WebhookChannelNotTextChannel(
                        "That channel is not a text channel! "
                        "Try again with a text channel."
                    )
                await self.bot.db.update_logger(guild, channel.id, "main")

                if original_logging_channel is None:
                    embed.description = f"Logging channel updated to {channel.mention}"
                else:
                    embed.description = f"Logging channel updated from <#{original_logging_channel.channel_id}> to {channel.mention}"
                return embed

    @cog_ext.cog_subcommand(
        base="settings",
        subcommand_group="set",
        sub_group_desc=settings_set_group_desc,
        name="logging",
        description="Set the logging channel, don't pass anything to reset it.",
        base_description=settings_base_desc,
        options=[
            manage_commands.create_option(
                name="channel",
                description="New logging channel",
                option_type=7,
                required=False,
            )
        ],
    )
    async def _set_logging(
        self,
        ctx: SlashContext,
        channel: Optional[Union[discord.TextChannel, int, str]] = None,
    ) -> None:
        if channel is None:
            channel = "none"
        if not isinstance(ctx.guild, discord.Guild):
            for guild in self.bot.guilds:
                if ctx.guild == guild.id:
                    ctx.guild = self.bot.get_channel(ctx.guild)
                    break
            else:
                await ctx.send(
                    content=(
                        "Error!! A bot user is required for this command to work!"
                        "\nPlease invite me, invite link here: https://messagemanager.xyz/invite"
                    ),
                    complete_hidden=True,
                )
                return
        if not isinstance(ctx.author, discord.Member):
            ctx.author = await ctx.guild.fetch_member(ctx.author)

        if not isinstance(channel, (int, str)):

            channel = channel.id

        try:

            msg = await self.set_logging_logic(ctx.guild, ctx.author, str(channel))

        except Exception as e:

            if isinstance(
                e,
                (
                    errors.InputContentIncorrect,
                    commands.MissingPermissions,
                    errors.WebhookChannelNotTextChannel,
                ),
            ):

                await ctx.send(content=str(e), complete_hidden=True)
                return

            else:
                raise
        await ctx.send(embeds=[msg])

    @cog_ext.cog_subcommand(
        base="settings",
        subcommand_group="get",
        sub_group_desc=settings_get_group_desc,
        name="logging",
        description="Gets the logging channel",
        base_description=settings_base_desc,
    )
    async def _get_logging(self, ctx: SlashContext) -> None:
        if not isinstance(ctx.guild, discord.Guild):
            for guild in self.bot.guilds:
                if ctx.guild == guild.id:
                    ctx.guild = self.bot.get_channel(ctx.guild)
                    break
            else:
                await ctx.send(
                    content=(
                        "Error!! A bot user is required for this command to work!"
                        "\nPlease invite me, invite link here: https://messagemanager.xyz/invite"
                    ),
                    complete_hidden=True,
                )
                return
        if not isinstance(ctx.author, discord.Member):
            ctx.author = await ctx.guild.fetch_member(ctx.author)

        try:
            msg = await self.set_logging_logic(ctx.guild, ctx.author, None)

        except commands.MissingPermissions as e:

            await ctx.send(content=str(e), complete_hidden=True)
            return
        if isinstance(msg, str):
            await ctx.send(content=msg)
        else:
            await ctx.send(embeds=[msg])

    @setup.command(name="logging")
    async def set_logging(
        self, ctx: commands.Context, channel_input: Optional[str] = None
    ) -> None:
        if ctx.guild is None:
            raise commands.CheckFailure("Internal error: ctx.guild was None")
        assert isinstance(ctx.author, discord.Member)
        msg = await self.set_logging_logic(ctx.guild, ctx.author, channel_input)
        if isinstance(msg, discord.Embed):
            await ctx.send(embed=msg)
        else:
            await ctx.send(msg)

    @commands.command(name="prefix")
    async def prefix(self, ctx: commands.Context) -> None:
        prefix = await self.bot.db.get_prefix(ctx.guild)
        await ctx.send(f"My prefix for this server is: `{prefix}`")


def setup(bot: Bot) -> None:
    bot.add_cog(SetupCog(bot))
    print("    Setup cog!")
