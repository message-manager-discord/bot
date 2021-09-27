from typing import Awaitable

from discord.ext import commands

from src import Context, errors
from src.models import CommandStatus, CommandUsageAnalytics


def success_analytics(ctx: Context, cancelled=False) -> Awaitable:
    if cancelled:
        success = CommandStatus.USER_CANCELLED
    else:
        success = CommandStatus.SUCCESS
    return CommandUsageAnalytics.create(
        guild_id=ctx.guild.id if ctx.guild is not None else None,
        command_name=[*ctx.invoked_parents, ctx.invoked_with],
        slash=False,
        success=success,
    )


def get_success_code(error: Exception) -> CommandStatus:
    if isinstance(
        error, (errors.MissingPermission, commands.errors.MissingPermissions)
    ):
        return CommandStatus.MISSING_USER_PERMISSIONS

    elif isinstance(error, errors.DifferentServer):
        return CommandStatus.INPUT_DIFFERENT_SERVER
    elif isinstance(error, errors.ConfigNotSet):
        return CommandStatus.CONFIG_NOT_SET
    elif isinstance(error, errors.InputContentIncorrect):
        return CommandStatus.INVALID_INPUT
    elif isinstance(error, errors.DifferentAuthor):
        return CommandStatus.MESSAGE_AUTHOR_NOT_BOT
    elif isinstance(error, errors.JSONFailure):
        return CommandStatus.INPUT_JSON_INVALID
    elif isinstance(error, errors.InputContentTooLong):
        return CommandStatus.INPUT_TOO_LONG
    elif isinstance(error, commands.NoPrivateMessage):
        return CommandStatus.GUILD_ONLY_COMMAND_IN_DM
    elif isinstance(error, errors.WebhookChannelNotTextChannel):
        return CommandStatus.CHANNEL_INPUT_NOT_TEXT_CHANNEL
    elif isinstance(error, errors.MissingBotPermission):
        return CommandStatus.MISSING_BOT_PERMISSIONS
    else:
        return CommandStatus.UNKNOWN_ERROR
