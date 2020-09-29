import platform
from datetime import datetime, timezone
import discord
from discord.ext import commands

from config import owner

class MainCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def on_command_error(self, ctx : commands.Context, error):
        cog = ctx.cog
        if cog:
            if cog._get_overridden_method(cog.cog_command_error) is not None:
                return
        await ctx.send(
                "There was an unknown error! "
                "This has been reported to the devs."
                "\nIf by any chance this broke something, "
                "contact us through our support server"
            )
        raise error

    @commands.Cog.listener()
    async def on_ready(self):
        # Print the bot invite link
        print(f"https://discord.com/api/oauth2/authorize?client_id={self.bot.user.id}&permissions=519232&scope=bot")
        print(f"Logged on as {self.bot.user}!")
        # Change the presence of the bot


    @commands.Cog.listener()
    async def on_guild_join(self, guild : discord.Guild):
        
            
        if guild.system_channel is None:
            for c in guild.text_channels:
                perm = c.permissions_for(guild.me)
                if perm.send_messages and perm.embed_links:
                    channel = c
                    break
        else:
            system_channel = guild.system_channel
            perms = system_channel.permissions_for(guild.me)
            if perms.send_messages and perms.embed_links:
                channel = system_channel
            else:
                for c in guild.text_channels:
                    perm = c.permissions_for(guild.me)
                    if perm.send_messages and perm.embed_links:
                        channel = c
                        break
        if channel is not None:
            prefix = await self.bot.db.get_prefix(guild)
            embed = discord.Embed(
                title = "Hi there!",
                colour = discord.Colour(16761035),
                description = "Thank you for inviting me to your server!",
                timestamp = datetime.now(timezone.utc)
            )
            embed.add_field(
                name = 'Prefix',
                value = f'My prefix here is: `{prefix}`',
                inline = False
            )
            embed.add_field(
                name='Help',
                value="Have a look at my [docs](https://anothercat1259.gitbook.io/message-bot/startup/setup) "
                "If you've got any questions or join our [support server](https://discord.gg/xFZu29t)",
                inline = False
            )
            await channel.send(embed=embed)
        if not self.bot.self_hosted:
            embed = discord.Embed(
                title = "Joined a new server!",
                colour = discord.Colour(16761035),
                timestamp = datetime.now(timezone.utc)
            )
            embed.add_field(name='Name',value=guild.name,inline=False)
            embed.add_field(name="ID",value=guild.id,inline=False)
            await self.bot.get_channel(self.bot.join_log_channel).send(embed=embed)


    @commands.command(name='help', help='Responds with an embed with all the commands and options')
    async def help(self, ctx : commands.Context):
        prefix = await self.bot.db.get_prefix(ctx.guild)
        embed = discord.Embed(
            title = "Help!",
            colour = 16761035,
            timestamp = datetime.now(timezone.utc)
        )
        embed.add_field(
            name=f"`{prefix}ping`", 
            value="Replys with the latency of the bot", 
            inline=True
        )
        embed.add_field(
            name=f"`{prefix}help`", 
            value="Displays this view.", 
            inline=True
        ),
        embed.add_field(
            name=f'`{prefix}info`', 
            value='Displays info about the bot', 
            inline=True
        ),
        embed.add_field(
            name = f"`{prefix}send [channel_id] [content]`",
            value="Sends a message from the bot in the specificed channel",
            inline=True
        )
        embed.add_field(
            name=f'`{prefix}edit [channel_id] [message_id] [new_content]`',
            value='Edits a message, message **must** be from the bot',
            inline=True
        )
        embed.add_field(
            name=f"`{prefix}delete [channel_id] [message_id]`",
            value="Deletes the message from the bot. **Must** be from the bot",
            inline=True
        )
        embed.add_field(
            name=f"`{prefix}stats update`",
            value="Update the stats channels",
            inline=True
        )    
        await ctx.send(embed=embed)

    # Create the info command.
    @commands.command(name = 'info')
    async def info(self, ctx : commands.Context):
        prefix = await self.bot.db.get_prefix(ctx.guild)
        total_seconds = (datetime.utcnow() - self.bot.start_time).total_seconds()
        days = total_seconds // 86400
        hours = (total_seconds - (days * 86400)) // 3600
        minutes = (total_seconds - (days * 86400) - (hours * 3600)) // 60
        seconds = total_seconds - (days * 86400) - (hours * 3600) - (minutes * 60)
        embed = discord.Embed(
            title="Info about the bot",
            colour=discord.Colour(0xc387c1),
            timestamp =datetime.now(timezone.utc)
        )
        embed.add_field(
            name="Username", 
            value=self.bot.user, 
            inline=True
        ),
        embed.add_field(
            name="Prefix", 
            value=f'`{prefix}`', 
            inline=True
        ),
        embed.add_field(
            name="Version", 
            value="v0.3.0",
            inline=True
        ),
        embed.add_field(
            name="Docs", 
            value="[The Docs](https://anothercat1259.gitbook.io/message-bot/)", 
            inline=True
        ),
        embed.add_field(
            name="Developer",
            value='[Another Cat](https://github.com/AnotherCat)', 
            inline=True
        ), # The developer (me), Must not be changed, as per the LICENSE
        embed.add_field(
            name="Discord.py Version", 
            value=discord.__version__, 
            inline=True
        ),
        embed.add_field(
            name="Python Version", 
            value=platform.python_version(), 
            inline=True
        ),
        embed.add_field(
            name="System", 
            value=platform.system(), 
            inline=True
        ),
        embed.add_field(
            name="Uptime", 
            value=f"{int(days)} days {int(hours)} hours {int(minutes)} minutes {int(seconds)} seconds", 
            inline=True
        ),
        embed.add_field(
            name="Number of Servers",
            value=len(self.bot.guilds), 
            inline=True
        )   
        embed.set_thumbnail(url=f"{self.bot.user.avatar_url}")
        await ctx.send(embed=embed)

    @commands.command (name = "ping")
    async def ping(self, ctx : commands.Context):
        message = await ctx.send('Pong!')
        ping_time = (message.created_at-ctx.message.created_at).total_seconds() * 1000
        await message.edit(content=f'Ping! Took: {int(ping_time)}ms')


    
def setup(bot):
    bot.add_cog(MainCog(bot))
    print('    Main cog!')