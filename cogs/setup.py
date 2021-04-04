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
from discord_slash import SlashContext, cog_ext
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


class LogicFunctions:
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    async def get_prefix_logic(
        self, guild: discord.Guild, author: discord.Member
    ) -> str:
        guild = await self.bot.db.get_guild(guild)
        return f"My prefix for this server is: `{guild.prefix}`"

    async def set_prefix_logic(
        self, guild: discord.Guild, author: discord.Member, new_prefix: Optional[str]
    ) -> discord.Embed:
        if not author.guild_permissions.administrator:
            raise commands.MissingPermissions(["administrator"])  # type: ignore
        guild = await self.bot.db.get_guild(guild)
        current_prefix = guild.prefix
        if new_prefix is None:
            await self.bot.db.update_prefix(guild, self.bot.default_prefix)
            return discord.Embed(
                title="Config updated!",
                description=f"Server prefix updated from `{current_prefix}` to `{self.bot.default_prefix}`",
                timestamp=datetime.now(timezone.utc),
                colour=discord.Colour(15653155),
            )
        else:
            if len(new_prefix) > 1:
                raise errors.InputContentIncorrect(
                    "Prefix's can only be 1 character long!"
                )
            else:
                await self.bot.db.update_prefix(guild, new_prefix)
                return discord.Embed(
                    title="Config updated!",
                    description=f"Server prefix updated from `{current_prefix}` to `{new_prefix}`",
                    timestamp=datetime.now(timezone.utc),
                    colour=discord.Colour(15653155),
                )

    async def get_logging_logic(
        self, guild: discord.Guild, author: discord.Member
    ) -> Union[discord.Embed, str]:
        if not author.guild_permissions.administrator:
            raise commands.MissingPermissions(["administrator"])  # type: ignore
        original_logging_channel = await self.bot.db.get_loggers(guild.id, "main")
        if original_logging_channel is None:
            return "Nothing has been set yet for logging!"
        else:
            return discord.Embed(
                title="Current logging channel",
                description=f"<#{original_logging_channel.channel_id}>",
                colour=discord.Colour(15653155),
                timestamp=datetime.now(timezone.utc),
            )

    async def set_logging_logic(
        self,
        guild: discord.Guild,
        author: discord.Member,
        channel_input: Optional[str],
    ) -> Union[discord.Embed, str]:
        if not author.guild_permissions.administrator:
            raise commands.MissingPermissions(["administrator"])  # type: ignore
        original_logging_channel = await self.bot.db.get_loggers(guild.id, "main")
        embed = discord.Embed(
            title="Config updated!",
            timestamp=datetime.now(timezone.utc),
            colour=discord.Colour(15653155),
        )
        if channel_input is None:
            await self.bot.db.remove_logger(guild, "main")
            if original_logging_channel is None:
                embed.description = "Logging channel not updated! It remains None"
            else:
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

    async def get_admin_role_logic(
        self, guild: discord.Guild, author: discord.Member
    ) -> Union[discord.Embed, str]:
        if not author.guild_permissions.administrator:
            raise commands.MissingPermissions(["administrator"])  # type: ignore
        db_guild = await self.bot.db.get_guild(guild)
        original_role_id = db_guild.management_role
        if original_role_id is None:
            return "The admin role has not been set yet!"
        original_role = guild.get_role(original_role_id)
        if original_role is None:
            return "The role could not be found!"
        else:
            return discord.Embed(
                title="Current management role",
                description=original_role.mention,
                colour=discord.Colour(15653155),
                timestamp=datetime.now(timezone.utc),
            )

    async def set_admin_role_logic(
        self, guild: discord.Guild, author: discord.Member, new_role_id: Optional[str]
    ) -> discord.Embed:
        if not author.guild_permissions.administrator:
            raise commands.MissingPermissions(["administrator"])  # type: ignore
        db_guild = await self.bot.db.get_guild(guild)
        original_role_id = db_guild.management_role
        original_role = guild.get_role(original_role_id)
        if new_role_id is None:
            await self.bot.db.update_admin_role(guild, None)

            embed = discord.Embed(
                title="Config updated!",
                timestamp=datetime.now(timezone.utc),
                colour=discord.Colour(15653155),
            )
            if original_role is None:
                embed.description = "Management role has not changed! It remains None"
            else:
                embed.description = (
                    f"Management role updated from {original_role.mention} to None"
                )
            return embed
        else:
            if new_role_id[:3] == "<@&":
                new_role_id = new_role_id[3:-1]
            if isinstance(new_role_id, str):
                try:
                    new_role_id = int(new_role_id)  # type: ignore
                except ValueError:
                    raise errors.InputContentIncorrect(
                        "I could not find that role! Please try again"
                    )
                assert isinstance(new_role_id, int)
            new_role = guild.get_role(new_role_id)
            if new_role is None:
                raise errors.InputContentIncorrect(
                    "I could not find that role! Please try again"
                )
            await self.bot.db.update_admin_role(guild, new_role_id)

            embed = discord.Embed(
                title="Config updated!",
                timestamp=datetime.now(timezone.utc),
                colour=discord.Colour(15653155),
            )
            if original_role is None:
                embed.description = f"Management role updated to {new_role.mention}"
            else:
                embed.description = f"Management role updated from {original_role.mention} to {new_role.mention}"
            return embed


class SetupCog(Cog):
    def __init__(self, bot: Bot, logic_functions: LogicFunctions) -> None:
        self.bot = bot
        self.logic_functions = logic_functions

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

    @setup.command(name="prefix")
    async def return_prefix(
        self, ctx: commands.Context, new_prefix: Optional[str] = None
    ) -> None:
        if ctx.guild is None:
            raise commands.CheckFailure("Internal error: ctx.guild was None")
        assert isinstance(ctx.author, discord.Member)
        if new_prefix is None:
            msg = await self.logic_functions.get_prefix_logic(ctx.guild, ctx.author)
            await ctx.send(msg)
        else:
            if new_prefix.lower() == "none":
                new_prefix = None
            msg_embed = await self.logic_functions.set_prefix_logic(
                ctx.guild, ctx.author, new_prefix
            )
            await ctx.send(embed=msg_embed)

    @commands.has_guild_permissions(administrator=True)
    @setup.command()
    async def admin(
        self, ctx: commands.Context, role_id_input: Optional[str] = None
    ) -> None:
        assert ctx.guild is not None
        assert isinstance(ctx.author, discord.Member)
        if role_id_input is None:
            msg = await self.logic_functions.get_admin_role_logic(ctx.guild, ctx.author)
        else:
            if role_id_input.lower() == "none":
                role_id_input = None
            msg = await self.logic_functions.set_admin_role_logic(
                ctx.guild, ctx.author, role_id_input
            )

        if isinstance(msg, discord.Embed):
            await ctx.send(embed=msg)
        else:
            await ctx.send(content=msg)

    @setup.command(name="logging")
    async def set_logging(
        self, ctx: commands.Context, channel_input: Optional[str] = None
    ) -> None:
        if ctx.guild is None:
            raise commands.CheckFailure("Internal error: ctx.guild was None")
        assert isinstance(ctx.author, discord.Member)
        if channel_input is None:
            msg = await self.logic_functions.get_logging_logic(ctx.guild, ctx.author)
        else:
            if channel_input.lower() == "none":
                channel_input = None
            msg = await self.logic_functions.set_logging_logic(
                ctx.guild, ctx.author, channel_input
            )
        if isinstance(msg, discord.Embed):
            await ctx.send(embed=msg)
        else:
            await ctx.send(msg)

    @commands.command(name="prefix")
    async def prefix(self, ctx: commands.Context) -> None:
        guild = await self.bot.db.get_guild(ctx.guild)
        await ctx.send(f"My prefix for this server is: `{guild.prefix}`")


class SetupCogSlash(Cog):
    def __init__(self, bot: Bot, logic_functions: LogicFunctions) -> None:
        self.bot = bot
        self.logic_functions = logic_functions

    @cog_ext.cog_subcommand(
        base="settings",
        subcommand_group="set",
        sub_group_desc=settings_set_group_desc,
        name="prefix",
        description="Set the prefix, don't pass anything to reset it.",
        base_description=settings_base_desc,
        options=[
            manage_commands.create_option(
                name="prefix",
                description="New prefix",
                option_type=3,
                required=False,
            )
        ],
    )
    async def _set_prefix(
        self,
        ctx: SlashContext,
        prefix: Optional[str] = None,
    ) -> None:
        if ctx.guild is None:
            await ctx.send(
                content=(
                    "You've either ran this command in a dm or in a server without the bot user!"
                    "\nYou cannot run this command in dms"
                    "\nAnd a bot user is required for this command to work!"
                    "\nPlease invite me, invite link here: https://messagemanager.xyz/invite"
                ),
                hidden=True,
            )
            return
        if ctx.author is None:
            ctx.author = await ctx.guild.fetch_member(ctx.author_id)

        try:

            msg = await self.logic_functions.set_prefix_logic(
                ctx.guild, ctx.author, prefix
            )

        except Exception as e:

            if isinstance(
                e,
                (
                    errors.InputContentIncorrect,
                    commands.MissingPermissions,
                    errors.WebhookChannelNotTextChannel,
                ),
            ):
                await ctx.send(content=str(e), hidden=True)
                return

            else:
                raise
        await ctx.send(embeds=[msg])

    @cog_ext.cog_subcommand(
        base="settings",
        subcommand_group="get",
        sub_group_desc=settings_get_group_desc,
        name="prefix",
        description="Gets the current prefix",
        base_description=settings_base_desc,
    )
    async def _get_prefix(self, ctx: SlashContext) -> None:
        if ctx.guild is None:

            await ctx.send(
                content=(
                    "You've either ran this command in a dm or in a server without the bot user!"
                    "\nYou cannot run this command in dms"
                    "\nAnd a bot user is required for this command to work!"
                    "\nPlease invite me, invite link here: https://messagemanager.xyz/invite"
                ),
                hidden=True,
            )
            return
        if ctx.author is None:
            ctx.author = await ctx.guild.fetch_member(ctx.author_id)

        try:
            msg = await self.logic_functions.get_prefix_logic(ctx.guild, ctx.author)

        except commands.MissingPermissions as e:

            await ctx.send(content=str(e), hidden=True)
            return

        await ctx.send(content=msg)

    @cog_ext.cog_subcommand(
        base="settings",
        subcommand_group="set",
        sub_group_desc=settings_set_group_desc,
        name="logging",
        description="Set the logging channel, don't pass anything to remove it.",
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
        if ctx.guild is None:

            await ctx.send(
                content=(
                    "You've either ran this command in a dm or in a server without the bot user!"
                    "\nYou cannot run this command in dms"
                    "\nAnd a bot user is required for this command to work!"
                    "\nPlease invite me, invite link here: https://messagemanager.xyz/invite"
                ),
                hidden=True,
            )
            return
        if ctx.author is None:
            ctx.author = await ctx.guild.fetch_member(ctx.author_id)

        if not isinstance(channel, (int, str)) and channel is not None:

            channel = channel.id

        if channel is not None:
            channel = str(channel)

        try:

            msg = await self.logic_functions.set_logging_logic(
                ctx.guild, ctx.author, channel
            )

        except Exception as e:

            if isinstance(
                e,
                (
                    errors.InputContentIncorrect,
                    commands.MissingPermissions,
                    errors.WebhookChannelNotTextChannel,
                ),
            ):

                await ctx.send(content=str(e), hidden=True)
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
        if ctx.guild is None:

            await ctx.send(
                content=(
                    "You've either ran this command in a dm or in a server without the bot user!"
                    "\nYou cannot run this command in dms"
                    "\nAnd a bot user is required for this command to work!"
                    "\nPlease invite me, invite link here: https://messagemanager.xyz/invite"
                ),
                hidden=True,
            )
            return
        if ctx.author is None:
            ctx.author = await ctx.guild.fetch_member(ctx.author_id)

        try:
            msg = await self.logic_functions.get_logging_logic(ctx.guild, ctx.author)

        except commands.MissingPermissions as e:

            await ctx.send(content=str(e), hidden=True)
            return

        if isinstance(msg, str):
            await ctx.send(content=msg)
        else:
            await ctx.send(embeds=[msg])

    @cog_ext.cog_subcommand(
        base="settings",
        subcommand_group="set",
        sub_group_desc=settings_set_group_desc,
        name="admin",
        description="Set the admin role, don't pass anything to remove it.",
        base_description=settings_base_desc,
        options=[
            manage_commands.create_option(
                name="role",
                description="Admin role",
                option_type=8,
                required=False,
            )
        ],
    )
    async def _set_admin(
        self,
        ctx: SlashContext,
        role: Optional[Union[discord.Role, int, str]] = None,
    ) -> None:
        if ctx.guild is None:

            await ctx.send(
                content=(
                    "You've either ran this command in a dm or in a server without the bot user!"
                    "\nYou cannot run this command in dms"
                    "\nAnd a bot user is required for this command to work!"
                    "\nPlease invite me, invite link here: https://messagemanager.xyz/invite"
                ),
                hidden=True,
            )
            return
        if ctx.author is None:
            ctx.author = await ctx.guild.fetch_member(ctx.author_id)

        if not isinstance(role, (int, str)) and role is not None:

            role = role.id

        if role is not None:
            role = str(role)

        try:

            msg = await self.logic_functions.set_admin_role_logic(
                ctx.guild, ctx.author, role
            )

        except Exception as e:

            if isinstance(
                e,
                (
                    errors.InputContentIncorrect,
                    commands.MissingPermissions,
                    errors.WebhookChannelNotTextChannel,
                ),
            ):
                await ctx.ack(hidden=True)
                await ctx.send(content=str(e), hidden=True)
                return

            else:
                raise

        await ctx.send(embeds=[msg])

    @cog_ext.cog_subcommand(
        base="settings",
        subcommand_group="get",
        sub_group_desc=settings_get_group_desc,
        name="admin",
        description="Gets the admin role",
        base_description=settings_base_desc,
    )
    async def _get_admin(self, ctx: SlashContext) -> None:
        if ctx.guild is None:

            await ctx.send(
                content=(
                    "You've either ran this command in a dm or in a server without the bot user!"
                    "\nYou cannot run this command in dms"
                    "\nAnd a bot user is required for this command to work!"
                    "\nPlease invite me, invite link here: https://messagemanager.xyz/invite"
                ),
                hidden=True,
            )
            return
        if ctx.author is None:
            ctx.author = await ctx.guild.fetch_member(ctx.author_id)

        try:
            msg = await self.logic_functions.get_admin_role_logic(ctx.guild, ctx.author)

        except commands.MissingPermissions as e:

            await ctx.send(content=str(e), hidden=True)
            return

        if isinstance(msg, str):
            await ctx.send(content=msg)
        else:
            await ctx.send(embeds=[msg])


def setup(bot: Bot) -> None:
    logic_functions = LogicFunctions(bot)
    bot.add_cog(SetupCog(bot, logic_functions))
    bot.add_cog(SetupCogSlash(bot, logic_functions))
    print("    Setup cog!")
