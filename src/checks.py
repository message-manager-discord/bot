import discord
from src import helpers
config_vars = helpers.fetch_config()
allowed_server = config_vars['allowed_server']
bypassed_users = config_vars['bypassed_users']
management_role = config_vars['management_role']

class MissingPermission(discord.ext.commands.CheckFailure):
    pass

def check_if_right_server(ctx):
    if allowed_server == 'None':
        return True
    elif ctx.message.guild.id == int(allowed_server):
        return True
    elif ctx.author.id in bypassed_users:
        return True
    else:
        return False

def check_if_manage_role(ctx):
    if management_role == "None":
        return True 
    elif ctx.author.id in bypassed_users:
        
        return True
    else:
        for role in ctx.author.roles:
            if int(management_role) == role.id:
                return True     
        raise MissingPermission("You need the management role to do that!\n"
    "Contact your server admin if you think you should be able to do this")

def is_bot_admin(ctx):
    if ctx.author.id in bypassed_users:
        return True
    else:
        raise MissingPermission("You need to be a bot dev to do that!")
