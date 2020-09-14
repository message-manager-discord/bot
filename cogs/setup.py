import discord, platform, asyncio, random, string
from datetime import datetime, timezone
from discord.ext import commands
from src import helpers, checks, errors, db
from main import logger


class SetupCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_command_error(self, ctx, error):
        if isinstance(
            error,
            (
                errors.MissingPermission,
                errors.InputContentIncorrect,
                errors.ConfigNotSet,
                errors.ConfigError
            )
        ):
            """embed = discord.Embed(
                title = "An error has occured!",
                colour = discord.Colour.red(),
                timestamp = datetime.now(timezone.utc),
                description = error.message
            )
            await ctx.send(embed=embed)"""
            await ctx.send(error)
            
        else:
            raise error
    
    @commands.has_guild_permissions(administrator=True)
    @commands.group()
    async def setup(self, ctx):
        if ctx.invoked_subcommand is None:
            prefix = await db.pool.get_prefix(ctx.guild.id)
            embed = discord.Embed(
                title = "Setup!",
                description = "Setup values for your server!",
                timestamp = datetime.now(timezone.utc),
                colour = discord.Colour(15653155)
            )
            embed.add_field(
                name=f"`{prefix}setup admin <role>`",
                value="This is the role that allows admin access to admin commands.",
                inline = False
            )
            embed.add_field(
                name=f"`{prefix}setup prefix <prefix>`",
                value="Sets the prefix for this server.",
                inline = False
            )
            embed.add_field(
                name=f"`{prefix}setup botstats <channel>`",
                value="Sets the voice channel for the bot count",
                inline = False
            )
            embed.add_field(
                name=f"`{prefix}setup userstats <channel>`",
                value="Sets the voice channel for the user count",
                inline = False
            )
            await ctx.send(embed=embed)

    @commands.has_guild_permissions(administrator=True)
    @setup.command(name='prefix')
    async def return_prefix(self, ctx, new_prefix = None):
        prefix = await db.pool.get_prefix(ctx.guild.id)
        if new_prefix == None:
            await ctx.send(f"My prefix for this server is: `{prefix}`")
        else:
            if len(new_prefix) >1:
                raise errors.InputContentIncorrect(
                "Prefix's can only be 1 character long!"
            )
            else:
                await db.pool.update_prefix(ctx.guild.id, new_prefix)
                await ctx.send(
                    embed = discord.Embed(
                        title = 'Config updated!',
                        description = f"Server prefex updated from `{prefix}` to `{new_prefix}`",
                        timestamp = datetime.now(timezone.utc),
                        colour = discord.Colour(15653155)
                    )
                )
    
    @commands.has_guild_permissions(administrator=True)
    @setup.command()
    async def admin(self, ctx, role_id = None):
        original_role_id = await db.pool.get_management_role(ctx.guild.id)
        if original_role_id is None and role_id is None:
            raise errors.ConfigNotSet('The admin role has not been set yet!')
        original_role = ctx.guild.get_role(original_role_id)
        if role_id is None:
                       
            if original_role is None:
                raise errors.ConfigNotSet('The role could not be found!')
            else:
                await ctx.send(
                    embed=discord.Embed(
                        title = "Current management role",
                        description=original_role.mention,
                        colour = discord.Colour(15653155),
                        timestamp = datetime.now(timezone.utc)
                    )
                )

        else:
            if role_id.lower() == 'none':
                await db.pool.update_admin_role(ctx.guild.id, None)
                
                embed = discord.Embed(
                    title = 'Config updated!',
                    timestamp = datetime.now(timezone.utc),
                    colour = discord.Colour(15653155),
                    allowed_mentions = discord.AllowedMentions(roles=False)
                )
                if original_role is None:
                    embed.description = f"Mangement role updated to None"
                else:
                    embed.description = f"Mangement role updated from {original_role.mention} to None"
                await ctx.send(embed = embed)
            else:
                if role_id[:3] == '<@&':
                    role_id = role_id[3:-1]
                try:
                    role_id = int(role_id)
                    role = ctx.guild.get_role(role_id)
                    if role is None:
                        raise errors.InputContentIncorrect(
                        "I could not find that role! Please try again"
                    )
                except ValueError:
                    raise errors.InputContentIncorrect(
                    "I could not find that role! Please try again"
                )
                await db.pool.update_admin_role(ctx.guild.id, role_id)
                
                embed = discord.Embed(
                    title = 'Config updated!',
                    timestamp = datetime.now(timezone.utc),
                    colour = discord.Colour(15653155),
                    allowed_mentions = discord.AllowedMentions(roles=False)
                )
                if original_role is None:
                    embed.description = f"Mangement role updated to {role.mention}"
                else:
                    embed.description = f"Mangement role updated from {original_role.mention} to {role.mention}"
                await ctx.send(embed = embed)

    @commands.has_guild_permissions(administrator=True)
    @setup.command()
    async def botstats(self, ctx, channel_id = None):
        original_channel_id = await db.pool.get_bot_channel(ctx.guild.id)
        if original_channel_id is not None:
            original_channel = ctx.guild.get_channel(original_channel_id)
            if original_channel is None:
                raise errors.ConfigError("Looks like the stored channel is incorrect, please reset bot channel in the config.")
        if channel_id is None:
            if original_channel_id is None:
                raise errors.ConfigNotSet('The bot stats channel has not been set yet!')
            else:
                await ctx.send(
                    embed = discord.Embed(
                        title = 'Bot stats channel',
                        description = f'The current bot stats channel is {original_channel.name}',
                        timestamp = datetime.now(timezone.utc),
                        colour = discord.Colour(15653155)
                    )
                )

        else:
            if channel_id.lower() == 'none':
                channel_id = None
                await db.pool.update_bot_channel(ctx.guild.id, channel_id)
                
                embed = discord.Embed(
                    title = 'Config updated!',
                    timestamp = datetime.now(timezone.utc),
                    colour = discord.Colour(15653155)
                )
                if original_channel_id is None:
                    embed.description = description = f"Bot stats channel set to none!"
                else:
                    embed.description = f"Bot stats channel updated from {original_channel.name} to none!"
                await ctx.send(embed=embed)

            else:
                if channel_id[:2] == '<#':
                    channel_id = channel_id[2:-1]
                try:
                    channel_id = int(channel_id)
                    if channel_id == await db.pool.get_member_channel(ctx.guild.id):
                        raise errors.InputContentIncorrect('Bot stats channel can\'t be the same as user stats channel!')
                    channel = ctx.guild.get_channel(channel_id)
                    if channel is None or not isinstance(channel, discord.VoiceChannel):
                        raise errors.InputContentIncorrect(
                        "I could not find that channel! \nPlease try again and make sure it's a voice channel."
                    )
                except ValueError:
                    raise errors.InputContentIncorrect(
                    "I could not find that channel! Please try again"
                )
                await db.pool.update_bot_channel(ctx.guild.id, channel_id)
                
                embed = discord.Embed(
                    title = 'Config updated!',
                    timestamp = datetime.now(timezone.utc),
                    colour = discord.Colour(15653155)
                )
                if original_channel_id is None:
                    embed.description = description = f"Bot stats channel set to {channel.name}!"
                else:
                    embed.description = f"Bot stats channel updated from {original_channel.name} to {channel.name}!"
                await ctx.send(embed=embed)

    @commands.has_guild_permissions(administrator=True)
    @setup.command()
    async def userstats(self, ctx, channel_id):
        original_channel_id = await db.pool.get_user_channel(ctx.guild.id)
        if original_channel_id is not None:
            original_channel = ctx.guild.get_channel(original_channel_id)
            if original_channel is None:
                raise errors.ConfigError("Looks like the stored channel is incorrect, please reset bot channel in the config.")
        if channel_id is None:
            if original_channel_id is None:
                raise errors.ConfigNotSet('The user stats channel has not been set yet!')
            else:
                await ctx.send(
                    embed = discord.Embed(
                        title = 'User stats channel',
                        description = f'The current user stats channel is {original_channel.name}',
                        timestamp = datetime.now(timezone.utc),
                        colour = discord.Colour(15653155)
                    )
                )

        else:
            if channel_id.lower == 'none':
                channel_id = None
                await db.pool.update_user_channel(ctx.guild.id, channel_id)
                
                embed = discord.Embed(
                    title = 'Config updated!',
                    timestamp = datetime.now(timezone.utc),
                    colour = discord.Colour(15653155)
                )
                if original_channel_id is None:
                    embed.description = description = f"User stats channel set to none!"
                else:
                    embed.description = f"User stats channel updated from {original_channel.name} to none!"
                await ctx.send(embed=embed)

            else:
                if channel_id[:2] == '<#':
                    channel_id = channel_id[2:-1]
                try:
                    channel_id = int(channel_id)
                    if channel_id == await db.pool.get_bot_channel(ctx.guild.id):
                        raise errors.InputContentIncorrect(
                        "User stats channel can't be the same as bot stats channel!"
                    )
                    channel = ctx.guild.get_channel(channel_id)
                    if channel is None or not isinstance(channel, discord.VoiceChannel):
                        raise errors.InputContentIncorrect(
                        "I could not find that channel! \nPlease try again and make sure it's a voice channel."
                    )
                except ValueError:
                    raise errors.InputContentIncorrect(
                    "I could not find that channel! Please try again"
                )
                await db.pool.update_bot_channel(ctx.guild.id, channel_id)
                
                embed = discord.Embed(
                    title = 'Config updated!',
                    timestamp = datetime.now(timezone.utc),
                    colour = discord.Colour(15653155)
                )
                if original_channel_id is None:
                    embed.description = description = f"User stats channel set to {channel.name}!"
                else:
                    embed.description = f"User stats channel updated from {original_channel.name} to {channel.name}!"
                await ctx.send(embed=embed)



    @commands.command(name='prefix')
    async def prefix(self, ctx):
        prefix = await db.pool.get_prefix(ctx.guild.id)
        await ctx.send(f"My prefix for this server is: `{prefix}`")
        


def setup(bot):
    bot.add_cog(SetupCog(bot))
    print('    Setup cog!')