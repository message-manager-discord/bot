# main.py
import asyncio
import logging
import datetime
import discord
import config
from src import db, checks, errors
from discord.ext import commands


async def run():
    database = db.DatabasePool(config.uri)
    await database._init()
    logging.basicConfig(filename='discord.log', filemode='w', level=logging.INFO)

    logging.info('Started logging!')

    intents = discord.Intents(
        guilds = True,
        members = True,
        messages = True
    )

    bot = Bot(
        owner_ids = config.owners,
        activity = discord.Game(name="Watching our important messages!"),
        intents = intents,
        db=database,
        logger=logging,
        checks = checks,
        errors = errors,
        default_prefix=config.default_prefix,
        self_hosted = config.self_host
    )
    bot.start_time = datetime.datetime.utcnow()

    bot.remove_command('help')

    extensions = [
        'cogs.maincog',
        'cogs.messages',
        'cogs.admin',
        'cogs.stats',
        'cogs.setup',
    ]
    if not config.self_host:
        bot.join_log_channel = config.join_logs
        bot.dbl_token = config.dbl_token
        bot.dboats_token = config.dboats_token
        extensions.append(
        "jishaku"
        )
        extensions.append(
            'cogs.listing'
        )
    print('Loading extensions...')
    for extension in extensions:
        bot.load_extension(extension)

    try:
        await bot.start(config.token)
    except KeyboardInterrupt:
        await database.close()
        await bot.logout()

class Bot(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(
            command_prefix = self.get_prefix,
            case_insensitive = True,
            **kwargs
        )
        self.db = kwargs.pop('db')
        self.logger = kwargs.pop('logger')
        self.checks = kwargs.pop('checks')
        self.errors = kwargs.pop('errors')
        self.default_prefix = kwargs.pop('default_prefix')
        self.self_hosted = kwargs.pop('self_hosted')


    async def get_prefix(self, message):
        prefix = await self.db.get_prefix(message.guild) # Fetch current server prefix from database
        if message.guild is None:
            prefix = [prefix, '']
        return commands.when_mentioned_or(*prefix)(self, message)

    
loop = asyncio.get_event_loop()
loop.run_until_complete(run())
