# cogs/maincog.py

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
import platform

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

import discord

from discord.channel import TextChannel
from discord.ext import commands

from main import Bot
from src import Context
from src.analytics import success_analytics
from src.cache import GuildTuple
from src.interactions import (
    CommandInteraction,
    InteractionResponseFlags,
    InteractionResponseType,
)
from src.models import CommandUsageAnalytics

if TYPE_CHECKING:
    Cog = commands.Cog[Context]
else:
    Cog = commands.Cog

info_base_description = "Information Commands"

logger = logging.getLogger(__name__)


async def create_info_embed(
    bot: Bot, guild_id: Optional[int] = None, guild_data: Optional[GuildTuple] = None
) -> discord.Embed:
    total_seconds = (datetime.utcnow() - bot.start_time).total_seconds()
    days = total_seconds // 86400
    hours = (total_seconds - (days * 86400)) // 3600
    minutes = (total_seconds - (days * 86400) - (hours * 3600)) // 60
    seconds = total_seconds - (days * 86400) - (hours * 3600) - (minutes * 60)
    embed = discord.Embed(
        title="Info about the bot",
        colour=discord.Colour(0xC387C1),
        timestamp=datetime.now(timezone.utc),
        url="https://message.anothercat.me",
    )
    embed.add_field(name="Username", value=str(bot.user), inline=True),
    if guild_id is not None:
        if guild_data is None:
            guild_data = await bot.guild_cache.get(guild_id)
            embed.add_field(name="Prefix", value=f"`{guild_data.prefix}`", inline=True),

    embed.add_field(name="Version", value=bot.version, inline=True),
    embed.add_field(
        name="Docs",
        value="[The Docs](https://message.anothercat.me/docs)",
        inline=True,
    ),
    embed.add_field(
        name="Support Invite",
        value="[Support Server](https://discord.gg/xFZu29t)",
        inline=True,
    )
    embed.add_field(
        name="Developer",
        value="[Another Cat](https://github.com/AnotherCat)",
        inline=True,
    ),  # The developer (me), Must not be changed, as per the LICENSE
    embed.add_field(name="Discord.py Version", value=discord.__version__, inline=True),
    embed.add_field(
        name="Python Version", value=platform.python_version(), inline=True
    ),

    embed.add_field(
        name="Uptime",
        value=f"{int(days)} days {int(hours)} hours {int(minutes)} minutes {int(seconds)} seconds",
        inline=True,
    ),
    embed.add_field(name="System", value=platform.system(), inline=True),
    embed.add_field(name="Number of Servers", value=str(len(bot.guilds)), inline=True)
    embed.set_thumbnail(url=f"{bot.user.avatar_url}")
    return embed


def create_privacy_embed() -> discord.Embed:
    embed = discord.Embed(
        title="Privacy Policy",
        description="We do store data. Please read our privacy policy.",
        url="https://message.anothercat.me/privacy",
        colour=discord.Colour.red(),
        timestamp=datetime.now(timezone.utc),
    )
    embed.add_field(
        name="Where to find the privacy policy",
        value="Click [here for the privacy policy](https://message.anothercat.me/privacy)",
    )
    return embed


def create_invite_embed() -> discord.Embed:
    return discord.Embed(
        title="Invite me to your server!",
        description="[Click here](https://discord.com/api/oauth2/authorize?client_id=735395698278924359&permissions=515933326400&scope=bot%20applications.commands) to invite me!",
        url="https://discord.com/api/oauth2/authorize?client_id=735395698278924359&permissions=515933326400&scope=bot%20applications.commands",
        colour=discord.Colour(0xC387C1),
        timestamp=datetime.now(timezone.utc),
    )


def create_docs_embed() -> discord.Embed:
    return discord.Embed(
        title="Docs!",
        description="My docs are [here](https://message.anothercat.me/docs)",
        url="https://message.anothercat.me/docs",
        colour=discord.Colour(0xC387C1),
        timestamp=datetime.now(timezone.utc),
    )


def create_source_embed() -> discord.Embed:
    return discord.Embed(
        title="Source Code!",
        description="My [source code](https://github.com/AnotherCat/message-manager)",
        url="https://github.com/AnotherCat/message-manager",
        colour=discord.Colour(0xC387C1),
        timestamp=datetime.now(timezone.utc),
    )


def create_support_embed() -> discord.Embed:
    return discord.Embed(
        title="Join my support server for support!",
        description="Click [here](https://discord.gg/xFZu29t) to join!",
        url="https://discord.gg/xFZu29t",
        colour=discord.Colour(0xC387C1),
        timestamp=datetime.now(timezone.utc),
    )


class MainCog(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.bot.slash_commands.update({"info": self.handle_info_command})

    async def cog_check(self, ctx: Context) -> bool:
        if isinstance(ctx.channel, TextChannel) and ctx.guild:
            perms = ctx.channel.permissions_for(ctx.guild.me)
        else:
            return True
        return perms.send_messages and perms.embed_links

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        # Print the bot invite link
        logger.info(
            f"https://discord.com/api/oauth2/authorize?client_id={self.bot.user.id}&permissions=515933326400&scope=applications.commands%20bot"
        )
        logger.info(f"Logged on as {self.bot.user}!")
        self.bot.load_time = datetime.utcnow()

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild) -> None:
        channel = None
        assert guild.me is not None
        if guild.system_channel is None:
            for c in guild.text_channels:
                perm = c.permissions_for(guild.me)
                if perm.send_messages and perm.embed_links:
                    channel = c
                    break
        else:
            system_channel = guild.system_channel
            perms = system_channel.permissions_for(guild.me)
            if perms.send_messages and perms.embed_links:
                channel = system_channel
            else:
                for c in guild.text_channels:
                    perm = c.permissions_for(guild.me)
                    if perm.send_messages and perm.embed_links:
                        channel = c
                        break
        if channel is not None:
            db_guild = await self.bot.guild_cache.get(guild.id)
            prefix = db_guild.prefix
            embed = discord.Embed(
                title="Hi there!",
                colour=discord.Colour(16761035),
                description="Thank you for inviting me to your server!",
                timestamp=datetime.now(timezone.utc),
                url="https://message.anothercat.me",
            )
            embed.add_field(
                name="Prefix", value=f"My prefix here is: `{prefix}`", inline=False
            )
            embed.add_field(
                name="Help",
                value="Have a look at my [docs](https://message.anothercat.me/docs) "
                "If you've got any questions or join our [support server](https://discord.gg/xFZu29t)",
                inline=False,
            )
            embed.add_field(
                name="Privacy Policy",
                value="Please read my [privacy policy](). \nBy using the bot you are confirming that you have read the privacy policy.",
            )
            await channel.send(embed=embed)

    @commands.command(
        name="help", help="Responds with an embed with all the commands and options"
    )
    async def help(self, ctx: Context, option: Optional[str] = None) -> None:
        if option is None or option.lower() != "setup":
            embed = discord.Embed(
                title="Help!",
                colour=16761035,
                timestamp=datetime.now(timezone.utc),
                url="https://message.anothercat.me/docs",
            )
            embed.add_field(
                name=self.bot.command_with_prefix(ctx, "ping"),
                value="Replies with the latency of the bot",
                inline=True,
            )
            embed.add_field(
                name=self.bot.command_with_prefix(ctx, "help"),
                value="Displays this view.",
                inline=True,
            ),
            embed.add_field(
                name=self.bot.command_with_prefix(ctx, "info"),
                value="Displays info about the bot",
                inline=True,
            ),
            embed.add_field(
                name=self.bot.command_with_prefix(ctx, "send [channel_id] [content]"),
                value="Sends a message from the bot in the specificed channel",
                inline=True,
            )
            embed.add_field(
                name=self.bot.command_with_prefix(
                    ctx, "edit [channel_id] [message_id] [new_content]"
                ),
                value="Edits a message, message **must** be from the bot",
                inline=True,
            )
            embed.add_field(
                name=self.bot.command_with_prefix(
                    ctx, "fetch [channel_id] [message_id]"
                ),
                value="Returns raw content of the message in a .txt file",
                inline=True,
            )
            embed.add_field(
                name=self.bot.command_with_prefix(
                    ctx, "delete [channel_id] [message_id]"
                ),
                value="Deletes the message from the bot. **Must** be from the bot",
                inline=True,
            )
            embed.add_field(
                name=self.bot.command_with_prefix(ctx, "setup"),
                value="Starts setup, Requires the user to have admin permissions",
                inline=True,
            )
            embed.add_field(
                name="Embeds",
                value="Find the documentation for sending embeds [here](https://message.anothercat.me/docs/features/messages) (it's too big to fit here now)",
            )
            await ctx.send(embed=embed)
        else:
            try:
                setup_command = self.bot.get_command("setup")
                if setup_command is not None:
                    await ctx.invoke(setup_command)
                return
            except Exception:
                help_command = self.bot.get_command("help")
                if help_command is not None:
                    await ctx.invoke(help_command)

        await success_analytics(ctx)

    async def handle_info_command(self, interaction: CommandInteraction) -> None:
        sub_commands = interaction.data.options
        if sub_commands is None:
            return
            # Partly to appease mypy, partly if discord messes up.
        sub_name = sub_commands[0].name
        # Since it's a subcommand only one option, the command
        if sub_name == "info":
            embed = await create_info_embed(bot=self.bot, guild_id=interaction.guild_id)
            await interaction.respond(
                response_type=InteractionResponseType.ChannelMessageWithSource,
                embeds=[embed],
                flags=InteractionResponseFlags.EPHEMERAL,
            )
        elif sub_name == "ping":
            await interaction.respond(
                response_type=InteractionResponseType.ChannelMessageWithSource,
                content=f"Gateway latency: {round(self.bot.latency*1000, 2)}ms",
                flags=InteractionResponseFlags.EPHEMERAL,
            )
        elif sub_name == "privacy":
            embed = create_privacy_embed()
            await interaction.respond(
                response_type=InteractionResponseType.ChannelMessageWithSource,
                flags=InteractionResponseFlags.EPHEMERAL,
                embeds=[embed],
            )
        elif sub_name == "invite":

            await interaction.respond(
                response_type=InteractionResponseType.ChannelMessageWithSource,
                flags=InteractionResponseFlags.EPHEMERAL,
                embeds=[create_invite_embed()],
            )
        elif sub_name == "docs":
            await interaction.respond(
                response_type=InteractionResponseType.ChannelMessageWithSource,
                flags=InteractionResponseFlags.EPHEMERAL,
                embeds=[create_docs_embed()],
            )
        elif sub_name == "source":
            await interaction.respond(
                response_type=InteractionResponseType.ChannelMessageWithSource,
                flags=InteractionResponseFlags.EPHEMERAL,
                embeds=[create_source_embed()],
            )

        elif sub_name == "support":
            await interaction.respond(
                response_type=InteractionResponseType.ChannelMessageWithSource,
                flags=InteractionResponseFlags.EPHEMERAL,
                embeds=[create_support_embed()],
            )
        if sub_name in (
            "info",
            "ping",
            "privacy",
            "invite",
            "docs",
            "source",
            "support",
        ):
            await CommandUsageAnalytics.create(
                guild_id=interaction.guild_id,
                command_name=["info", sub_name],
                slash=True,
            )

    # Create the info command.
    @commands.command(name="info")
    async def info(self, ctx: Context) -> None:
        guild_id = None if ctx.guild is None else ctx.guild.id
        embed = await create_info_embed(
            bot=self.bot, guild_id=guild_id, guild_data=ctx.guild_data
        )
        await ctx.send(embed=embed)
        await success_analytics(ctx)

    @commands.command(name="ping")
    async def ping(self, ctx: Context) -> None:
        await ctx.send(f"Gateway latency: {round(self.bot.latency*1000, 2)}ms")
        await success_analytics(ctx)

    @commands.command()
    async def privacy(self, ctx: Context) -> None:
        embed = create_privacy_embed()
        await ctx.send(embed=embed)
        await success_analytics(ctx)

    @commands.command()
    async def invite(self, ctx: Context) -> None:
        await ctx.send(embed=create_invite_embed())
        await success_analytics(ctx)

    @commands.command()
    async def docs(self, ctx: Context) -> None:
        await ctx.send(embed=create_docs_embed())
        await success_analytics(ctx)

    @commands.command()
    async def source(self, ctx: Context) -> None:
        await ctx.send(embed=create_source_embed())
        await success_analytics(ctx)

    @commands.command()
    async def support(self, ctx: Context) -> None:
        await ctx.send(embed=create_support_embed())
        await success_analytics(ctx)


def setup(bot: Bot) -> None:
    bot.add_cog(MainCog(bot))
    logger.info("Main cog!")
