import discord
from src import helpers, errors, db
from config import bypassed_users


async def check_if_manage_role(ctx):
    management_role = await db.pool.get_management_role(ctx.guild.id)
    if management_role is None:
        prefix = await db.pool.get_prefix(ctx.guild.id)
        raise errors.ConfigNotSet(f"You have not set any stats channels!\nDo this with the `{prefix}config` command")
    elif ctx.author.id in bypassed_users:
        
        return True
    else:
        for role in ctx.author.roles:
            if int(management_role) == role.id:
                return True     
        raise errors.MissingPermission("You need the management role to do that!\n"
    "Contact your server admin if you think you should be able to do this")

def is_bot_admin(ctx):
    if ctx.author.id in bypassed_users:
        return True
    else:
        raise errors.MissingPermission("You need to be a bot dev to do that!")

def setup(bot):
    print('    Checks!')