import discord, platform, datetime, asyncio
from discord.ext import commands
from src import helpers, checks
# from main import prefix

prefix = helpers.fetch_config('prefix')
owner = helpers.fetch_config('owner')

class MessagesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    def cog_check(self, ctx):
        return checks.check_if_manage_role(ctx)

    @commands.command(name="send", rest_is_raw = True)
    async def send(self, ctx, channel_id=None, *, content=None):
        try:
            await ctx.message.delete()
        except discord.errors.Forbidden:
            pass
        channel_id = await helpers.check_channel_id(ctx, channel_id, self.bot)
        if channel_id == False:
            return None
        content = await helpers.check_content(ctx, content, self.bot)
        if content == False:
            return None
        if content[1:4] == '```'and content[-3:] == '```':
            content = content[4:-3]
        channel = self.bot.get_channel(int(channel_id)) # Get the channel.
        msg = await channel.send(content)
        await helpers.send_message_info_embed(ctx, 'Send', ctx.author, content, msg)

    # Create the edit command. This command will edit the specificed message. (Message must be from the bot)
    @commands.command(name="edit", rest_is_raw=True)  # rest_is_raw so that the white space will not be cut from the content.
    async def edit(self, ctx, channel_id=None, message_id=None, *, content=None):
        await ctx.message.delete()
        channel_id = await helpers.check_channel_id(ctx, channel_id, self.bot)
        if channel_id == False:
            return None
        message_id = await helpers.check_message_id(ctx, message_id, self.bot)
        if message_id == False:
            return None
        content = await helpers.check_content(ctx, content, self.bot)
        if content == False:
            return None
        if content[1:4] == '```'and content[-3:] == '```':
            content = content[4:-3]
        msg = await helpers.get_message(self.bot, channel_id, message_id)   
        await helpers.send_message_info_embed(ctx, 'edit', ctx.author, content, msg)
        await msg.edit(content=content)

    # Create the command delete. This will delete a message from the bot. 
    @commands.command(name = 'delete')
    async def delete(self, ctx, channel_id=None, message_id=None):
        def is_correct(m):
            return m.author == ctx.author
        try:
            await ctx.message.delete()
        except discord.errors.Forbidden:
            pass
        channel_id = await helpers.check_channel_id(ctx, channel_id, self.bot)
        if channel_id == False:
            return None
        message_id = await helpers.check_message_id(ctx, message_id, self.bot)
        if message_id == False:
            return None

        msg = await helpers.get_message(self.bot, channel_id, message_id)        
        
        message = await ctx.send(
            embed = helpers.create_embed(
                "Are you sure you want to delete this message?",
                discord.Color.red(),
                [
                    ["Channel", msg.channel.mention, False],
                    ["Content", msg.content, False]
                ]
            )
        )
        
        
        try:
            choice = await self.bot.wait_for('message', check=is_correct, timeout=20.0)
        except asyncio.TimeoutError:
            return await ctx.send('Timedout, Please re-do the command.')

        if choice.content.lower() == 'yes':
            try:
                await choice.delete()
                await msg.delete()
                await message.delete()
            except discord.errors.Forbidden:
                pass
            await helpers.send_message_info_embed(ctx, 'delete', ctx.author, msg.content, msg)
        else:
            ctx.send(embed = helpers.create_embed(
                "Message deletion exited.",
                'red',
                [
                    ['', f'{ctx.author.mention}chose not to delete the message', False]
                ]
            )
            )

    @commands.command(name="fetch")
    async def fetch(self, ctx, channel_id=None, message_id=None):
        try:
            await ctx.message.delete()
        except discord.errors.Forbidden:
            pass
        channel_id = await helpers.check_channel_id(ctx, channel_id, self.bot)
        if channel_id == False:
            return None
        message_id = await helpers.check_message_id(ctx, message_id, self.bot)
        if message_id == False:
            return None
        msg = await helpers.get_message(self.bot, channel_id, message_id)
        await helpers.send_message_info_embed(ctx, 'fetch', ctx.author, msg.content, msg)

def setup(bot):
    bot.add_cog(MessagesCog(bot))
