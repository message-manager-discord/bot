from os import environ
from typing import Optional

"""
    All enviromental variables are in the format MM_BOT_{name} with the name below

    (Sets the url variable)
    POSTGRES_USER -> Role username
    POSTGRES_PASSWORD -> Role password
    POSTGRES_DB -> Database name 

    DEFAULT_PREFIX? -> This is the default prefix before commands. If a server prefix is set for a server this will be overridden. (default "~")
    DISCORD_TOKEN -> This is the discord bot token.
    SENTRY_DSN? -> sentry_dsn (defualt "")
    GUILD_CACHE_MAX? -> This is the maxium amount of guild-settings that will be cached before infrequently used ones are dropped (default 500)
    GUILD_CACHE_DROP? -> This is the amount of guilds that will be removed from the cache when it exceeds it's max size (defualt 50)
    BOT_OWNERS? -> comma seperated ids of bot owners, in the format "id,id2,id3" NOTE: There must not be a comma an a non int value at the end (default "")
                    Allows users to run dev only commands

    These varaible are for the offical production version only, and I provide no support for changing them from the defualt
    BOT_SELFHOST -> (default "True")
    LISTING_DBL_TOKEN -> (default "")
    LISTING_DBOATS_TOKEN -> (default "")
    LISTING_DEL_TOKEN -> (default "")
    LISTING_DBGG_TOKEN -> (default "")
    LISTING_TOPGG_TOKEN -> (default "")

"""


def try_get_config_var(name: str, optional: Optional[str] = None) -> str:
    result = environ.get(name)
    if not result:
        if optional is not None:
            result = optional
        else:
            raise Exception(f"Enviromental variable {name} not defined!")
    return result


token = try_get_config_var("DISCORD_TOKEN")
default_prefix = try_get_config_var("DEFAULT_PREFIX", "~")

uri = try_get_config_var("DATABASE_URL")


sentry_dsn = try_get_config_var("SENTRY_DSN", "")

guild_cache_max = int(try_get_config_var("GUILD_CACHE_MAX", "500"))
guild_cache_drop = int(try_get_config_var("GUILD_CACHE_DROP", "50"))


owners = [int(x) for x in try_get_config_var("BOT_OWNERS", "").split(",")]

# Ingore the values below
self_host = (
    not try_get_config_var("BOT_SELFHOST") == "False"
)  # Do not change this, if you do it will break


dbl_token = try_get_config_var("LISTING_DBL_TOKEN", "")
dboats_token = try_get_config_var("LISTING_DBOATS_TOKEN", "")
del_token = try_get_config_var("LISTING_DEL_TOKEN", "")
dbgg_token = try_get_config_var("LISTING_DBGG_TOKEN", "")
topgg_token = try_get_config_var("LISTING_TOPGG_TOKEN", "")
