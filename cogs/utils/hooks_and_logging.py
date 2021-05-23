from typing import List, Optional, Union

import discord

from discord import AsyncWebhookAdapter

from cogs.utils import errors
from main import Bot
from models import Channel, LoggingChannel


async def create_webhook(
    channel_id: int, bot: Bot, attempt: int = 0
) -> Union[errors.MissingManageWebhooks, discord.Webhook]:
    if attempt >= 3:
        raise errors.WebhookFailed("Got stuck in a loop!")
    channel = bot.get_channel(channel_id)
    if not isinstance(channel, discord.TextChannel):
        raise errors.WebhookChannelNotTextChannel()
    try:
        channel_webhooks = await channel.webhooks()
    except discord.Forbidden:
        return errors.MissingManageWebhooks()
    existing_webhooks = []
    for webhook in channel_webhooks:
        assert webhook.user is not None
        if webhook.user.id == bot.user.id:
            existing_webhooks.append(webhook)
    if len(existing_webhooks) == 0:
        try:
            webhook = await channel.create_webhook(
                name=bot.user.name, avatar=await bot.user.avatar_url_as().read()
            )
            await Channel.update_or_create(
                defaults={"webhook_token": webhook.token, "webhook_id": webhook.id},
                channel_id=channel_id,
            )
        except discord.Forbidden:
            return errors.MissingManageWebhooks()
        return webhook
    elif len(existing_webhooks) == 1:
        webhook = existing_webhooks[0]
        stored_webhook = await Channel.get_or_none(channel_id=channel_id)
        if webhook.token is None:
            await webhook.delete()
            return await create_webhook(channel_id, bot, attempt=attempt + 1)
        elif (
            stored_webhook is None
            or stored_webhook.webhook_token != webhook.token
            or stored_webhook.webhook_id != webhook.id
        ):
            await Channel.update_or_create(
                defaults={"webhook_token": webhook.token, "webhook_id": webhook.id},
                channel_id=channel_id,
            )
            return webhook
        else:
            return webhook
    else:  # More than one webhook by this bot in that channel. THIS SHOULD NOT HAPPEN
        stored_webhook = await Channel.get_or_none(channel_id=channel_id)
        for webhook in existing_webhooks:
            if (
                stored_webhook is None  # Nothing is stored, delete all
                or stored_webhook.webhook_token != webhook.token
                or stored_webhook.webhook_id != webhook.id
            ):
                # if the webhook does not match the stored one, delete it
                await webhook.delete()
        return await create_webhook(channel_id, bot, attempt=attempt + 1)


async def send_log_once(
    guild_id: int,
    bot: Bot,
    logger_type: str,
    files: Optional[List[discord.File]] = None,
    file: Optional[discord.File] = None,
    content: Optional[str] = None,
    embeds: Optional[List[discord.Embed]] = None,
) -> None:
    channel_logger = await ServerLogger.get_logger(guild_id, bot, logger_type)
    if channel_logger is not None:
        await channel_logger.send_log(
            content=content, embeds=embeds, files=files, file=file
        )


class ServerLogger:
    def __init__(
        self,
        bot: Bot,
        logger_type: str,
        channel_id: int,
        webhook: Optional[discord.Webhook] = None,
    ) -> None:
        self.channel_id = channel_id
        self.bot = bot
        self.has_webhook = False
        self.logger_type = logger_type
        self.webhook: Optional[discord.Webhook]
        if webhook is not None:
            self.has_webhook = True
            self.webhook = webhook

    @classmethod
    async def get_logger(cls, guild_id: int, bot: Bot, logger_type: str):  # type: ignore
        logger = await LoggingChannel.get_or_none(
            guild_id=guild_id, logger_type=logger_type
        )
        if logger is None:
            return None
        await logger.fetch_related("channel")
        assert isinstance(logger.channel, Channel)
        if (
            logger.channel.webhook_id is not None
            and logger.channel.webhook_token is not None
        ):
            webhook = discord.Webhook.partial(
                id=logger.channel.webhook_id,
                token=logger.channel.webhook_token,
                adapter=AsyncWebhookAdapter(bot.session),
            )
            return cls(bot, logger_type, logger.channel_id, webhook=webhook)
        else:
            return cls(bot, logger_type, logger.channel_id)

    async def send_log(
        self,
        content: Optional[str] = None,
        embeds: Optional[List[discord.Embed]] = None,
        file: Optional[discord.File] = None,
        files: Optional[List[discord.File]] = None,
    ) -> None:
        if (
            not self.has_webhook
        ):  # did not use if because if the webhook fails in above then this will be true
            webhook = await create_webhook(self.channel_id, self.bot)
            if isinstance(webhook, errors.MissingManageWebhooks):
                channel = self.bot.get_channel(self.channel_id)
                assert isinstance(channel, discord.TextChannel)
                try:
                    if embeds is None or len(embeds) == 0:
                        await channel.send(content=content, files=files, file=file)
                    else:
                        for embed in embeds:
                            add_permissions_text = "Logging requires your action to function correctly. [Click here](https://docs.messagemanager.xyz) for more info "
                            if embed.description:
                                embed.description = (
                                    str(embed.description)
                                    + "\n\n"
                                    + add_permissions_text
                                )
                            else:
                                embed.description = add_permissions_text
                        if len(embeds) == 1:
                            await channel.send(
                                content=content, embed=embeds[0], files=files, file=file
                            )
                        else:
                            await channel.send(content=content, files=files, file=file)
                            for embed in embeds:
                                await channel.send(embed=embed)
                except discord.Forbidden:
                    pass
            else:
                self.webhook = webhook
                self.has_webhook = True

        if self.has_webhook:
            try:
                await self.webhook.send(  # type: ignore
                    wait=True,
                    content=content,
                    embeds=embeds,
                    file=file,
                    files=files,
                    username="Message Manager - Logs",
                    avatar_url=self.bot.user.avatar_url,
                )
            except (discord.Forbidden, discord.NotFound):
                await Channel.update_or_create(
                    defaults={"webhook_token": None, "webhook_id": None},
                    channel_id=self.channel_id,
                )
                self.webhook = None
                self.has_webhook = False

                new_webhook = await create_webhook(self.channel_id, self.bot)
                if not isinstance(new_webhook, errors.MissingManageWebhooks):
                    self.webhook = new_webhook
                    self.has_webhook = True
                    await self.webhook.send(  # type: ignore
                        wait=True,
                        content=content,
                        embeds=embeds,
                        file=file,
                        files=files,
                        username="Message Manager - Logs",
                        avatar_url=self.bot.user.avatar_url,
                    )
