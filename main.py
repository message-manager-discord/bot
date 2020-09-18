# main.py
import discord
import asyncio
import logging
from src import db, checks, errors
from datetime import datetime, timezone
from discord.ext import commands
from config import token, uri

async def run():
    database = db.DatabasePool(uri)
    await database._init()

    logger = logging.getLogger('discord')
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    error_handler = logging.FileHandler(filename='discord_errors.log', encoding='utf-8', mode='w')
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(error_handler)
    logger.addHandler(handler)

    bot = Bot(
        db=database,
        logger=logger,
        checks = checks,
        errors = errors
    )

    bot.remove_command('help')

    extensions = [
        'cogs.maincog',
        'cogs.messages',
        'cogs.admin',
        'cogs.stats',
        'cogs.setup',
    ]
    print('Loading extensions...')
    for extension in extensions:
        bot.load_extension(extension)

    try:
        await bot.start(token)
    except KeyboardInterrupt:
        await db.close()
        await bot.logout()

class Bot(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(
            command_prefix = self.get_prefix,
            case_insensitive = True
        )
        self.db = kwargs.pop('db')
        self.logger = kwargs.pop('logger')
        self.checks = kwargs.pop('checks')
        self.errors = kwargs.pop('errors')


    async def get_prefix(self, message):
        prefix = await self.db.get_prefix(message.guild.id) # Fetch current server prefix from database
        return commands.when_mentioned_or(*prefix)(self, message)

    
loop = asyncio.get_event_loop()
loop.run_until_complete(run())
