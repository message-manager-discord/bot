from typing import TYPE_CHECKING

from discord.ext import commands
from discord_slash import SlashCommand, SlashContext, cog_ext

from cogs.src import shared_commands
from main import Bot

if TYPE_CHECKING:
    Cog = commands.Cog[commands.Context]
else:
    Cog = commands.Cog

guilds = [742373263593963614]


class Slash(Cog):
    def __init__(self, bot: Bot) -> None:
        if not hasattr(bot, "slash"):
            # Creates new SlashCommand instance to bot if bot doesn't have.
            bot.slash = SlashCommand(bot, override_type=True)
        self.bot = bot
        self.bot.slash.get_cog_commands(self)

    def cog_unload(self) -> None:
        self.bot.slash.remove_cog_commands(self)

    @cog_ext.cog_subcommand(base="info", name="info", guild_ids=guilds)
    async def _info(self, ctx: SlashContext) -> None:
        embed = await shared_commands.create_info_embed(ctx, self.bot)
        await ctx.send(embeds=[embed])

    @cog_ext.cog_subcommand(base="info", name="privacy", guild_ids=guilds)
    async def privacy(self, ctx: SlashContext) -> None:
        embed = shared_commands.create_privacy_embed()
        await ctx.send(embeds=[embed])

    @cog_ext.cog_subcommand(base="info", name="ping", guild_ids=guilds)
    async def _ping(self, ctx: SlashContext) -> None:
        await ctx.send(content=f"Gateway latency: {round(self.bot.latency*1000, 2)}ms")

    @cog_ext.cog_subcommand(base="info", name="invite", guild_ids=guilds)
    async def _invite(self, ctx: SlashContext) -> None:
        await ctx.send(embeds=[shared_commands.create_invite_embed()])

    @cog_ext.cog_subcommand(base="info", name="docs", guild_ids=guilds)
    async def _docs(self, ctx: SlashContext) -> None:
        await ctx.send(embeds=[shared_commands.create_docs_embed()])

    @cog_ext.cog_subcommand(base="info", name="source", guild_ids=guilds)
    async def _source(self, ctx: SlashContext) -> None:
        await ctx.send(embeds=[shared_commands.create_source_embed()])

    @cog_ext.cog_subcommand(base="info", name="support", guild_ids=guilds)
    async def _support(self, ctx: SlashContext) -> None:
        await ctx.send(embeds=[shared_commands.create_support_embed()])


def setup(bot: Bot) -> None:
    bot.add_cog(Slash(bot))
    print("    Slash Commands")
