import platform
import typing

from datetime import datetime, timezone

import discord

from discord.ext.commands import Context
from discord_slash import SlashContext

from main import Bot


async def create_info_embed(
    ctx: typing.Union[Context, SlashContext], bot: Bot
) -> discord.Embed:
    prefix = await bot.db.get_prefix(ctx.guild)
    total_seconds = (datetime.utcnow() - bot.start_time).total_seconds()
    days = total_seconds // 86400
    hours = (total_seconds - (days * 86400)) // 3600
    minutes = (total_seconds - (days * 86400) - (hours * 3600)) // 60
    seconds = total_seconds - (days * 86400) - (hours * 3600) - (minutes * 60)
    embed = discord.Embed(
        title="Info about the bot",
        colour=discord.Colour(0xC387C1),
        timestamp=datetime.now(timezone.utc),
        url="https://messagemanager.xyz",
    )
    embed.add_field(name="Username", value=str(bot.user), inline=True),
    embed.add_field(name="Prefix", value=f"`{prefix}`", inline=True),
    embed.add_field(name="Version", value=bot.version, inline=True),
    embed.add_field(
        name="Docs",
        value="[The Docs](https://docs.messagemanager.xyz)",
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
        url="https://github.com/AnotherCat/message-bot/blob/master/PRIVACY_POLICY.md",
        colour=discord.Colour.red(),
        timestamp=datetime.now(timezone.utc),
    )
    embed.add_field(
        name="Where to find the privacy policy",
        value="My privacy policy is located on [github](https://github.com/AnotherCat/message-bot/blob/master/PRIVACY_POLICY.md)",
    )
    return embed


def create_invite_embed() -> discord.Embed:
    return discord.Embed(
        title="Invite me to your server!",
        description="[Click here](https://discord.com/api/oauth2/authorize?client_id=735395698278924359&permissions=537250880&scope=bot%20applications.commands) to invite me!",
        url="https://discord.com/api/oauth2/authorize?client_id=735395698278924359&permissions=537250880&scope=bot%20applications.commands",
        colour=discord.Colour(0xC387C1),
        timestamp=datetime.now(timezone.utc),
    )


def create_docs_embed() -> discord.Embed:
    return discord.Embed(
        title="Docs!",
        description="My docs are [here](https://docs.messagemanager.xyz)",
        url="https://docs.messagemanager.xyz",
        colour=discord.Colour(0xC387C1),
        timestamp=datetime.now(timezone.utc),
    )


def create_source_embed() -> discord.Embed:
    return discord.Embed(
        title="Source Code!",
        description="My [source code](https://github.com/AnotherCat/message-bot)",
        url="https://github.com/AnotherCat/message-bot",
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
