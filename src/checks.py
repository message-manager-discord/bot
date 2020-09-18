import discord
from src import helpers
from config import bypassed_users


async def check_if_manage_role(bot, ctx):
    management_role = await bot.db.get_management_role(ctx.guild.id)
    if management_role is None:
        prefix = await bot.db.get_prefix(ctx.guild.id)
        raise bot.errors.ConfigNotSet(f"You have not set the management role!\nDo this with the `{prefix}setup` command")
    elif ctx.author.id in bypassed_users:
        
        return True
    else:
        for role in ctx.author.roles:
            if int(management_role) == role.id:
                return True     
        raise bot.errors.MissingPermission("You need the management role to do that!\n"
    "Contact your server admin if you think you should be able to do this")

def is_bot_admin(bot, ctx):
    if ctx.author.id in bypassed_users:
        return True
    else:
        raise bot.errors.MissingPermission("You need to be a bot dev to do that!")

def setup(bot):
    print('    Checks!')