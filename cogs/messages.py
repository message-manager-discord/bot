# cogs/messages.py

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

import asyncio
import json
import os

from datetime import datetime, timezone

import discord

from discord.ext import commands


class MessagesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def cog_check(self, ctx: commands.Context):
        return self.bot.checks.check_if_manage_role(self.bot, ctx)

    async def cog_command_error(self, ctx: commands.Context, error):
        if isinstance(
            error,
            (
                self.bot.errors.MissingPermission,
                self.bot.errors.ContentError,
                self.bot.errors.DifferentServer,
                self.bot.errors.ConfigNotSet,
                self.bot.errors.InputContentIncorrect,
                self.bot.errors.DifferentAuthor,
                self.bot.errors.JSONFailure,
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
            await ctx.send("There was an unknown error!\n" f"Error: {error}")
            raise error

    async def check_channel(self, ctx: commands.Context, channel):
        def is_correct(m):
            return m.author == ctx.author

        if channel == None:
            await ctx.send("What is the channel?")
            get_channel = await self.bot.wait_for("message", check=is_correct)
            get_channel.content
            channel = await commands.TextChannelConverter().convert(
                ctx, get_channel.content
            )

        perms = channel.permissions_for(ctx.guild.me)
        sender_perms = channel.permissions_for(ctx.author)
        if not perms.view_channel:
            raise self.bot.errors.InputContentIncorrect(
                "I do not have the the `View Messages` permission in that channel!"
            )
        elif not (perms.send_messages and perms.embed_links):
            raise self.bot.errors.InputContentIncorrect(
                "I do not have the the `Send Message` and `Embed Links` permission in that channel!"
            )
        elif not sender_perms.view_channel:
            raise self.bot.errors.InputContentIncorrect(
                "You don't have the `View Messages` permissions in that channel!"
            )

        return channel

    async def check_content(
        self,
        ctx: commands.Context,
        content,
        ask_message="What is the content of the message to be?",
    ):
        def is_correct(m):
            return m.author == ctx.author

        if content == None or content == "":
            await ctx.send(ask_message)
            get_content = await self.bot.wait_for("message", check=is_correct)
            content = get_content.content
            return content
        else:
            return content

    async def check_message_id(self, ctx: commands.Context, channel, message):
        if not isinstance(channel, discord.TextChannel):
            channel = await commands.TextChannelConverter().convert(ctx, channel)

        def is_correct(m):
            return m.author == ctx.author

        async def message_or_error(channel, message):
            try:
                return await channel.fetch_message(int(message))
            except Exception as e:
                if isinstance(e, discord.NotFound):
                    raise self.bot.errors.InputContentIncorrect(
                        "I can't find that message!"
                    )
                elif isinstance(e, ValueError):
                    raise self.bot.errors.InputContentIncorrect(
                        "That is not a message id!"
                    )
                else:
                    raise e

        if message == None:
            await ctx.send("What is the id of the message?")

            get_message = await self.bot.wait_for("message", check=is_correct)

            message = await message_or_error(channel, get_message.content)
            return message
        else:
            message = await message_or_error(channel, message)
            return message

    async def send_message_info_embed(
        self, ctx: commands.Context, command_type, author, content, message
    ):
        title = "Sent"
        list_content = [
            ["Author", author.mention, True],
            ["Channel", message.channel.mention, True],
            ["Content", content, False],
        ]
        if command_type == "edit":
            title = "Edited"
            list_content.insert(2, ["Original Content", message.content, False])
            list_content[3][0] = "New Content"
            list_content[0][0] = "Editor"
        elif command_type == "delete":
            title = "Deleted"
            list_content[0][0] = "Deleter"
        elif command_type == "fetch":
            title = "Fetched"
            del list_content[1:2]
            del list_content[2:3]

        embed = discord.Embed(
            title=f"{title} the message!",
            colour=discord.Colour(0xC387C1),
            timestamp=datetime.now(timezone.utc),
        )
        for item in list_content:
            embed.add_field(name=item[0], value=item[1], inline=item[2])
        if len(content) >= 500 or len(message.content) >= 500:
            with open("content.txt", "w+") as f:
                if command_type == "edit":
                    f.write(
                        f"Original Content:\n\n{message.content}\n\nNew Content:\n\n{content}"
                    )
                    del list_content[2:4]
                elif command_type == "fetch":
                    f.write(f"Content:\n\n{content}")
                    del list_content[2:3]
                else:
                    f.write(f"Content:\n\n{content}")
                    del list_content[2:3]
            embed = discord.Embed(
                title=f"{title} the message!",
                colour=discord.Colour(0xC387C1),
                timestamp=datetime.now(timezone.utc),
            )
            for item in list_content:
                embed.add_field(name=item[0], value=item[1], inline=item[2])
            with open("content.txt", "r") as fx:
                await ctx.send(embed=embed, file=discord.File(fx, "Content.txt"))
            os.remove("content.txt")
        else:
            await ctx.send(embed=embed)

    @commands.command(name="send", rest_is_raw=True)
    async def send(
        self,
        ctx: commands.Context,
        channel: discord.TextChannel = None,
        *,
        content=None,
    ):
        channel = await self.check_channel(ctx, channel)  # Get the channel.
        if channel.guild != ctx.guild:
            raise self.bot.errors.DifferentServer()
        content = await self.check_content(ctx, content)
        if content[1:4] == "```" and content[-3:] == "```":
            content = content[4:-3]
        msg = await channel.send(content)
        embed = discord.Embed(
            title="Sent the message!",
            colour=discord.Colour(0xC387C1),
            timestamp=datetime.now(timezone.utc),
        )
        await self.send_message_info_embed(ctx, "Send", ctx.author, content, msg)

    # Create the edit command. This command will edit the specificed message. (Message must be from the bot)
    @commands.command(
        name="edit", rest_is_raw=True
    )  # rest_is_raw so that the white space will not be cut from the content.
    async def edit(
        self,
        ctx: commands.Context,
        channel: discord.TextChannel = None,
        message_id=None,
        *,
        content=None,
    ):
        channel = await self.check_channel(ctx, channel)
        if channel.guild != ctx.guild:
            raise self.bot.errors.DifferentServer()

        msg = await self.check_message_id(ctx, channel, message_id)
        if msg.author != ctx.guild.me:
            raise self.bot.errors.DifferentAuthor()

        content = await self.check_content(ctx, content)
        if content[1:4] == "```" and content[-3:] == "```":
            content = content[4:-3]

        await self.send_message_info_embed(ctx, "edit", ctx.author, content, msg)
        await msg.edit(content=content)

    # Create the command delete. This will delete a message from the bot.
    @commands.command(name="delete", aliases=["delete-embed"])
    async def delete(
        self,
        ctx: commands.Context,
        channel: discord.TextChannel = None,
        message_id=None,
    ):
        def is_correct(m):
            return m.author == ctx.author

        channel = await self.check_channel(ctx, channel)

        if channel.guild != ctx.guild:
            raise self.bot.errors.DifferentServer(
                "That channel is not in this server, Please re-do the command"
            )

        msg = await self.check_message_id(ctx, channel, message_id)
        if msg.author.id != ctx.me.id:
            raise self.bot.errors.DifferentAuthor(
                "That message was not from me! I cannot delete messages that are not from me"
            )
        embed = discord.Embed(
            title="Are you sure you want to delete this message?",
            colour=discord.Colour.red(),
            timestamp=datetime.now(timezone.utc),
        )
        embed.add_field(name="Channel", value=msg.channel.mention, inline=False)
        embed.add_field(
            name="Content", value=msg.content or msg.embeds[0].title, inline=False
        )
        await ctx.send(embed=embed)

        try:
            choice = await self.bot.wait_for("message", check=is_correct, timeout=100.0)
        except asyncio.TimeoutError:
            return await ctx.send("Timedout, Please re-do the command.")

        if choice.content.lower() == "yes":
            if len(msg.embeds) > 0:
                log_embed = discord.Embed(
                    title="Sent the embed!",
                    colour=discord.Colour(0xC387C1),
                    description="The full embed(s) are in the attached text file in JSON format.",
                    timestamp=datetime.now(timezone.utc),
                )
                log_embed.add_field(name="Deleter", value=ctx.author.mention)
                with open("content.txt", "w+") as f:
                    file_contents = (
                        f"Content:\n\n{msg.content if msg.content != '' else 'None'}"
                    )
                    n = 1
                    for embed in msg.embeds:
                        file_contents = (
                            file_contents
                            + f"\n\nEmbed in JSON:\n\n{json.dumps(embed.to_dict())}"
                        )
                        log_embed.add_field(
                            name=f"Embed {n}", value=embed.title or "None"
                        )
                        n = n + 1
                    f.write(file_contents)
                with open("content.txt", "r") as fx:
                    fx = open("content.txt", "r")
                    await ctx.send(
                        embed=log_embed, file=discord.File(fx, "Content.txt")
                    )
                os.remove("content.txt")

            else:
                await self.send_message_info_embed(
                    ctx, "delete", ctx.author, msg.content or msg.embeds[0].title, msg
                )
            try:
                await msg.delete()
            except discord.errors.Forbidden:
                raise self.bot.errors.ContentError("There was an unknown error!")

        else:
            embed = discord.Embed(
                title="Message deletion exited",
                colour=discord.Colour.red(),
                description=f"{ctx.author.mention}chose not to delete the message",
                timestamp=datetime.now(timezone.utc),
            )
            await ctx.send(embed=embed)

    @commands.command(name="fetch", aliases=["fetch-embed"])
    async def fetch(
        self,
        ctx: commands.Context,
        channel: discord.TextChannel = None,
        message_id=None,
    ):
        channel = await self.check_channel(ctx, channel)
        if channel.guild != ctx.guild:
            raise self.bot.errors.DifferentServer(
                "That channel is not in this server, Please re-do the command"
            )

        msg = await self.check_message_id(ctx, channel, message_id)

        with open("content.txt", "w+") as f:
            if len(msg.embeds) == 0:
                f.write(f"Content:\n\n{msg.content}")
            else:
                file_contents = (
                    f"Content:\n\n{msg.content if msg.content != '' else 'None'}"
                )
                for embed in msg.embeds:
                    file_contents = (
                        file_contents
                        + f"\n\nEmbed in JSON:\n\n{json.dumps(embed.to_dict())}"
                    )
                f.write(file_contents)
        with open("content.txt", "r") as fx:
            fx = open("content.txt", "r")
            await ctx.send(
                content="Fetched the message! Contents in the attached text file.",
                file=discord.File(fx, "Content.txt"),
            )
        os.remove("content.txt")

    @commands.group(name="send-embed")
    async def send_embed(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            channel = await self.check_channel(ctx, None)  # Get the channel.
            if channel.guild != ctx.guild:
                raise self.bot.errors.DifferentServer()
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
            await channel.send(embed=embed)
            log_embed = discord.Embed(
                title="Sent the embed!",
                colour=discord.Colour(0xC387C1),
                description="The full embed is in the attached text file in JSON format.",
                timestamp=datetime.now(timezone.utc),
            )
            log_embed.add_field(name="Title", value=title)
            file_name = f"{ctx.author.id}-{datetime.utcnow()}-content.txt"
            with open(file_name, "w+") as f:
                f.write(f"JSON content:\n\n{json.dumps(embed.to_dict())}")
            with open(file_name, "r") as fx:
                await ctx.send(embed=log_embed, file=discord.File(fx, "Content.txt"))
            os.remove(file_name)

    @send_embed.command(name="json")
    async def send_json_embed(
        self,
        ctx: commands.Context,
        channel: discord.TextChannel = None,
        *,
        json_content=None,
    ):
        log_embed = discord.Embed(
            title="Sent the embed!",
            colour=discord.Colour(0xC387C1),
            description="The full embed is in the attached text file in JSON format.",
            timestamp=datetime.now(timezone.utc),
        )
        log_embed.add_field(name="Author", value=ctx.author.mention)
        channel = await self.check_channel(ctx, channel)  # Get the channel.
        if channel.guild != ctx.guild:
            raise self.bot.errors.DifferentServer()
        log_embed.add_field(name="Channel", value=channel.mention)
        print(json_content)
        json_content = await self.check_content(
            ctx, json_content, ask_message="What is the JSON content of the embed?"
        )
        print(json_content)
        if json_content[0:3] == "```" and json_content[-3:] == "```":
            json_content = json_content[3:-3]
        print(json_content)
        try:
            dict_content = json.loads(json_content)
        except json.decoder.JSONDecodeError as e:
            raise self.bot.errors.JSONFailure(
                "The json that you specified was not correct, please check and try again.\n"
                f"Get support from the docs or the support server at `{ctx.prefix}support`\n"
                f"Error message: {e}"
            )

        if "embeds" in dict_content:
            embeds = dict_content["embeds"]
            content = dict_content.pop("content", None)
            if content is not None and content != "":
                await channel.send(content)
            n = 1
            for embed in embeds:
                try:
                    if isinstance(embed["timestamp"], str):
                        embed.pop("timestamp")
                except KeyError:
                    pass
                if "title" in embed:
                    log_embed.add_field(name=f"Embed {n}", value=embed["title"])
                await channel.send(embed=discord.Embed.from_dict(embed))
                n = n + 1
            file_name = f"{ctx.author.id}-{datetime.utcnow()}-content.txt"
            with open(file_name, "w+") as f:
                f.write(f"JSON content:\n\n{json.dumps(dict_content)}")
            with open(file_name, "r") as fx:
                await ctx.send(embed=log_embed, file=discord.File(fx, "Content.txt"))
            os.remove(file_name)

        else:
            try:
                if isinstance(dict_content["timestamp"], str):
                    dict_content.pop("timestamp")
            except KeyError:
                pass
            await channel.send(embed=discord.Embed.from_dict(dict_content))
            if "title" in dict_content:
                log_embed.add_field(name="Embed title", value=dict_content["title"])
            file_name = f"{ctx.author.id}-{datetime.utcnow()}-content.txt"
            with open(file_name, "w+") as f:
                f.write(f"JSON content:\n\n{json.dumps(dict_content)}")
            with open(file_name, "r") as fx:
                await ctx.send(embed=log_embed, file=discord.File(fx, "Content.txt"))
            os.remove(file_name)

    @commands.group(
        name="edit-embed", rest_is_raw=True
    )  # rest_is_raw so that the white space will not be cut from the content.
    async def edit_embed(
        self,
        ctx: commands.Context,
        channel: discord.TextChannel = None,
        message_id=None,
    ):
        if ctx.invoked_subcommand is None:
            channel = await self.check_channel(ctx, channel)
            if channel.guild != ctx.guild:
                raise self.bot.errors.DifferentServer()

            msg = await self.check_message_id(ctx, channel, message_id)
            if msg.author != ctx.guild.me:
                raise self.bot.errors.DifferentAuthor()
            if len(msg.embeds) == 0:
                raise self.bot.errors.InputContentIncorrect(
                    f"That message does not have an embed! Try `{ctx.prefix}edit` instead"
                )
            elif len(msg.embeds) > 1:
                raise self.bot.errors.InputContentINcorrect(
                    f"That message has more than one embed! I don't support that right now 😔"
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
            log_embed = discord.Embed(
                title="Edited the embed!",
                colour=discord.Colour(0xC387C1),
                description="The full embed is in the attached text file in JSON format.",
                timestamp=datetime.now(timezone.utc),
            )
            log_embed.add_field(name="Editor", value=ctx.author.mention)
            file_name = f"{ctx.author.id}-{datetime.utcnow()}-content.txt"
            with open(file_name, "w+") as f:
                f.write(
                    f"Old JSON content:\n\n{json.dumps(old_embed)}\n\nNew JSON content:\n\n{json.dumps(new_embed.to_dict())}"
                )
            with open(file_name, "r") as fx:
                await ctx.send(embed=log_embed, file=discord.File(fx, "Content.txt"))
            os.remove(file_name)
            await msg.edit(embed=new_embed)

    @edit_embed.command(
        name="json", rest_is_raw=True
    )  # rest_is_raw so that the white space will not be cut from the content.
    async def json_edit(
        self,
        ctx: commands.Context,
        channel: discord.TextChannel = None,
        message_id=None,
        *,
        json_content=None,
    ):

        channel = await self.check_channel(ctx, channel)
        if channel.guild != ctx.guild:
            raise self.bot.errors.DifferentServer()

        msg = await self.check_message_id(ctx, channel, message_id)
        if msg.author != ctx.guild.me:
            raise self.bot.errors.DifferentAuthor()
        if len(msg.embeds) == 0:
            raise self.bot.errors.InputContentIncorrect(
                f"That message does not have an embed! Try `{ctx.prefix}edit` instead"
            )
        elif len(msg.embeds) > 1:
            raise self.bot.errors.InputContentINcorrect(
                f"That message has more than one embed! I don't support that right now 😔"
            )

        new_json_content = await self.check_content(
            ctx, json_content, ask_message="What is the new JSON content of the embed?"
        )
        if new_json_content[0:3] == "```" and new_json_content[-3:] == "```":
            new_json_content = new_json_content[3:-3]
        try:
            new_dict_content = json.loads(new_json_content)
        except json.decoder.JSONDecodeError as e:
            raise self.bot.errors.JSONFailure(
                "The json that you specified was not correct, please check and try again.\n"
                f"Get support from the docs or the support server at `{ctx.prefix}support`\n"
                f"Error message: {e}"
            )

        log_embed = discord.Embed(
            title="Edited the embed!",
            colour=discord.Colour(0xC387C1),
            description="The full embed is in the attached text file in JSON format.",
            timestamp=datetime.now(timezone.utc),
        )
        log_embed.add_field(name="Editor", value=ctx.author.mention)

        if "embeds" in new_dict_content:
            embeds = new_dict_content["embeds"]

            content = new_dict_content.pop("content", None)

            if len(embeds) > 1:
                raise self.bot.errors.InputContentIncorrect(
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
            file_name = f"{ctx.author.id}-{datetime.utcnow()}-content.txt"
            with open(file_name, "w+") as f:
                f.write(
                    f"Old JSON content:\n\n{json.dumps(msg.embeds[0].to_dict())}\n\nNew JSON content:\n\n{json.dumps(embed)}"
                )
            with open(file_name, "r") as fx:
                await ctx.send(embed=log_embed, file=discord.File(fx, "Content.txt"))
            os.remove(file_name)
            await msg.edit(embed=discord.Embed.from_dict(embed))

        else:
            try:
                if isinstance(new_dict_content["timestamp"], str):
                    new_dict_content.pop("timestamp")
            except KeyError:
                pass
            file_name = f"{ctx.author.id}-{datetime.utcnow()}-content.txt"
            with open(file_name, "w+") as f:
                f.write(
                    f"Old JSON content:\n\n{json.dumps(msg.embeds[0].to_dict())}\n\nNew JSON content:\n\n{json.dumps(new_dict_content)}"
                )
            with open(file_name, "r") as fx:
                await ctx.send(embed=log_embed, file=discord.File(fx, "Content.txt"))
            os.remove(file_name)
            await msg.edit(embed=discord.Embed.from_dict(new_dict_content))


def setup(bot):
    bot.add_cog(MessagesCog(bot))
    print("    Messages cog!")
