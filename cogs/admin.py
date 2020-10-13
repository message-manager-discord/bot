import discord, asyncio, random, string, datetime
from discord.ext import commands
from math import floor


class AdminCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx: commands.Context):
        if await self.bot.is_owner(ctx.author):
            return True
        else:
            raise self.bot.errors.MissingPermission(
                "You need to be a bot dev to do that!"
            )

    async def cog_command_error(self, ctx: commands.Context, error):
        if isinstance(
            error,
            (
                self.bot.errors.MissingPermission,
                commands.errors.MissingRequiredArgument,
            ),
        ):
            await ctx.send(error)
        else:
            await ctx.send(
                "There was an unknown error! "
                "This has been reported to the devs."
                "\nIf by any chance this broke something, "
                "contact us through our support server"
            )
            raise error

    @commands.command(hidden=True)
    async def load(self, ctx: commands.Context, *, module: str):
        try:
            self.bot.load_extension(module)
        except Exception as error:
            await ctx.send(f"{type(error).__name__}: {error}")
        else:
            await ctx.send(f"The module {module} was loaded!")

    @commands.command(hidden=True)
    async def listservers(self, ctx: commands.Context):
        servers = []
        x = 0
        for guild in self.bot.guilds:
            try:
                servers[int(x / 50)] = (
                    servers[int(x / 50)] + f'\n"{guild.name}", {len(guild.members)}'
                )
            except IndexError:
                servers.append(f'\n"{guild.name}", {len(guild.members)}')
            x += 1
        await ctx.author.send(f"I am in {len(self.bot.guilds)} servers!")
        for item in servers:
            await ctx.author.trigger_typing()
            await asyncio.sleep(1)
            await ctx.author.send(item)

    @commands.command(hidden=True)
    async def unload(self, ctx: commands.Context, *, module: str):
        """Unloads a module."""
        try:
            self.bot.unload_extension(module)
        except Exception as error:
            await ctx.send(f"{type(error).__name__}: {error}")
        else:
            await ctx.send(f"The module {module} was unloaded!")

    @commands.command(name="reload", hidden=True)
    async def _reload(self, ctx: commands.Context, *, module: str):
        """Reloads a module."""
        try:
            self.bot.unload_extension(module)
            self.bot.load_extension(module)
        except Exception as error:
            await ctx.send(f"{type(error).__name__}: {error}")
        else:
            await ctx.send(f"The module {module} was reloaded!")

    @commands.command()
    async def kill(self, ctx: commands.Context):
        message = await ctx.send("Are you sure you want to kill me?")

        def is_correct(m):
            return m.author == ctx.author

        try:
            choice = await self.bot.wait_for("message", check=is_correct)
        except asyncio.TimeoutError:
            return await ctx.send("Timedout, Please re-do the command.")

        if choice.content.lower() == "yes":
            try:
                await choice.delete()
                await message.delete()
            except discord.errors.Forbidden:
                pass
            verify_message = "".join(
                random.SystemRandom().choice(string.ascii_letters + string.digits)
                for _ in range(6)
            )
            message = await ctx.send(
                "Are you still **absolutely** sure you want to log the bot out?\n"
                "**WARNING: This will disconnect the bot. It will have to be started from the console.\n"
                f"If you are absloutly sure then reply with the following code: `{verify_message}`"
            )
            try:
                choice = await self.bot.wait_for(
                    "message", check=is_correct, timeout=280.0
                )
            except asyncio.TimeoutError:
                return await ctx.send("Timedout, Please re-do the command.")

            if choice.content == verify_message:
                await ctx.send("Logging out")
                try:
                    await self.bot.logout()
                except Exception as error:
                    await ctx.send(f"{type(error).__name__}: {error}")

    @commands.command()
    async def loadtime(self, ctx):
        diff = self.bot.load_time - self.bot.start_time
        hours = floor(diff.seconds / 3600)
        minutes = floor((diff.seconds - (hours * 3600)) / 60)
        seconds = floor(diff.seconds - (hours * 3600 + minutes * 60))
        milliseconds = floor(diff.microseconds / 1000)
        microseconds = diff.microseconds - (milliseconds * 1000)
        await ctx.send(
            embed=discord.Embed(
                title="Time it took to load",
                description=f"{hours} Hours, {minutes} Minutes, {seconds} Seconds, {milliseconds} Milliseconds, {microseconds} Microseconds",
                colour=discord.Colour(16761035),
                timestamp=datetime.datetime.now(datetime.timezone.utc),
            )
        )


def setup(bot):
    bot.add_cog(AdminCog(bot))
    print("    Admin cog!")
