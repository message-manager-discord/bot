# cogs/setup.py

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


from datetime import datetime, timezone
from typing import TYPE_CHECKING, Awaitable, Callable, Optional, Union

import discord

from discord.embeds import Embed
from discord.ext import commands
from discord.role import Role

from main import Bot
from src import Context, errors
from src.interactions import (
    ApplicationCommandInteractionDataOption,
    CommandInteraction,
    InteractionResponseFlags,
    InteractionResponseType,
    PartialChannel,
    PartialRole,
)
from src.models import Channel, LoggingChannel

if TYPE_CHECKING:
    Cog = commands.Cog[Context]
else:
    Cog = commands.Cog

settings_set_group_desc = "Set the values of settings"

settings_get_group_desc = "Gets the current value of the setting"

settings_base_desc = "Set and get values of settings"

logger = logging.getLogger(__name__)


class LogicFunctions:
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    async def get_prefix_logic(self, guild: discord.Guild) -> str:
        guild = await self.bot.guild_cache.get(guild.id)
        return f"My prefix for this server is: `{guild.prefix}`"

    async def set_prefix_logic(
        self, guild: discord.Guild, new_prefix: Optional[str]
    ) -> discord.Embed:
        guild_data = await self.bot.guild_cache.get(guild.id)
        current_prefix = guild_data.prefix
        if new_prefix is None:
            await self.bot.guild_cache.update_prefix(guild.id, self.bot.default_prefix)
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
                await self.bot.guild_cache.update_prefix(guild.id, new_prefix)
                return discord.Embed(
                    title="Config updated!",
                    description=f"Server prefix updated from `{current_prefix}` to `{new_prefix}`",
                    timestamp=datetime.now(timezone.utc),
                    colour=discord.Colour(15653155),
                )

    async def get_logging_logic(
        self, guild: discord.Guild
    ) -> Union[discord.Embed, str]:
        logging_channel = await LoggingChannel.get_or_none(
            guild_id=guild.id, logger_type="main"
        )
        if logging_channel is None:
            return "Nothing has been set yet for logging!"

        return discord.Embed(
            title="Current logging channel",
            description=f"<#{logging_channel.channel_id}>",
            colour=discord.Colour(15653155),
            timestamp=datetime.now(timezone.utc),
        )

    async def set_logging_logic(
        self,
        guild: discord.Guild,
        channel_input: Optional[str],
    ) -> Union[discord.Embed, str]:
        logging_channel = await LoggingChannel.get_or_none(
            guild_id=guild.id, logger_type="main"
        )
        embed = discord.Embed(
            title="Config updated!",
            timestamp=datetime.now(timezone.utc),
            colour=discord.Colour(15653155),
        )
        if channel_input is None:
            if logging_channel is None:
                embed.description = "Logging channel not updated! It remains None"
            else:
                await logging_channel.delete()
                embed.description = f"Logging channel updated from <#{logging_channel.channel_id}> to None"
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

            db_channel = await Channel.get_or_create(id=channel.id)
            if logging_channel is None:
                original_channel = None
                logging_channel = LoggingChannel(
                    guild_id=guild.id, channel=db_channel[0], logger_type="main"
                )
            else:
                original_channel = logging_channel.channel_id
                logging_channel.channel = db_channel[0]
            await logging_channel.save()

            if original_channel is None:
                embed.description = f"Logging channel updated to {channel.mention}"
            else:
                embed.description = f"Logging channel updated from <#{original_channel}> to {channel.mention}"
            return embed

    async def get_admin_role_logic(
        self, guild: discord.Guild
    ) -> Union[discord.Embed, str]:
        db_guild = await self.bot.guild_cache.get(guild.id)
        role_id = db_guild.management_role_id
        if role_id is None:
            return "The admin role has not been set yet!"
        original_role = guild.get_role(role_id)
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
        self, guild: discord.Guild, new_role_id: Optional[str]
    ) -> discord.Embed:
        db_guild = await self.bot.guild_cache.get(guild.id)
        original_role_id = db_guild.management_role_id
        original_role = (
            guild.get_role(original_role_id) if original_role_id is not None else None
        )
        if new_role_id is None:
            await self.bot.guild_cache.update_management_role(guild.id, None)

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
            await self.bot.guild_cache.update_management_role(guild.id, new_role_id)

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
        self, ctx: Context, error: discord.DiscordException
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
            logger.error(
                f"Ignoring exception in interaction {ctx.command}:", exc_info=error
            )

    @commands.has_guild_permissions(administrator=True)
    @commands.group()
    async def setup(self, ctx: Context) -> None:
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
        self, ctx: Context, new_prefix: Optional[str] = None
    ) -> None:
        if ctx.guild is None:
            raise commands.CheckFailure("Internal error: ctx.guild was None")
        assert isinstance(ctx.author, discord.Member)
        if new_prefix is None:
            msg = await self.logic_functions.get_prefix_logic(ctx.guild)
            await ctx.send(msg)
        else:
            if new_prefix.lower() == "none":
                new_prefix = None
            msg_embed = await self.logic_functions.set_prefix_logic(
                ctx.guild, new_prefix
            )
            await ctx.send(embed=msg_embed)

    @commands.has_guild_permissions(administrator=True)
    @setup.command()
    async def admin(self, ctx: Context, role_id_input: Optional[str] = None) -> None:
        assert ctx.guild is not None
        assert isinstance(ctx.author, discord.Member)
        if role_id_input is None:
            msg = await self.logic_functions.get_admin_role_logic(ctx.guild)
        else:
            if role_id_input.lower() == "none":
                role_id_input = None
            msg = await self.logic_functions.set_admin_role_logic(
                ctx.guild, role_id_input
            )

        if isinstance(msg, discord.Embed):
            await ctx.send(embed=msg)
        else:
            await ctx.send(content=msg)

    @setup.command(name="logging")
    async def set_logging(
        self, ctx: Context, channel_input: Optional[str] = None
    ) -> None:
        if ctx.guild is None:
            raise commands.CheckFailure("Internal error: ctx.guild was None")
        assert isinstance(ctx.author, discord.Member)
        if channel_input is None:
            msg = await self.logic_functions.get_logging_logic(ctx.guild)
        else:
            if channel_input.lower() == "none":
                channel_input = None
            msg = await self.logic_functions.set_logging_logic(ctx.guild, channel_input)
        if isinstance(msg, discord.Embed):
            await ctx.send(embed=msg)
        else:
            await ctx.send(msg)

    @commands.command(name="prefix")
    async def prefix(self, ctx: Context) -> None:
        if ctx.guild is not None:
            guild = await self.bot.guild_cache.get(ctx.guild.id)
            await ctx.send(f"My prefix for this server is: `{guild.prefix}`")
        else:
            await ctx.send(f"My prefix is `{self.bot.default_prefix}`")


class SetupCogSlash(Cog):
    def __init__(self, bot: Bot, logic_functions: LogicFunctions) -> None:
        self.bot = bot
        self.logic_functions = logic_functions
        self.bot.slash_commands.update({"settings": self.handle_setup_command})

    async def respond_str_or_embed(
        self,
        interaction: CommandInteraction,
        msg: Union[str, Embed],
        ephemeral: bool = False,
    ) -> None:
        flags: Optional[InteractionResponseFlags]
        if ephemeral:
            flags = InteractionResponseFlags.EPHEMERAL
        else:
            flags = None
        if isinstance(msg, str):
            await interaction.respond(
                response_type=InteractionResponseType.ChannelMessageWithSource,
                content=msg,
                flags=flags,
            )
        else:
            await interaction.respond(
                response_type=InteractionResponseType.ChannelMessageWithSource,
                embeds=[msg],
                flags=flags,
            )

    async def clean_option(
        self, option: Optional[ApplicationCommandInteractionDataOption]
    ) -> Optional[str]:
        if option is None:
            return None
        else:
            value = option.value
        id_objects = (Role, PartialRole, Channel, PartialChannel)
        if isinstance(value, id_objects):
            return str(value.id)
        elif isinstance(value, int):
            return str(value)
        elif isinstance(value, str):
            return value
        return None

    async def try_function_send_errors(
        self,
        interaction: CommandInteraction,
        function: Callable[
            [discord.Guild, Optional[str]], Awaitable[Union[Embed, str]]
        ],
        guild: discord.Guild,
        argument: Optional[str],
    ) -> None:
        try:
            msg = await function(guild, argument)
        except (
            errors.InputContentIncorrect,
            errors.WebhookChannelNotTextChannel,
        ) as e:
            await interaction.respond(
                response_type=InteractionResponseType.ChannelMessageWithSource,
                content=str(e),
                flags=InteractionResponseFlags.EPHEMERAL,
            )
            return

        await self.respond_str_or_embed(interaction, msg)

    async def handle_setup_command(self, interaction: CommandInteraction) -> None:
        sub_groups = interaction.data.options
        if sub_groups is None:
            return
            # Partly to appease mypy, partly if discord messes up.
        sub_group_name = sub_groups[0].name
        sub_commands = sub_groups[0].options
        # Since it's a subcommand only one option, the command
        if sub_commands is None:
            return
            # Partly to appease mypy, partly if discord messes up.
        sub_command = sub_commands[0]
        sub_command_name = sub_command.name
        if interaction.guild is None:
            if interaction.guild_id:
                message = (
                    "There is an issue with how I was invited to this server."
                    "\nPlease (reinvite me)[https://messagemanager.xyz/invite] to ensure the full bot is added"
                )
            else:
                message = "This command cannot be ran in dms"
            await interaction.respond(
                response_type=InteractionResponseType.ChannelMessageWithSource,
                content=message,
                flags=InteractionResponseFlags.EPHEMERAL,
            )
            return
        has_admin = (
            interaction.member.permissions.administrator
            if interaction.member is not None
            and interaction.member.permissions is not None
            else False
        )
        if not has_admin:
            await interaction.respond(
                response_type=InteractionResponseType.ChannelMessageWithSource,
                content="You do not have the required permissions to run this command: `ADMINISTRATOR`",
                flags=InteractionResponseFlags.EPHEMERAL,
            )
            return

        assert interaction.member is not None
        if sub_group_name == "set":
            if sub_command_name == "prefix":
                option = (
                    sub_command.options[0] if sub_command.options is not None else None
                )
                prefix = option.value if option is not None else None
                await self.try_function_send_errors(
                    interaction,
                    self.logic_functions.set_prefix_logic,
                    interaction.guild,
                    prefix,
                )
            elif sub_command_name == "logging":
                option = (
                    sub_command.options[0] if sub_command.options is not None else None
                )
                channel = await self.clean_option(option)
                await self.try_function_send_errors(
                    interaction,
                    self.logic_functions.set_logging_logic,
                    interaction.guild,
                    channel,
                )
            elif sub_command_name == "admin":
                option = (
                    sub_command.options[0] if sub_command.options is not None else None
                )
                role = await self.clean_option(option)
                await self.try_function_send_errors(
                    interaction,
                    self.logic_functions.set_admin_role_logic,
                    interaction.guild,
                    role,
                )
        elif sub_group_name == "get":
            msg: Union[Embed, str]
            if sub_command_name == "prefix":
                msg = await self.logic_functions.get_prefix_logic(interaction.guild)
                await interaction.respond(
                    response_type=InteractionResponseType.ChannelMessageWithSource,
                    content=msg,
                )
            elif sub_command_name == "logging":
                msg = await self.logic_functions.get_logging_logic(interaction.guild)
                await self.respond_str_or_embed(interaction, msg, False)
            elif sub_command_name == "admin":
                msg = await self.logic_functions.get_admin_role_logic(interaction.guild)
                await self.respond_str_or_embed(interaction, msg, False)


def setup(bot: Bot) -> None:
    logic_functions = LogicFunctions(bot)
    bot.add_cog(SetupCog(bot, logic_functions))
    bot.add_cog(SetupCogSlash(bot, logic_functions))
    logger.info("Setup cog!")
