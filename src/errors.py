from discord.ext.commands import CheckFailure


class ConfigNotSet(CheckFailure):
    pass


class ConfigError(CheckFailure):
    pass


class DifferentServer(CheckFailure):
    def __init__(self, **kwargs):
        self.message = "That channel is not in this server, Please re-do the command"
        super(kwargs)


class ContentError(CheckFailure):
    pass


class MissingPermission(CheckFailure):
    pass


class InputContentIncorrect(CheckFailure):
    pass


def setup(bot):
    print("    Errors!")
