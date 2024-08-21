
'''spacew Discord bot'''

# pylint: disable=eval-used

import logging
import sys
import discord
from discord.ext import tasks
# these 2 lines fail when this is run directly
# but work when this is run by discord_bot_main.py
import discord_bot.config as config_parser
import now, cli


config = config_parser.load()

logger = logging.getLogger('spacew_bot')


intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(
    intents=intents,
    allowed_mentions=discord.AllowedMentions(everyone=True),
)


@client.event
async def on_ready():
    global config
    handler = logging.StreamHandler(sys.stdout)
    print(logging.getLogger('discord').handlers[1].formatter)
    handler.setFormatter(logging.getLogger('discord').handlers[1].formatter)
    logger.addHandler(handler)
    logger.info('logged in as %s', client.user)
    config = await config_parser.add_client(config, client)
    set_now.start()
    status.start()


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    # if message.content.startswith('$hello'):
    #     await message.channel.send('Hello!')


current = now.get()
@tasks.loop(seconds=14)
async def set_now():
    global current
    current = now.get()


@tasks.loop(seconds=30)
async def status():
    if config.status_enabled:
        logger.info('sending status message')
        message = eval('f"""' + config.status_message + '"""')
        if config.status_edit:
            await config.status_edit_message.edit(content=message) # type: ignore
        else:
            await config.status_channel.send(message) # type: ignore
