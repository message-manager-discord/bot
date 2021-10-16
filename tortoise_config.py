from load_config import uri

TORTOISE_ORM = {
    "connections": {
        # Using a DB_URL string
        "default": uri
    },
    "apps": {
        "bot": {
            "models": ["src.models", "aerich.models"],
            "default_connection": "default",
        }
    },
}
