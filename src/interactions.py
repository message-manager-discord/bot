from enum import IntEnum
from typing import Any, Awaitable, Dict, List, Optional, Union
from urllib.parse import quote as _uriquote

from discord import Embed, Guild, Member, User
from discord.colour import Colour
from discord.enums import ChannelType
from discord.http import Route
from discord.permissions import Permissions
from discord.role import Role, RoleTags
from discord.state import ConnectionState

from src.errors import NotResponded


class InteractionResponseFlags(IntEnum):
    EPHEMERAL = 64


class InteractionType(IntEnum):
    PING = 1
    APPLICATION_COMMAND = 2
    MESSAGE_COMPONENT = 3


class ApplicationCommandOptionType(IntEnum):
    SUB_COMMAND = 1
    SUB_COMMAND_GROUP = 2
    STRING = 3
    INTEGER = 4
    BOOLEAN = 5
    USER = 6
    CHANNEL = 7
    ROLE = 8
    MENTIONABLE = 9


class InteractionResponseType(IntEnum):
    Pong = 1
    ChannelMessageWithSource = 4
    DeferredChannelMessageWithSource = 5
    DeferredUpdateMessage = 6
    UpdateMessage = 7


class ComponentType(IntEnum):
    ActionRow = 1
    Button = 2
    Select = 3


class ButtonStyle(IntEnum):
    Primary = 1
    Secondary = 2
    Success = 3
    Danger = 4
    Link = 5


class InteractionMember(Member):
    def __init__(
        self, data: Dict[Any, Any], state: ConnectionState, guild: Optional[Guild]
    ) -> None:
        self.permissions = (
            Permissions(int(data["permissions"])) if "permissions" in data else None
        )
        super().__init__(data=data, state=state, guild=guild)  # type: ignore


class Interaction:
    def __init__(self, data: Dict[str, Any], state: ConnectionState) -> None:
        self._state = state
        self.responded = False
        self.id = int(data["id"])
        self.application_id = int(data["application_id"])
        self.type = InteractionType(int(data["type"]))
        self.guild_id = int(data["guild_id"]) if "guild_id" in data else None
        self.channel_id = int(data["channel_id"]) if "channel_id" in data else None
        self.member = (
            InteractionMember(data=data["member"], state=state, guild=self.guild)
            if "member"
            else None
        )
        self.user = (
            User(data=data["user"], state=self._state) if "user" in data else None  # type: ignore
        )
        self.token = data["token"]
        self.version = int(data["version"])

    @property
    def author(self) -> Union[InteractionMember, User]:
        author = self.member or self.user
        assert author is not None
        return author

    @property
    def guild(self) -> Optional[Guild]:
        guild = self._state._get_guild(self.guild_id)  # type: ignore
        return guild  # type: ignore

    async def respond(
        self,
        *,
        response_type: InteractionResponseType,
        content: Optional[str] = None,
        embeds: Optional[List[Embed]] = None,
        flags: Optional[InteractionResponseFlags] = None,
    ) -> None:
        route = InteractionRoute(
            method="POST",
            path="/interactions/{interaction_id}/{webhook_token}/callback",
            interaction_id=self.id,
            webhook_token=self.token,
        )
        embeds = [e.to_dict() for e in embeds] if embeds is not None else None

        json = {
            "type": response_type,
            "data": {
                "embeds": embeds,
                "content": content,
                "flags": flags,
            },
        }
        self.responded = True
        await self._state.http.request(route=route, json=json)  # type: ignore

    def edit_response(
        self,
        *,
        content: Optional[str] = None,
        embeds: Optional[List[Embed]] = None,
    ) -> Awaitable:
        if not self.responded:
            raise NotResponded()
        return self.edit_message(message_id="@original", content=content, embeds=embeds)

    async def edit_message(
        self,
        message_id: Union[str, int],
        *,
        content: Optional[str] = None,
        embeds: Optional[List[Embed]] = None,
    ) -> Dict[Any, Any]:
        route = InteractionRoute(
            method="PATCH",
            path="/webhooks/{application_id}/{webhook_token}/messages/{message_id}",
            application_id=self.application_id,
            webhook_token=self.token,
            message_id=message_id,
        )
        embeds = [e.to_dict() for e in embeds] if embeds is not None else None
        data = {
            "embeds": embeds,
            "content": content,
        }

        response = await self._state.http.request(route=route, json=data)  # type: ignore
        return response  # type: ignore

    async def create_followup(
        self, *, content: Optional[str] = None, embeds: Optional[List[Embed]] = None,
        flags: Optional[InteractionResponseFlags] = None,
    ) -> Dict[Any, Any]:
        embeds = [e.to_dict() for e in embeds] if embeds is not None else None
        data = {
            "embeds": embeds,
            "content": content,
            "flags": flags
        }
        route = InteractionRoute(
            method="POST",
            path="/webhooks/{application_id}/{webhook_token}/",
            application_id=self.application_id,
            webhook_token=self.token,
        )
        return await self._state.http.request(route=route, json=data)  # type: ignore

    async def delete_followup(self, message_id: Union[str, int]) -> None:
        route = InteractionRoute(
            method="DELETE",
            path="/webhooks/{application_id}/{webhook_token}/messages/{message_id}",
            application_id=self.application_id,
            webhook_token=self.token,
            message_id=message_id,
        )
        await self._state.http.request(route=route)  # type: ignore

    def delete_response(self) -> Awaitable:
        return self.delete_followup(message_id="@original")


class CommandInteraction(Interaction):
    def __init__(self, data: Dict[str, Any], state: ConnectionState) -> None:
        super().__init__(data=data, state=state)
        self.data = ApplicationCommandInteractionData(
            data=data["data"], state=self._state, guild=self.guild
        )


class ComponentInteraction(Interaction):
    def __init__(self, data: Dict[str, Any], state: ConnectionState) -> None:
        super().__init__(data=data, state=state)
        self.message = (
            data["message"] if "message" in data else None
        )  # I seriously can't be bothered to make a message class for components


class InteractionRoute(Route):
    BASE = "https://discord.com/api/v8"

    def __init__(self, method: str, path: str, **parameters: Any) -> None:
        self.path: str = path
        self.method: str = method
        url = self.BASE + self.path
        if parameters:
            url = url.format_map(
                {
                    k: _uriquote(v) if isinstance(v, str) else v
                    for k, v in parameters.items()
                }
            )
        self.url: str = url

        # major parameters:
        self.channel_id = parameters.get("channel_id")
        self.guild_id = parameters.get("guild_id")
        self.webhook_id = parameters.get("webhook_id")
        self.webhook_token = parameters.get("webhook_token")
        self.interaction_id = parameters.get("interaction_id")

    @property
    def bucket(self) -> str:
        # the bucket is just method + path w/ major parameters
        return f"{self.channel_id}:{self.guild_id}:{self.webhook_id}:{self.webhook_token}:{self.path}"


class ApplicationCommandInteractionData:
    def __init__(
        self, data: Dict[str, Any], state: ConnectionState, guild: Optional[Guild]
    ) -> None:
        self.id = int(data["id"])
        self.name = data["name"]
        self.resolved = data["resolved"] if "resolved" in data else None
        self.options = (
            [
                ApplicationCommandInteractionDataOption(
                    data=d, resolved=self.resolved, state=state, guild=guild
                )
                for d in data["options"]
            ]
            if "options" in data
            else None
        )
        self.custom_id = data["custom_id"] if "custom_id" in data else None
        self.component_type = (
            ComponentType(int(data["component_type"]))
            if "component_type" in data
            else None
        )


class ApplicationCommandInteractionDataOption:
    def __init__(
        self,
        data: Dict[str, Any],
        resolved: Dict[str, Dict[str, Any]],
        state: ConnectionState,
        guild: Optional[Guild] = None,
    ) -> None:
        self.name = data["name"]
        self.type = ApplicationCommandOptionType(int(data["type"]))
        self._resolved = resolved
        if "value" in data:
            self.raw_value = data["value"]
            self.options = None
            if self.type == ApplicationCommandOptionType.CHANNEL:
                if (
                    "channels" not in resolved
                    or self.raw_value not in resolved["channels"]
                ):
                    self.value = self.raw_value
                else:
                    channel_data = resolved["channels"][self.raw_value]
                    self.value = PartialChannel(channel_data)
            elif self.type == ApplicationCommandOptionType.ROLE:
                if guild is not None:
                    cached_role = guild.get_role(int(self.raw_value))
                else:
                    cached_role = None
                role: Union[PartialRole, Role]
                if cached_role is None:
                    if (
                        "roles" not in resolved
                        or self.raw_value not in resolved["roles"]
                    ):
                        self.value = self.raw_value
                    else:
                        role_data = resolved["role"][self.raw_value]
                        role = PartialRole(role_data)
                else:
                    role = cached_role
                self.value = role
            elif self.type in (
                ApplicationCommandOptionType.USER,
                ApplicationCommandOptionType.INTEGER,
                ApplicationCommandOptionType.MENTIONABLE,
            ):  # NOTE: Have not implemented user or member since that is currently not used.
                self.value = int(self.raw_value)
            else:
                self.value = self.raw_value

        elif "options" in data:
            self.value = self.raw_value = None
            self.options = [
                ApplicationCommandInteractionDataOption(
                    data=d, resolved=self._resolved, state=state, guild=guild
                )
                for d in data["options"]
            ]
        else:
            self.value = self.raw_value = self.options = None


class PartialRole:
    def __init__(self, data: Dict[str, Any]) -> None:
        self.id = int(data["id"])
        self.name = data["name"]
        self.permissions = Permissions(int(data.get("permissions", 0)))
        self.position = data.get("position", 0)
        self.colour = Colour(data.get("color", 0))
        self.hoist = data.get("hoist", False)
        self.managed = data.get("managed", False)
        self.mentionable = data.get("mentionable", False)

        self.tags: Optional[RoleTags]
        try:
            self.tags = RoleTags(data=data["tags"])  # type: ignore
        except KeyError:
            self.tags = None


class PartialChannel:
    def __init__(self, data: Dict[str, Any]) -> None:
        self.name = data["name"]
        self.id = int(data["id"])
        self.type = ChannelType(data["type"])
        self.permissions = Permissions(int(data["permissions"]))
