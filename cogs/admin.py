import discord, platform, datetime, asyncio, random, string
from discord.ext import commands
from src import helpers, checks, errors
from main import logger


class AdminCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def cog_check(self, ctx):
        return checks.is_bot_admin(ctx)

    async def cog_command_error(self, ctx, error):
        if isinstance(error, errors.MissingPermission):
            await ctx.send(error)
        else:
            logger.errr(error)


    @commands.command(hidden=True)
    async def load(self, ctx, *, module : str):
        try:
            self.bot.load_extension(module)
        except Exception as error:
            await ctx.send(f'{type(error).__name__}: {error}')
        else:
            await ctx.send(f'The module {module} was loaded!')

    @commands.command(hidden=True)
    async def unload(self, ctx, *, module : str):
        """Unloads a module."""
        try:
            self.bot.unload_extension(module)
        except Exception as error:
            await ctx.send(f'{type(error).__name__}: {error}')
        else:
            await ctx.send(f'The module {module} was unloaded!')

    @commands.command(name='reload', hidden=True)
    async def _reload(self, ctx, *, module : str):
        """Reloads a module."""
        try:
            self.bot.unload_extension(module)
            self.bot.load_extension(module)
        except Exception as error:
            await ctx.send(f'{type(error).__name__}: {error}')
        else:
            await ctx.send(f'The module {module} was reloaded!')

    @commands.command()
    async def kill(self, ctx):  
        message = await ctx.send("Are you sure you want to kill me?")
        def is_correct(m):
            return m.author == ctx.author
        try:
            choice = await self.bot.wait_for('message', check=is_correct)
        except asyncio.TimeoutError:
            return await ctx.send('Timedout, Please re-do the command.')

        if choice.content.lower() == 'yes':
            try:
                await choice.delete()
                await message.delete()
            except discord.errors.Forbidden:
                pass
            verify_message = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(6))
            message = await ctx.send("Are you still **absolutely** sure you want to log the bot out?\n"
            "**WARNING: This will disconnect the bot. It will have to be started from the console.\n"
            f"If you are absloutly sure then reply with the following code: `{verify_message}`"
            )
            try:
                choice = await self.bot.wait_for('message', check=is_correct, timeout=280.0)
            except asyncio.TimeoutError:
                return await ctx.send('Timedout, Please re-do the command.')

            if choice.content == verify_message:
                await ctx.send("Logging out")
                try:
                    await self.bot.logout()
                except Exception as error:
                    await ctx.send(f'{type(error).__name__}: {error}')

def setup(bot):
    bot.add_cog(AdminCog(bot))
    print('    Admin cog!')