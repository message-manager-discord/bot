import discord


async def check_if_manage_role(bot, ctx):
    if guild_only(bot, ctx):
        management_role = await bot.db.get_management_role(ctx.guild)
        if management_role is None:
            prefix = await bot.db.get_prefix(ctx.guild)
            raise bot.errors.ConfigNotSet(
                f"You have not set the management role!\nDo this with the `{prefix}setup` command"
            )
        elif await bot.is_owner(ctx.author):
            return True
        else:
            for role in ctx.author.roles:
                if int(management_role) == role.id:
                    return True
            raise bot.errors.MissingPermission(
                "You need the management role to do that!\n"
                "Contact your server admin if you think you should be able to do this"
            )


def guild_only(bot, ctx):
    if ctx.guild is None:
        raise discord.ext.commands.NoPrivateMessage(
            "That command can only be used in guilds!"
        )
    else:
        return True


def setup(bot):
    print("    Checks!")
