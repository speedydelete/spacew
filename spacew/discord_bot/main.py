
import logging
from logging import DEBUG, INFO, WARN, ERROR
from spacew import current
import config as config_parser
import discord
from discord.ext import tasks


logger = logging.getLogger('discord.aurora_bot')

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(
    intents=intents,
    allowed_mentions=discord.AllowedMentions(everyone=True),
)


config = config_parser.load()


@client.event
async def on_ready():
    global config
    logger.info(f'logged in as {client.user}')
    config = await config_parser.add_client(config, client)
    set_now.start()
    status.start()


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    # if message.content.startswith('$hello'):
    #     await message.channel.send('Hello!')


now = current.now()
@tasks.loop(seconds=14)
async def set_now():
    global now
    now = current.now()


config.status_message = """```
space weather conditions at {now.dt.strftime('%Y/%m/%d %H:%M:%S UTC')}
R{now.r} S{now.s} G{now.g}
Kp{now.kp} ap {now.ap}
```"""


@tasks.loop(seconds=30)
async def status():
    if config.status_enabled:
        logger.info('sending status message')
        message = eval('f"""' + config.status_message + '"""')
        if config.status_edit:
            await config.status_edit_message.edit(content=message) # type: ignore
        else:
            await config.status_channel.send(message) # type: ignore


client.run(config.token)
