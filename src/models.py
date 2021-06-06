from typing import Optional, Union

from tortoise import Model, fields


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
