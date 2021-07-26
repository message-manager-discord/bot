# main.py
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

import asyncio
import datetime
import logging

from asyncio.futures import Future
from typing import (
    TYPE_CHECKING,
    Any,
    Awaitable,
    Callable,
    Dict,
    List,
    Optional,
    Sequence,
    Tuple,
    Union,
)

import aiohttp
import discord
import sentry_sdk

from discord.ext import commands
from tortoise import Tortoise

import config

from src import Context, PartialGuildCache
from src.errors import NoComponents
from src.interactions import (
    ActionRow,
    Button,
    CommandInteraction,
    ComponentInteraction,
    Interaction,
    InteractionResponseFlags,
    InteractionResponseType,
    InteractionType,
    Select,
)
from tortoise_config import TORTOISE_ORM

__version__ = "v2.1"

if TYPE_CHECKING:
    BotBase = commands.Bot[Context]
else:
    BotBase = commands.Bot


class Bot(BotBase):
    def __init__(
        self, default_prefix: str, self_hosted: bool = False, **kwargs: Any
    ) -> None:

        super().__init__(  # type: ignore
            case_insensitive=True,
            chunk_guilds_on_startup=False,
            intents=discord.Intents(guilds=True, members=False, messages=True),
            activity=discord.Game(name="Watching our important messages!"),
            help_command=None,
            **kwargs,
        )
        self.default_prefix = default_prefix
        self.self_hosted = self_hosted
        self.start_time = datetime.datetime.utcnow()
        self.session: aiohttp.ClientSession
        self.version = __version__
        self.guild_cache: PartialGuildCache
        self.load_time: datetime.datetime
        self.dbl_token: str
        self.dboats_token: str
        self.del_token: str
        self.dbgg_token: str
        self.topgg_token: str
        self.slash_commands: Dict[str, Callable] = {}
        self.component_listeners: Dict[
            str, Tuple[Future[Any], Callable[[ComponentInteraction], Awaitable[bool]]]
        ] = {}
        self.removed_listeners: List[str] = []
        self.inject_parsers()

    async def init_db(self) -> None:
        await Tortoise.init(config=TORTOISE_ORM)
        self.guild_cache = PartialGuildCache(
            capacity=config.guild_cache_max,
            drop_amount=config.guild_cache_drop,
        )

    async def start(self, *args, **kwargs) -> None:  # type: ignore
        self.session = aiohttp.ClientSession()

        await self.init_db()
        await super().start(*args, **kwargs)

    async def close(self) -> None:
        await Tortoise.close_connections()
        await super().close()

    def command_with_prefix(self, ctx: Context, command_name: str) -> str:
        if str(self.user.id) in ctx.prefix:
            if isinstance(ctx.me, discord.Member):
                return f"`@{ctx.me.nick or ctx.me.name} {command_name}`"
            else:
                return f"`@{ctx.me.name} {command_name}`"
        else:
            return f"`{ctx.prefix}{command_name}`"

    async def process_commands(self, message: discord.Message) -> None:
        if message.author.bot:
            return
        ctx = await self.get_context(message, cls=Context)
        if ctx.command is None:
            return
        if message.guild is not None:
            await ctx.fetch_guild_data()
        await self.invoke(ctx)

    async def on_command_interaction(self, interaction: CommandInteraction) -> None:
        call = self.slash_commands[interaction.data.name]
        try:
            await call(interaction)
        except Exception as e:
            self.dispatch("slash_command_error", interaction, e)

    async def on_slash_command_error(
        self, interaction: CommandInteraction, error: Exception
    ) -> None:
        name = interaction.data.name
        logger.error(f"Ignoring exception in interaction {name}:", exc_info=error)
        if not interaction.responded:
            await interaction.respond(
                content=(
                    "There was an unknown error!\n"
                    f"Report a bug or get support from the support server at `/info support`\n"
                    f"Error: {error}"
                ),
                response_type=InteractionResponseType.ChannelMessageWithSource,
                flags=InteractionResponseFlags.EPHEMERAL,
            )
        else:
            await interaction.create_followup(
                content=(
                    "There was an unknown error!\n"
                    f"Report a bug or get support from the support server at `/info support`\n"
                    f"Error: {error}"
                ),
                flags=InteractionResponseFlags.EPHEMERAL,
            )

    def parse_interaction_create(self, data: Dict[Any, Any]) -> None:
        interaction = Interaction(data=data, state=self._connection)  # type: ignore
        if data["type"] == InteractionType.APPLICATION_COMMAND:
            interaction = CommandInteraction(data=data, state=self._connection)  # type: ignore
            self.dispatch("command_interaction", interaction)
        elif data["type"] == InteractionType.MESSAGE_COMPONENT:
            interaction = ComponentInteraction(data=data, state=self._connection)  # type: ignore
            self.dispatch("component_interaction", interaction)
            self.dispatch("check_component_interaction", interaction)

    async def on_check_component_interaction(
        self, interaction: ComponentInteraction
    ) -> None:
        await self.dispatch_components(interaction)

    def parse_unhandled_event(self, data: Dict[Any, Any]) -> None:
        pass

    def inject_parsers(self) -> None:
        parsers = {
            "INTERACTION_CREATE": self.parse_interaction_create,
            "APPLICATION_COMMAND_CREATE": self.parse_unhandled_event,
            "APPLICATION_COMMAND_DELETE": self.parse_unhandled_event,
            "APPLICATION_COMMAND_UPDATE": self.parse_unhandled_event,
        }
        self._connection.parsers.update(parsers)  # type: ignore

    def clean_components(
        self,
        components: Union[
            Button, Select, Sequence[Union[Button, Select, ActionRow]], ActionRow
        ],
    ) -> Optional[List[Union[Button, Select]]]:
        result: List[Union[Button, Select]] = []
        if isinstance(components, (Button, Select)):
            result.append(components)
        elif isinstance(components, ActionRow):
            result.extend(components.components)

        elif isinstance(components, List):
            for components_in_list in components:
                next_clean = self.clean_components(components_in_list)
                if next_clean is not None:
                    result.extend(next_clean)
        return result

    def wait_for_components(
        self,
        components: Union[
            Button, Select, Sequence[Union[Button, Select, ActionRow]], ActionRow
        ],
        check: Callable[[ComponentInteraction], Awaitable[bool]] = None,
        timeout: float = None,
    ) -> "Future[Any]":
        cleaned_components = self.clean_components(components)
        if cleaned_components is None or len(cleaned_components) == 0:
            raise NoComponents()
        future = self.loop.create_future()
        if check is None:

            async def _check(interaction: ComponentInteraction) -> bool:
                return True

            check = _check
        for component in cleaned_components:
            self.component_listeners[component.custom_id] = (future, check)

        if len(self.component_listeners) > 1000:
            logger.warning("Bot.component_listeners exceeded 1000")

        return asyncio.wait_for(future, timeout)

    async def dispatch_components(self, interaction: ComponentInteraction) -> None:
        custom_id = interaction.component.custom_id
        listener = self.component_listeners.get(custom_id, None)
        no_response = False
        if listener is not None:
            future, condition = listener
            if future.done():
                self.component_listeners.pop(custom_id)
                no_response = True
            else:
                result = await condition(interaction)
                if result:
                    future.set_result(interaction)
                    self.component_listeners.pop(custom_id)
                else:
                    no_response = True

        else:
            no_response = True
        if no_response:
            if interaction.responded:
                return
            if interaction.message.components is None:
                # ephemeral message
                await interaction.respond(
                    response_type=InteractionResponseType.ChannelMessageWithSource,
                    content="❗That component could not be found!\n This could be due to an outage, please try the original action again.",
                    flags=InteractionResponseFlags.EPHEMERAL,
                )
            else:
                components = interaction.message.components
                for component in components:
                    if isinstance(component, ActionRow):
                        for next_component in component.components:
                            if isinstance(next_component, (Select, Button)):
                                if (
                                    next_component.custom_id
                                    == interaction.component.custom_id
                                ):
                                    next_component.disabled = True
                    if isinstance(component, (Select, Button)):
                        if component.custom_id == interaction.component.custom_id:
                            component.disabled = True
                await interaction.respond(
                    content=interaction.message.content,
                    embeds=interaction.message.embeds,
                    response_type=InteractionResponseType.UpdateMessage,
                    components=components,
                )
                await interaction.create_followup(
                    content="❗That component could not be found!\n This could be due to an outage, please try the original action again.",
                    flags=InteractionResponseFlags.EPHEMERAL,
                )

    async def check_component_listener(self, custom_id: str) -> None:
        future, check = self.component_listeners[custom_id]
        if future.done():
            self.removed_listeners.append(custom_id)

    async def clean_component_listeners(self) -> None:
        for listener in self.component_listeners:
            await self.check_component_listener(listener)
        for custom_id in self.removed_listeners:
            self.component_listeners.pop(custom_id)
        self.removed_listeners = []

    async def on_error(self, event_method: str, *args: Any, **kwargs: Any) -> None:
        logger.error(f"Ignoring exception in {event_method}", exc_info=True)

    async def on_command_error(self, context: Context, exception: Exception) -> None:
        command = context.command
        if command and command.has_error_handler():
            return

        cog = context.cog
        if cog and cog.has_error_handler():
            return

        logger.error(
            f"Ignoring exception in command {context.command}:", exc_info=exception
        )


logger = logging.getLogger(__name__)
logging.basicConfig(
    format="%(asctime)s:%(levelname)s:%(name)s: %(message)s", level=logging.INFO
)
# Setup sentry
if hasattr(config, "sentry_dsn"):
    logger.info("Started sentry")

    sentry_sdk.init(
        config.sentry_dsn,
        release=f"bot@{__version__}",
        traces_sample_rate=0.5,
    )


async def get_custom_prefix(bot: Bot, message: discord.Message) -> List[str]:

    if message.guild is not None:
        guild = await bot.guild_cache.get(
            message.guild.id
        )  # Fetch current server prefix from database
        prefix = [guild.prefix]
    else:
        prefix = [config.default_prefix, ""]

    return commands.when_mentioned_or(*prefix)(bot, message)


def run() -> None:
    bot = Bot(
        owner_ids=config.owners,
        default_prefix=config.default_prefix,
        self_hosted=config.self_host,
        command_prefix=get_custom_prefix,
    )

    extensions = [
        "cogs.maincog",
        "cogs.messages",
        "cogs.stats",
        "cogs.admin",
        "cogs.setup",
        "cogs.component_management",
    ]
    if not config.self_host:
        bot.dbl_token = config.dbl_token
        bot.dboats_token = config.dboats_token
        bot.del_token = config.def_token
        bot.dbgg_token = config.dbgg_token
        bot.topgg_token = config.topgg_token
        extensions.append("jishaku")
        extensions.append("cogs.listing")
    logger.info("Loading extensions...")
    for extension in extensions:
        bot.load_extension(extension)
    bot.run(config.token)


if __name__ == "__main__":
    run()
