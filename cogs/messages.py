# cogs/messages.py

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
import json
import os
import sys
import traceback
import logging

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Dict, List, NamedTuple, Optional, TypedDict, Union

import discord

from discord.ext import commands

from main import Bot
from src import Context, checks, errors, send_log_once
from src.interactions import (
    ActionRow,
    Button,
    ButtonStyle,
    ComponentInteraction,
    InteractionResponseFlags,
    InteractionResponseType,
    PartialEmoji,
    send_message_components,
)

if TYPE_CHECKING:
    Cog = commands.Cog[Context]
else:
    Cog = commands.Cog


logger = logging.getLogger(__name__)

class ComfirmEmbedTuple(NamedTuple):
    confirmation_embed: discord.Embed
    finish_embed: discord.Embed
    content: str
    original_content: Optional[str]


class FieldDict(TypedDict):
    name: str
    value: str
    inline: bool


async def confirm(
    bot: Bot,
    embed: discord.Embed,
    finished_embed: discord.Embed,
    content: str,
    channel_id: int,
    author_id: int,
    initial_message_id: int,
    content_name: str,
    original_content: Optional[str] = None,
) -> bool:
    base_custom_id = f"{author_id}-{initial_message_id}"
    cancel_custom_id = f"{base_custom_id}-n"
    confirm_custom_id = f"{base_custom_id}-y"
    components = [
        ActionRow(
            components=[
                Button(
                    style=ButtonStyle.Primary,
                    emoji=PartialEmoji(id=None, name="✅"),
                    label="Confirm",
                    custom_id=confirm_custom_id,
                ),
                Button(
                    style=ButtonStyle.Danger,
                    emoji=PartialEmoji(id=None, name="❌"),
                    label="Cancel",
                    custom_id=cancel_custom_id,
                ),
            ]
        )
    ]

    await send_message_components(
        embed=embed, channel_id=channel_id, components=components, state=bot._connection  # type: ignore
    )

    async def check(interaction: ComponentInteraction) -> bool:
        if interaction.author.id != author_id:
            await interaction.respond(
                response_type=InteractionResponseType.ChannelMessageWithSource,
                content="❗Only the user who ran that command can use these buttons!",
                flags=InteractionResponseFlags.EPHEMERAL,
            )
            return False
        else:
            return True

    button_interaction: ComponentInteraction = await bot.wait_for_components(
        components=components, check=check
    )
    if button_interaction.component.custom_id == confirm_custom_id:
        state = "a success"
        return_value = True
        colour = discord.Colour.green()
    else:
        state = "cancelled"
        colour = discord.Colour.red()
        if original_content:
            finished_embed.add_field(
                name=f"New {content_name}", value=content, inline=False
            )
            finished_embed.add_field(
                name=f"Original {content_name}", value=original_content, inline=False
            )
        else:
            finished_embed.add_field(name=content_name, value=content)
        return_value = False
    finished_embed.colour = colour
    finished_embed.title = finished_embed.title.format(state=state)  # type: ignore
    for component in components[0].components:
        component.disabled = True
    await button_interaction.respond(
        response_type=InteractionResponseType.UpdateMessage,
        embeds=[finished_embed],
        components=components,
    )
    return return_value


class MessagesCog(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    async def cog_check(self, ctx: Context) -> bool:
        return await checks.check_if_manage_role(self.bot, ctx)

    async def cog_command_error(
        self, ctx: Context, error: discord.DiscordException
    ) -> None:
        if isinstance(
            error,
            (
                errors.MissingPermission,
                errors.ContentError,
                errors.DifferentServer,
                errors.ConfigNotSet,
                errors.InputContentIncorrect,
                errors.DifferentAuthor,
                errors.JSONFailure,
                commands.NoPrivateMessage,
            ),
        ):
            await ctx.send(error)
        elif isinstance(error, asyncio.TimeoutError):
            await ctx.send("Timedout, Please try again.")
        elif isinstance(error, commands.ChannelNotFound):
            await ctx.send(
                "I could not find that channel!\n"
                "Please check that the id is correct\n"
                "Run the command without pararameters to be guided through the input!"
            )
        else:
            await ctx.send(
                "There was an unknown error!\n"
                f"Report a bug or get support from the support server at {self.bot.command_with_prefix(ctx, 'support')}\n"
                f"Error: {error}"
            )

            logger.error(f'Ignoring exception in command {ctx.command}:', exc_info = error)

    async def check_channel(
        self, ctx: Context, channel: Optional[discord.TextChannel]
    ) -> discord.TextChannel:
        def is_correct(m: discord.Message) -> bool:
            return m.author == ctx.author

        if channel is None:
            await ctx.send("What is the channel?")
            get_channel = await self.bot.wait_for("message", check=is_correct)
            get_channel.content
            channel = await commands.TextChannelConverter().convert(
                ctx, get_channel.content
            )
        assert ctx.guild is not None
        assert ctx.guild.me is not None
        assert isinstance(ctx.author, discord.Member)
        perms = channel.permissions_for(ctx.guild.me)
        sender_perms = channel.permissions_for(ctx.author)
        if not perms.view_channel:
            raise errors.InputContentIncorrect(
                "I do not have the the `View Messages` permission in that channel!"
            )
        elif not (perms.send_messages and perms.embed_links):
            raise errors.InputContentIncorrect(
                "I do not have the the `Send Message` and `Embed Links` permission in that channel!"
            )
        elif not sender_perms.view_channel:
            raise errors.InputContentIncorrect(
                "You don't have the `View Messages` permissions in that channel!"
            )

        return channel

    async def check_content(
        self,
        ctx: Context,
        content: Optional[str],
        ask_message: str = "What is the content of the message to be?",
    ) -> str:
        def is_correct(m: discord.Message) -> bool:
            return m.author == ctx.author

        if content is None or content == "":
            await ctx.send(ask_message)
            get_content = await self.bot.wait_for("message", check=is_correct)
            content = get_content.content
            return content
        else:
            return content

    async def check_message_id(
        self,
        ctx: Context,
        channel: Union[discord.TextChannel, str, int],
        message_id: Optional[int],
    ) -> discord.Message:
        if not isinstance(channel, discord.TextChannel):
            channel = await commands.TextChannelConverter().convert(ctx, str(channel))

        def is_correct(m: discord.Message) -> bool:
            return m.author == ctx.author

        async def message_or_error(
            channel: discord.TextChannel, message_id: Union[int, str]
        ) -> discord.Message:
            try:
                return await channel.fetch_message(int(message_id))
            except Exception as e:
                if isinstance(e, discord.NotFound):
                    raise errors.InputContentIncorrect("I can't find that message!")
                elif isinstance(e, ValueError):
                    raise errors.InputContentIncorrect("That is not a message id!")
                else:
                    raise e

        if message_id is None:
            await ctx.send("What is the id of the message?")

            get_message = await self.bot.wait_for("message", check=is_correct)

            message = await message_or_error(channel, get_message.content)
            return message
        else:
            message = await message_or_error(channel, message_id)
            return message

    async def send_message_info_embed(
        self,
        ctx: Context,
        command_type: str,
        author: Union[discord.Member, discord.User],
        content: str,
        message: discord.Message,
        channel: discord.TextChannel,
    ) -> None:
        if ctx.guild is None:
            raise commands.CheckFailure("Internal error: ctx.guild was None")
        title = "Sent"
        list_content: Dict[str, FieldDict] = {
            "author": {"name": "Author", "value": author.mention, "inline": True},
            "channel": {"name": "Channel", "value": channel.mention, "inline": True},
            "content": {"name": "Content", "value": content, "inline": True},
        }
        if command_type == "edit":
            title = "Edited"
            list_content["original_content"] = {
                "name": "Original Content",
                "value": message.content,
                "inline": False,
            }
            list_content["content"]["name"] = "New Content"
            list_content["author"]["name"] = "Editor"
        elif command_type == "delete":
            title = "Deleted"
            list_content["author"]["name"] = "Deleter"
        elif command_type == "fetch":
            title = "Fetched"
            del list_content["author"]

        embed = discord.Embed(
            title=f"{title} the message!",
            colour=discord.Colour(0xC387C1),
            timestamp=datetime.now(timezone.utc),
        )
        for key in list_content:
            embed.add_field(
                name=list_content[key]["name"],
                value=list_content[key]["value"],
                inline=list_content[key]["inline"],
            )
        if len(content) >= 500 or len(message.content) >= 500:
            with open("content.txt", "w+") as f:
                if command_type == "edit":
                    f.write(
                        f"Original Content:\n\n{message.content}\n\nNew Content:\n\n{content}"
                    )
                    del list_content["content"]
                    del list_content["original_content"]
                elif command_type == "fetch":
                    f.write(f"Content:\n\n{content}")
                    del list_content["content"]
                else:
                    f.write(f"Content:\n\n{content}")
                    del list_content["content"]
            embed = discord.Embed(
                title=f"{title} the message!",
                colour=discord.Colour(0xC387C1),
                timestamp=datetime.now(timezone.utc),
            )
            for key in list_content:
                embed.add_field(
                    name=list_content[key]["name"],
                    value=list_content[key]["value"],
                    inline=list_content[key]["inline"],
                )
            await send_log_once(
                guild_id=ctx.guild.id,
                bot=self.bot,
                logger_type="main",
                embeds=[embed],
                file=discord.File("content.txt", filename="content.txt"),
            )
            os.remove("content.txt")
        else:
            await send_log_once(
                guild_id=ctx.guild.id, bot=self.bot, logger_type="main", embeds=[embed]
            )

    def generate_confirmation_embeds(
        self,
        content: str,
        original_content: Optional[str],
        channel: discord.TextChannel,
        author: Union[discord.Member, discord.User],
        action: str,
        message_type: str,
        content_name: str,
        message_link: Optional[str],
    ) -> ComfirmEmbedTuple:
        description = "Click above to jump to message" if message_link else None
        confirmation_embed = discord.Embed(
            title="Please check if this is correct.",
            colour=discord.Colour(0xC387C1),
        )
        if description is not None:
            confirmation_embed.description = description
        if message_link:
            confirmation_embed.url = message_link
        confirmation_embed.add_field(name="Author", value=author.mention)
        confirmation_embed.add_field(name="Channel", value=channel.mention)
        if len(content) > 150:
            cleaned_content = f"{content[:150]} ..."
        else:
            cleaned_content = content
        cleaned_original_content: Optional[str]
        if original_content:
            if len(original_content) > 150:
                cleaned_original_content = f"{original_content[:150]} ..."
            else:
                cleaned_original_content = original_content
            confirmation_embed.add_field(
                name=f"New {content_name}", value=cleaned_content, inline=False
            )
            confirmation_embed.add_field(
                name=f"Original {content_name}",
                value=cleaned_original_content,
                inline=False,
            )
        else:
            confirmation_embed.add_field(name=content_name, value=cleaned_content)
            cleaned_original_content = None

        finish_embed = discord.Embed(
            title=f"{action} the {message_type} was {'{state}'}.",
        )
        if description is not None:
            finish_embed.description = description
        if message_link:
            finish_embed.url = message_link
        finish_embed.add_field(name="Author", value=author.mention)
        finish_embed.add_field(name="Channel", value=channel.mention)
        return ComfirmEmbedTuple(
            confirmation_embed=confirmation_embed,
            finish_embed=finish_embed,
            content=cleaned_content,
            original_content=cleaned_original_content,
        )

    @commands.command(name="send")
    async def send(
        self,
        ctx: Context,
        channel: Optional[discord.TextChannel] = None,
        *,
        content: Optional[str] = None,
    ) -> None:
        channel = await self.check_channel(ctx, channel)  # Get the channel.
        if channel.guild != ctx.guild:
            raise errors.DifferentServer()
        content = await self.check_content(ctx, content)
        if content[1:4] == "```" and content[-3:] == "```":
            content = content[4:-3]

        embeds = self.generate_confirmation_embeds(
            content=content,
            original_content=None,
            channel=channel,
            author=ctx.author,
            action="Sending",
            message_type="message",
            message_link=None,
            content_name="Content",
        )

        success = await confirm(
            bot=self.bot,
            embed=embeds.confirmation_embed,
            finished_embed=embeds.finish_embed,
            content=embeds.content,
            channel_id=ctx.channel.id,
            author_id=ctx.author.id,
            initial_message_id=ctx.message.id,
            content_name="Content",
        )
        if success:
            msg = await channel.send(content)
            await self.send_message_info_embed(
                ctx, "Send", ctx.author, content, msg, channel
            )

    # Create the edit command. This command will edit the specificed message. (Message must be from the bot)
    @commands.command(name="edit")
    async def edit(
        self,
        ctx: Context,
        channel: Optional[discord.TextChannel] = None,
        message_id: Optional[int] = None,
        *,
        content: Optional[str] = None,
    ) -> None:
        channel = await self.check_channel(ctx, channel)
        if channel.guild != ctx.guild:
            raise errors.DifferentServer()

        msg = await self.check_message_id(ctx, channel, message_id)
        if msg.author != ctx.guild.me:
            raise errors.DifferentAuthor()

        content = await self.check_content(ctx, content)
        if content[1:4] == "```" and content[-3:] == "```":
            content = content[4:-3]

        embeds = self.generate_confirmation_embeds(
            content=content,
            original_content=msg.content,
            channel=channel,
            author=ctx.author,
            action="Editing",
            message_type="message",
            message_link=msg.jump_url,
            content_name="Content",
        )

        success = await confirm(
            bot=self.bot,
            embed=embeds.confirmation_embed,
            finished_embed=embeds.finish_embed,
            content=embeds.content,
            original_content=embeds.original_content,
            channel_id=ctx.channel.id,
            author_id=ctx.author.id,
            initial_message_id=ctx.message.id,
            content_name="Content",
        )
        if success:
            await self.send_message_info_embed(
                ctx, "edit", ctx.author, content, msg, channel
            )
            await msg.edit(content=content)

    # Create the command delete. This will delete a message from the bot.
    @commands.command(name="delete", aliases=["delete-embed"])
    async def delete(
        self,
        ctx: Context,
        channel: Optional[discord.TextChannel] = None,
        message_id: Optional[int] = None,
    ) -> None:
        def is_correct(m: discord.Message) -> bool:
            return m.author == ctx.author

        channel = await self.check_channel(ctx, channel)

        if channel.guild != ctx.guild:
            raise errors.DifferentServer(
                "That channel is not in this server, Please re-do the command"
            )

        msg = await self.check_message_id(ctx, channel, message_id)
        if msg.author.id != ctx.me.id:
            raise errors.DifferentAuthor(
                "That message was not from me! I cannot delete messages that are not from me"
            )

        if msg.content:
            message_content = msg.content
            content_name = "Content"
        elif isinstance(msg.embeds[0].title, str):
            message_content = msg.embeds[0].title
            content_name = "Embed Title"
        else:
            content_name = "Embed Title"
            message_content = "No title"

        embeds = self.generate_confirmation_embeds(
            content=message_content,
            original_content=None,
            channel=channel,
            author=ctx.author,
            action="Deleting",
            message_type="message",
            message_link=msg.jump_url,
            content_name=content_name,
        )
        success = await confirm(
            bot=self.bot,
            embed=embeds.confirmation_embed,
            finished_embed=embeds.finish_embed,
            content=embeds.content,
            original_content=embeds.original_content,
            channel_id=ctx.channel.id,
            author_id=ctx.author.id,
            initial_message_id=ctx.message.id,
            content_name=content_name,
        )
        if success:

            if len(msg.embeds) > 0:
                log_embed = discord.Embed(
                    title="Deleted the message!",
                    colour=discord.Colour(0xC387C1),
                    description="The full embed(s) are in the attached file in JSON format.",
                    timestamp=datetime.now(timezone.utc),
                )
                log_embed.add_field(name="Deleter", value=ctx.author.mention)
                log_embed.add_field(name="Channel", value=channel.mention)
                file_name = f"{ctx.author.id}-{datetime.utcnow()}-content.json"
                with open(file_name, "w+") as f:
                    embeds_list = []
                    for embed in msg.embeds:
                        embeds_list.append(embed.to_dict())
                    message_content_dict = {"embeds": embeds_list, "content": ""}
                    if msg.content is not None:
                        message_content_dict["content"] = msg.content

                    json.dump(message_content_dict, f)
                await send_log_once(
                    guild_id=ctx.guild.id,
                    bot=self.bot,
                    logger_type="main",
                    embeds=[log_embed],
                    file=discord.File(file_name, filename="content.json"),
                )
                os.remove(file_name)

            else:
                await self.send_message_info_embed(
                    ctx, "delete", ctx.author, message_content, msg, channel
                )
            try:
                await msg.delete()
            except discord.errors.Forbidden:
                raise errors.ContentError("There was an unknown error!")

    @commands.command(name="fetch", aliases=["fetch-embed"])
    async def fetch(
        self,
        ctx: Context,
        channel: Optional[discord.TextChannel] = None,
        message_id: Optional[int] = None,
    ) -> None:
        channel = await self.check_channel(ctx, channel)
        if channel.guild != ctx.guild:
            raise errors.DifferentServer(
                "That channel is not in this server, Please re-do the command"
            )

        msg = await self.check_message_id(ctx, channel, message_id)
        file_name = f"{ctx.author.id}-{datetime.utcnow()}-content"
        if len(msg.embeds) == 0:
            file_name = file_name + ".txt"
            with open(file_name, "w+") as f:
                f.write(f"Content:\n\n{msg.content}")
        else:
            file_name = file_name + ".json"
            with open(file_name, "w+") as f:
                embeds_list = []
                for embed in msg.embeds:
                    embeds_list.append(embed.to_dict())
                message_content_dict = {"embeds": embeds_list, "content": ""}
                if msg.content is not None:
                    message_content_dict["content"] = msg.content

                json.dump(message_content_dict, f)
        if file_name[-4:] == "json":
            file_display_name = "content.json"
        else:
            file_display_name = "content.txt"
        await ctx.send(
            content="Fetched the message! Contents in the attached text file.",
            file=discord.File(file_name, filename=file_display_name),
        )
        os.remove(file_name)

    @commands.command(name="send-embed")
    async def send_embed(
        self, ctx: Context, channel: Optional[discord.TextChannel] = None
    ) -> None:
        if ctx.invoked_subcommand is None:
            channel = await self.check_channel(ctx, channel)  # Get the channel.
            if channel.guild != ctx.guild:
                raise errors.DifferentServer()
            title = await self.check_content(
                ctx, None, ask_message="Enter the title of the embed:"
            )
            if title[0:3] == "```" and title[-3:] == "```":
                title = title[3:-3]
            description = await self.check_content(
                ctx, None, ask_message="Enter the description (main body) of the embed:"
            )
            if description[0:3] == "```" and description[-3:] == "```":
                description = description[3:-3]
            embed = discord.Embed(title=title, description=description)
            embeds = self.generate_confirmation_embeds(
                content=title,
                original_content=None,
                channel=channel,
                author=ctx.author,
                action="Sending",
                message_type="embed",
                message_link=None,
                content_name="Embed Title",
            )
            success = await confirm(
                bot=self.bot,
                embed=embeds.confirmation_embed,
                finished_embed=embeds.finish_embed,
                content=embeds.content,
                original_content=embeds.original_content,
                channel_id=ctx.channel.id,
                author_id=ctx.author.id,
                initial_message_id=ctx.message.id,
                content_name="Embed Title",
            )
            if success:
                await channel.send(embed=embed)
                log_embed = discord.Embed(
                    title="Sent the embed!",
                    colour=discord.Colour(0xC387C1),
                    description="The full embed is in the attached file in JSON format.",
                    timestamp=datetime.now(timezone.utc),
                )
                log_embed.add_field(name="Title", value=title)
                file_name = f"{ctx.author.id}-{datetime.utcnow()}-content.json"
                with open(file_name, "w+") as f:
                    message_content_dict = embed.to_dict()

                    json.dump(message_content_dict, f)
                await send_log_once(
                    guild_id=ctx.guild.id,
                    bot=self.bot,
                    logger_type="main",
                    embeds=[log_embed],
                    file=discord.File(file_name, filename="content.json"),
                )
                os.remove(file_name)

    @commands.command(name="send-embed-json")
    async def send_json_embed(
        self,
        ctx: Context,
        channel: Optional[discord.TextChannel] = None,
        *,
        json_content: Optional[str] = None,
    ) -> None:
        log_embed = discord.Embed(
            title="Sent the embed!",
            colour=discord.Colour(0xC387C1),
            description="The full embed is in the attached text file in JSON format.",
            timestamp=datetime.now(timezone.utc),
        )
        log_embed.add_field(name="Author", value=ctx.author.mention)
        channel = await self.check_channel(ctx, channel)  # Get the channel.
        if channel.guild != ctx.guild:
            raise errors.DifferentServer()
        log_embed.add_field(name="Channel", value=channel.mention)
        json_content = await self.check_content(
            ctx, json_content, ask_message="What is the JSON content of the embed?"
        )
        if json_content[0:7] == "```json" and json_content[-3:]:
            json_content = json_content[7:-3]
        elif json_content[0:3] == "```" and json_content[-3:] == "```":
            json_content = json_content[3:-3]
        try:
            dict_content = json.loads(json_content)
        except json.decoder.JSONDecodeError as e:
            raise errors.JSONFailure(
                "The json that you specified was not correct, please check and try again.\n"
                f"Get support from the docs or the support server at {self.bot.command_with_prefix(ctx, 'support')}\n"
                f"Error message: {e}"
            )
        final_embeds: List[discord.Embed] = []
        embed_titles: List[str] = []
        content_to_send: Optional[str] = None
        if "embeds" in dict_content or "content" in dict_content:
            embeds = dict_content.get("embeds", [])
            content = dict_content.pop("content", None)
            if content is not None and content != "":
                content_to_send = content
            n = 1
            for embed in embeds:
                try:
                    if isinstance(embed["timestamp"], str):
                        embed.pop("timestamp")
                except KeyError:
                    pass
                if "title" in embed:
                    log_embed.add_field(name=f"Embed {n}", value=embed["title"])
                    embed_titles.append(embed["title"])
                final_embeds.append(discord.Embed.from_dict(embed))
                n = n + 1

        else:
            try:
                if isinstance(dict_content["timestamp"], str):
                    dict_content.pop("timestamp")
            except KeyError:
                pass
            final_embeds.append(discord.Embed.from_dict(dict_content))
            if "title" in dict_content:
                log_embed.add_field(name="Embed title", value=dict_content["title"])
                embed_titles.append(dict_content["title"])
        if content_to_send is None and len(final_embeds) == 0:
            raise errors.InputContentIncorrect(
                "You must provide either content or embeds!"
            )
        if len(final_embeds) > 1:
            message_type = "embeds"
        elif len(final_embeds) == 1:
            message_type = "embed"
        else:
            message_type = "message"

        if len(embed_titles) > 0:
            if len(final_embeds) > 1:
                content_name = "First Embed Title"
            else:
                content_name = "Embed Title"
        elif len(embed_titles) == 0 and content_to_send is not None:
            content_name = "Content"
        else:
            content_name = "Content too complicated to condense"
        content_for_confirm = (
            embed_titles[0] if len(embed_titles) > 0 else content_to_send
        )
        if content_for_confirm is None:
            content_for_confirm = "Content too complicated to condense"
        embeds = self.generate_confirmation_embeds(
            content=content_for_confirm,
            original_content=None,
            channel=channel,
            author=ctx.author,
            action="Sending",
            message_type=message_type,
            message_link=None,
            content_name=content_name,
        )
        success = await confirm(
            bot=self.bot,
            embed=embeds.confirmation_embed,
            finished_embed=embeds.finish_embed,
            content=embeds.content,
            original_content=embeds.original_content,
            channel_id=ctx.channel.id,
            author_id=ctx.author.id,
            initial_message_id=ctx.message.id,
            content_name="Embed Title",
        )
        if success:
            file_name = f"{ctx.author.id}-{datetime.utcnow()}-content.json"
            with open(file_name, "w+") as f:
                json.dump(dict_content, f)

            if content_to_send is not None:
                await channel.send(content_to_send)
            for embed in final_embeds:
                await channel.send(embed=embed)
            await send_log_once(
                guild_id=ctx.guild.id,
                bot=self.bot,
                logger_type="main",
                embeds=[log_embed],
                file=discord.File(file_name, filename="content.json"),
            )
            os.remove(file_name)

    @commands.command(name="edit-embed")
    async def edit_embed(
        self,
        ctx: Context,
        channel: Optional[discord.TextChannel] = None,
        message_id: Optional[int] = None,
    ) -> None:
        channel = await self.check_channel(ctx, channel)
        if channel.guild != ctx.guild:
            raise errors.DifferentServer()

        msg = await self.check_message_id(ctx, channel, message_id)
        if msg.author != ctx.guild.me:
            raise errors.DifferentAuthor()
        if len(msg.embeds) == 0:
            raise errors.InputContentIncorrect(
                f"That message does not have an embed! Try {self.bot.command_with_prefix(ctx, 'edit')} instead"
            )
        elif len(msg.embeds) > 1:
            raise errors.InputContentIncorrect(
                "That message has more than one embed! I don't support that right now 😔"
            )

        title = await self.check_content(
            ctx, None, ask_message="Enter the new title of the embed:"
        )
        if title[0:3] == "```" and title[-3:] == "```":
            title = title[3:-3]
        description = await self.check_content(
            ctx,
            None,
            ask_message="Enter the new description (main body) of the embed:",
        )
        if description[0:3] == "```" and description[-3:] == "```":
            description = description[3:-3]
        old_embed = msg.embeds[0].to_dict()
        new_embed = msg.embeds[0]
        new_embed.description = description
        new_embed.title = title
        embeds = self.generate_confirmation_embeds(
            content=title,
            original_content=old_embed.get("title", "No Title"),
            channel=channel,
            author=ctx.author,
            action="Editing",
            message_type="embed",
            message_link=msg.jump_url,
            content_name="Embed Title",
        )
        success = await confirm(
            bot=self.bot,
            embed=embeds.confirmation_embed,
            finished_embed=embeds.finish_embed,
            content=embeds.content,
            original_content=embeds.original_content,
            channel_id=ctx.channel.id,
            author_id=ctx.author.id,
            initial_message_id=ctx.message.id,
            content_name="Embed Title",
        )
        if success:
            log_embed = discord.Embed(
                title="Edited the embed!",
                colour=discord.Colour(0xC387C1),
                description="The original message and the new message are attached above.",
                timestamp=datetime.now(timezone.utc),
            )
            log_embed.add_field(name="Editor", value=ctx.author.mention)
            log_embed.add_field(name="Channel", value=channel.mention)
            old_file_name = f"{ctx.author.id}-{datetime.utcnow()}-old-content.json"
            with open(old_file_name, "w+") as f:
                json.dump(old_embed, f)

            new_file_name = f"{ctx.author.id}-{datetime.utcnow()}-new-content.json"
            with open(new_file_name, "w+") as f:
                json.dump(new_embed.to_dict(), f)
            await send_log_once(
                guild_id=ctx.guild.id,
                bot=self.bot,
                logger_type="main",
                embeds=[log_embed],
                files=[
                    discord.File(new_file_name, filename="new-content.json"),
                    discord.File(old_file_name, "old-content.json"),
                ],
            )
            os.remove(new_file_name)
            os.remove(old_file_name)
            await msg.edit(embed=new_embed)

    @commands.command(name="edit-embed-json")
    async def json_edit(
        self,
        ctx: Context,
        channel: Optional[discord.TextChannel] = None,
        message_id: Optional[int] = None,
        *,
        json_content: Optional[str] = None,
    ) -> None:
        channel = await self.check_channel(ctx, channel)
        if channel.guild != ctx.guild:
            raise errors.DifferentServer()

        msg = await self.check_message_id(ctx, channel, message_id)
        if msg.author != ctx.guild.me:
            raise errors.DifferentAuthor()
        if len(msg.embeds) == 0:
            raise errors.InputContentIncorrect(
                f"That message does not have an embed! Try {self.bot.command_with_prefix(ctx, 'edit')} instead"
            )
        elif len(msg.embeds) > 1:
            raise errors.InputContentIncorrect(
                "That message has more than one embed! I don't support that right now 😔"
            )
        old_embed = msg.embeds[0].to_dict()

        new_json_content = await self.check_content(
            ctx, json_content, ask_message="What is the new JSON content of the embed?"
        )
        if new_json_content[0:7] == "```json" and new_json_content[-3:] == "```":
            new_json_content = new_json_content[7:-3]
        elif new_json_content[0:3] == "```" and new_json_content[-3:] == "```":
            new_json_content = new_json_content[3:-3]

        try:
            new_dict_content = json.loads(new_json_content)
        except json.decoder.JSONDecodeError as e:
            raise errors.JSONFailure(
                "The json that you specified was not correct, please check and try again.\n"
                f"Get support from the docs or the support server at {self.bot.command_with_prefix(ctx, 'support')}\n"
                f"Error message: {e}"
            )

        log_embed = discord.Embed(
            title="Edited the embed!",
            colour=discord.Colour(0xC387C1),
            description="The original message and the new message are attached above.",
            timestamp=datetime.now(timezone.utc),
        )
        log_embed.add_field(name="Editor", value=ctx.author.mention)
        log_embed.add_field(name="channel", value=channel.mention)

        final_embed: discord.Embed
        if "embeds" in new_dict_content:
            embeds = new_dict_content["embeds"]

            content = new_dict_content.pop("content", None)

            if len(embeds) > 1:
                raise errors.InputContentIncorrect(
                    "You can't edit more than one embed at once!\nTry again with only one embed in the JSON data"
                )
            if content is not None and content != "":
                await ctx.send(
                    "WARNING!\nPlease update the content separately, the content value has been ignored"
                )
            embed = embeds[0]
            try:
                if isinstance(embed["timestamp"], str):
                    embed.pop("timestamp")
            except KeyError:
                pass
            final_embed = discord.Embed.from_dict(embed)

        else:
            try:
                if isinstance(new_dict_content["timestamp"], str):
                    new_dict_content.pop("timestamp")
            except KeyError:
                pass
            final_embed = discord.Embed.from_dict(new_dict_content)
        content_for_confirm = final_embed.title or "No Title"
        if not isinstance(content_for_confirm, str):
            content_for_confirm = "Content too complicated to condense"
        embeds = self.generate_confirmation_embeds(
            content=content_for_confirm,
            original_content=old_embed.get("title", "No Title"),
            channel=channel,
            author=ctx.author,
            action="Editing",
            message_type="embed",
            message_link=msg.jump_url,
            content_name="Embed Title",
        )
        success = await confirm(
            bot=self.bot,
            embed=embeds.confirmation_embed,
            finished_embed=embeds.finish_embed,
            content=embeds.content,
            original_content=embeds.original_content,
            channel_id=ctx.channel.id,
            author_id=ctx.author.id,
            initial_message_id=ctx.message.id,
            content_name="Embed Title",
        )
        if success:
            await msg.edit(embed=final_embed)
            old_file_name = f"{ctx.author.id}-{datetime.utcnow()}-old-content.json"
            with open(old_file_name, "w+") as f:
                json.dump(old_embed, f)

            new_file_name = f"{ctx.author.id}-{datetime.utcnow()}-new-content.json"
            with open(new_file_name, "w+") as f:
                json.dump(new_dict_content, f)
            await send_log_once(
                guild_id=ctx.guild.id,
                bot=self.bot,
                logger_type="main",
                embeds=[log_embed],
                files=[
                    discord.File(new_file_name, filename="new-content.json"),
                    discord.File(old_file_name, "old-content.json"),
                ],
            )
            os.remove(new_file_name)
            os.remove(old_file_name)


def setup(bot: Bot) -> None:
    bot.add_cog(MessagesCog(bot))
    logger.info("Messages cog!")
