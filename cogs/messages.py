import asyncio
import os
import platform

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
                commands.NoPrivateMessage,
            ),
        ):
            await ctx.send(error)
        elif isinstance(error, asyncio.TimeoutError):
            await ctx.send("Timedout, Please try again.")
        else:
            await ctx.send(
                "There was an unknown error! "
                "This has been reported to the devs."
                "\nIf by any chance this broke something, "
                "contact us through our support server"
            )
            raise error

    async def check_channel(self, ctx: commands.Context, channel):
        def is_correct(m):
            return m.author == ctx.author

        if channel == None:
            message = await ctx.send(
                embed=discord.Embed(
                    title="What is the channel?",
                    colour=discord.Colour.blue(),
                    timestamp=datetime.now(timezone.utc),
                )
            )
            get_channel = await self.bot.wait_for("message", check=is_correct)
            try:
                await get_channel.delete()
                await message.delete()
            except discord.errors.Forbidden:
                pass
            get_channel.content
            channel = await commands.TextChannelConverter().convert(
                ctx, get_channel.content
            )

            return channel
        else:
            return channel

    async def check_content(self, ctx: commands.Context, content):
        def is_correct(m):
            return m.author == ctx.author

        if content == None or content == "":
            message = await ctx.send(
                embed=discord.Embed(
                    title="What is the content of the message to be?",
                    colour=discord.Colour.blue(),
                    timestamp=datetime.now(timezone.utc),
                )
            )
            get_content = await self.bot.wait_for("message", check=is_correct)
            content = get_content.content
            try:
                await get_content.delete()
                await message.delete()
            except discord.errors.Forbidden:
                pass
            return content
        else:
            return content

    async def check_message_id(self, ctx: commands.Context, channel, message):
        ctx_but_with_channel = ctx
        if not isinstance(channel, discord.TextChannel):
            channel = await commands.TextChannelConverter().convert(ctx, channel)

        def is_correct(m):
            return m.author == ctx.author

        if message == None:
            message = await ctx.send(
                embed=discord.Embed(
                    title="What is the id of the message?",
                    colour=discord.Colour.blue(),
                    timestamp=datetime.now(timezone.utc),
                )
            )

            get_message = await self.bot.wait_for("message", check=is_correct)

            try:
                msg = await channel.fetch_message(get_message.content)
            except discord.NotFound:
                raise self.bot.errors.InputContentIncorrect(
                    "I can't find that message!"
                )

            try:
                await get_message.delete()
                await message.delete()
            except discord.errors.Forbidden:
                pass
            return msg
        else:
            try:
                message = await channel.fetch_message(message)
            except discord.NotFound:
                raise self.bot.errors.InputContentIncorrect(
                    "I can't find that message!"
                )
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
                    f.write(f"Cotent:\n\n{content}")
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
        try:
            await ctx.message.delete()
        except discord.errors.Forbidden:
            pass
        channel = await self.check_channel(ctx, channel)  # Get the channel.
        if channel.guild != ctx.guild:
            raise self.bot.errors.DifferentServer()
        perms = channel.permissions_for(ctx.guild.me)
        if not (perms.send_messages and perms.embed_links):
            raise self.bot.errors.InputContentIncorrect(
                "I do not the the `SEND MESSAGES` permission in that channel!"
            )

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
        try:
            await ctx.message.delete()
        except discord.errors.Forbidden:
            pass
        channel = await self.check_channel(ctx, channel)
        if channel.guild != ctx.guild:
            raise self.bot.errors.DifferentServer()

        msg = await self.check_message_id(ctx, channel, message_id)
        content = await self.check_content(ctx, content)
        if content[1:4] == "```" and content[-3:] == "```":
            content = content[4:-3]

        await self.send_message_info_embed(ctx, "edit", ctx.author, content, msg)
        await msg.edit(content=content)

    # Create the command delete. This will delete a message from the bot.
    @commands.command(name="delete")
    async def delete(
        self,
        ctx: commands.Context,
        channel: discord.TextChannel = None,
        message_id=None,
    ):
        def is_correct(m):
            return m.author == ctx.author

        try:
            await ctx.message.delete()
        except discord.errors.Forbidden:
            pass
        channel = await self.check_channel(ctx, channel)

        if channel.guild != ctx.guild:
            raise self.bot.errors.DifferentServer(
                "That channel is not in this server, Please re-do the command"
            )

        msg = await self.check_message_id(ctx, channel, message_id)
        embed = discord.Embed(
            title="Are you sure you want to delete this message?",
            colour=discord.Colour.red(),
            timestamp=datetime.now(timezone.utc),
        )
        embed.add_field(name="Channel", value=msg.channel.mention, inline=False)
        embed.add_field(
            name="Content", value=msg.content or msg.embeds[0].title, inline=False
        )
        message = await ctx.send(embed=embed)

        try:
            choice = await self.bot.wait_for("message", check=is_correct, timeout=100.0)
        except asyncio.TimeoutError:
            return await ctx.send("Timedout, Please re-do the command.")

        if choice.content.lower() == "yes":
            try:
                await msg.delete()
            except discord.errors.Forbidden:
                raise self.bot.errors.ContentError("There was an unknown error!")
            try:
                await choice.delete()
                await message.delete()
            except discord.errors.Forbidden:
                pass
            await self.send_message_info_embed(
                ctx, "delete", ctx.author, msg.content or msg.embeds[0].title, msg
            )
        else:
            embed = discord.Embed(
                title="Message deletion exited",
                colour=discord.Colour.red(),
                timestamp=datetime.now(timezone.utc),
            )
            embed.add_field(
                title="", value="{ctx.author.mention}chose not to delete the message"
            )
            await ctx.send(embed=embed)

    @commands.command(name="fetch")
    async def fetch(
        self,
        ctx: commands.Context,
        channel: discord.TextChannel = None,
        message_id=None,
    ):
        try:
            await ctx.message.delete()
        except discord.errors.Forbidden:
            pass
        channel = await self.check_channel(ctx, channel)
        if channel.guild != ctx.guild:
            raise self.bot.errors.DifferentServer(
                "That channel is not in this server, Please re-do the command"
            )

        msg = await self.check_message_id(ctx, channel, message_id)

        with open("content.txt", "w+") as f:
            f.write(f"Content:\n\n{msg.content}")
        embed = discord.Embed(
            title=f"Fetched the message!",
            colour=discord.Colour(0xC387C1),
            timestamp=datetime.now(timezone.utc),
        )
        with open("content.txt", "r") as fx:
            fx = open("content.txt", "r")
            await ctx.send(embed=embed, file=discord.File(fx, "Content.txt"))
        os.remove("content.txt")

    def check_content_length(self, content):
        if len(content) < 500:
            return content
        else:
            name = f"content-{datetime.now()}.txt"
            with open(name, "w+") as f:
                return discord.File(f, filename="content.txt")


def setup(bot):
    bot.add_cog(MessagesCog(bot))
    print("    Messages cog!")
