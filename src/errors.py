# cogs/utils/errors.py

"""
Message Manager - A bot for discord
Copyright (C) 2020-2021 AnotherCat

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from typing import Any, Optional

from discord import DiscordException
from discord.ext.commands import CheckFailure


class ConfigNotSet(CheckFailure):
    pass


class DifferentServer(CheckFailure):
    def __init__(
        self,
        message: str = "That channel is not in this server, Please re-do the command",
        *args: Any,
    ) -> None:
        super().__init__(message, *args)


class DifferentAuthor(CheckFailure):
    def __init__(
        self,
        message: str = "That message was not sent by me! I cannot edit messages sent by others.",
        *args: Any,
    ) -> None:
        super().__init__(message, *args)


class ContentError(CheckFailure):
    pass


class MissingPermission(CheckFailure):
    pass


class MissingBotPermission(CheckFailure):
    pass


class InputContentIncorrect(CheckFailure):
    pass


class InputContentTooLong(CheckFailure):
    def __init__(
        self,
        message: Optional[str] = None,
        name_of_content: str = "Content",
        max_content_length: int = 2000,
        *args: Any,
    ) -> None:
        if message is None:
            message = (
                f"{name_of_content} must be {max_content_length} characters or less"
            )
        super().__init__(message, *args)


class JSONFailure(CheckFailure):
    pass


class MissingManageWebhooks(CheckFailure):
    pass


class DatabaseError(DiscordException):
    pass


class WebhookFailed(DiscordException):
    pass


class WebhookChannelNotTextChannel(CheckFailure):
    pass


class CacheError(DiscordException):
    pass


class NotResponded(DiscordException):
    def __init__(
        self, message: str = "The interaction has not been responded to", *args: Any
    ) -> None:
        super().__init__(message, *args)


class NoComponents(DiscordException):
    def __init__(
        self, message: str = "No components were provided", *args: Any
    ) -> None:
        super().__init__(message, *args)
