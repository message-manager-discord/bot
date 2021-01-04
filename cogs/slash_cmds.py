from typing import TYPE_CHECKING, List

from discord.ext import commands
from discord_slash import SlashCommand, SlashContext, cog_ext

from cogs.utils import shared_commands
from main import Bot

if TYPE_CHECKING:
    Cog = commands.Cog[commands.Context]
else:
    Cog = commands.Cog


guilds: List[int] = []


class Slash(Cog):
    def __init__(self, bot: Bot) -> None:
        if not hasattr(bot, "slash"):
            # Creates new SlashCommand instance to bot if bot doesn't have.
            bot.slash = SlashCommand(
                bot, override_type=True, auto_register=True, auto_delete=True
            )
        self.bot = bot
        guilds = self.bot.slash_guilds  # noqa F841
        self.bot.slash.get_cog_commands(self)

    def cog_unload(self) -> None:
        self.bot.slash.remove_cog_commands(self)

    """ Add this command again once a set of testing commands is added
    @cog_ext.cog_slash(name="beta-slash", description="How to enable slash commands for this bot!")
    async def _beta_slash(self, ctx: SlashContext) -> None:
        message = (
            "Slash commands are here!"
            "\nCurrently the slash commands on this bot are in a beta testing phase"
            "\nJoin the [support server](https://discord.gg/xFZu29t) "
            "for instructions on how to join the beta (if you have not already)"
        )
        await ctx.send(content=message, complete_hidden=True)
    """

    @cog_ext.cog_subcommand(base="info", name="info", description="Bot information")
    async def _info(self, ctx: SlashContext) -> None:
        embed = await shared_commands.create_info_embed(ctx, self.bot)
        await ctx.send(embeds=[embed])

    @cog_ext.cog_subcommand(
        base="info", name="privacy", description="Privacy information"
    )
    async def privacy(self, ctx: SlashContext) -> None:
        embed = shared_commands.create_privacy_embed()
        await ctx.send(embeds=[embed])

    @cog_ext.cog_subcommand(
        base="info", name="ping", description="Returns the current gateway latency"
    )
    async def _ping(self, ctx: SlashContext) -> None:
        await ctx.send(content=f"Gateway latency: {round(self.bot.latency*1000, 2)}ms")

    @cog_ext.cog_subcommand(base="info", name="invite", description="Bot invite")
    async def _invite(self, ctx: SlashContext) -> None:
        await ctx.send(embeds=[shared_commands.create_invite_embed()])

    @cog_ext.cog_subcommand(base="info", name="docs", description="Bot documentation")
    async def _docs(self, ctx: SlashContext) -> None:
        await ctx.send(embeds=[shared_commands.create_docs_embed()])

    @cog_ext.cog_subcommand(base="info", name="source", description="Bot's source code")
    async def _source(self, ctx: SlashContext) -> None:
        await ctx.send(embeds=[shared_commands.create_source_embed()])

    @cog_ext.cog_subcommand(
        base="info", name="support", description="Join my support server!"
    )
    async def _support(self, ctx: SlashContext) -> None:
        await ctx.send(embeds=[shared_commands.create_support_embed()])


def setup(bot: Bot) -> None:
    bot.add_cog(Slash(bot))
    print("    Slash Commands")
