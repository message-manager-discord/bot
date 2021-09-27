from enum import IntEnum
from typing import Optional, Union

from tortoise import Model, fields
from tortoise.fields.data import (
    BigIntField,
    BooleanField,
    DatetimeField,
    IntEnumField,
    JSONField,
)


class Guild(Model):
    id = fields.BigIntField(pk=True)
    management_role_id: Optional[Union[fields.BigIntField, int]] = fields.BigIntField(
        null=True
    )
    prefix: Union[fields.CharField, str] = fields.CharField(max_length=3, default="~")

    logging_channels: fields.ForeignKeyRelation["LoggingChannel"]

    class Meta:
        table = "guilds"

    def __str__(self) -> str:
        return str(self.id)


class Channel(Model):
    id = fields.BigIntField(pk=True)
    webhook_id = fields.BigIntField(null=True)
    webhook_token = fields.CharField(max_length=255, null=True)

    logging_channels: fields.ForeignKeyRelation["LoggingChannel"]

    class Meta:
        table = "channels"

    def __str__(self) -> str:
        return str(self.id)


class LoggingChannel(Model):
    guild: fields.ForeignKeyRelation[Guild] = fields.ForeignKeyField(
        "bot.Guild", related_name="logging_channel"
    )
    channel: fields.ForeignKeyRelation[Channel] = fields.ForeignKeyField(
        "bot.Channel", related_name="logging_channel"
    )
    logger_type = fields.CharField(max_length=20, null=False)

    channel_id: int

    class Meta:
        table = "logging_channels"
        unique_together = ("guild_id", "channel_id")

    def __str__(self) -> str:
        return f"{self.channel_id}-{self.logger_type}"


class CommandStatus(IntEnum):
    SUCCESS = 0
    MISSING_BOT_PERMISSIONS = 1
    MISSING_USER_PERMISSIONS = 2
    INVALID_INPUT = 3
    MISSING_BOT_SCOPE = 4
    GUILD_ONLY_COMMAND_IN_DM = 5
    CHANNEL_INPUT_NOT_TEXT_CHANNEL = 6
    UNKNOWN_ERROR = 7
    INPUT_CHANNEL_NOT_FOUND = 8
    TIMEOUT = 9
    INPUT_DIFFERENT_SERVER = 10
    CONFIG_NOT_SET = 11
    MESSAGE_AUTHOR_NOT_BOT = 12
    INPUT_JSON_INVALID = 13
    INPUT_TOO_LONG = 14
    USER_CANCELLED = 15


class CommandUsageAnalytics(Model):
    guild_id = BigIntField(null=True)
    timestamp = DatetimeField(auto_now_add=True)
    command_name = JSONField(max_length=40)
    #  A list of the command name and subcommand names
    slash = BooleanField()
    success = IntEnumField(CommandStatus, default=0)

    class Meta:
        table = "command_usage_analytics"

    def __str__(self) -> str:
        return str(f"{self.guild_id}-{self.timestamp}-{self.command_name}")
