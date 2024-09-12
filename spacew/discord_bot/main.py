
'''spacew Discord bot'''

# pylint: disable=eval-used

import logging
import discord
from discord.ext import tasks
# these 2 lines fail when this is run directly
# but work when this is run by discord_bot_main.py
import discord_bot.config as config_parser
import now
import importlib


log = logging.getLogger('spacew_bot')
log.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
format_string = ''
datefmt_string = '%Y-%m-%d %H:%M:%S'
formatter = logging.Formatter(format_string, datefmt=datefmt_string)
handler.setFormatter(logging.Formatter('[%(asctime)s] [%(levelname)-8s] %(name)s: %(message)s', '%Y-%m-%d %H:%M:%S'))
log.addHandler(handler)


config = config_parser.load()

for module in config.imports:
    _ = importlib.import_module(module)
    exec(f'{module} = _')


intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(
    intents=intents,
    allowed_mentions=discord.AllowedMentions(everyone=True),
    log_level=logging.DEBUG,
)


@client.event
async def on_ready():
    global config
    log.info('logged in as %s', client.user)
    config = await config_parser.add_client(config, client)
    set_now.start()
    status.start()
    alerts.start()


@client.event
async def on_message(message: discord.Message) -> None:
    if message.author == client.user:
        return
    if config.commands_enabled and message.content.startswith(config.command_prefix):
        msg = message.content[len(config.command_prefix):]
        args = msg.split(' ')[1:]
        for text, command in config.commands.items(): # type: ignore
            if msg.startswith(text):
                await message.reply(eval('f"""' + command + '"""'))


current = now.get()
@tasks.loop(seconds=config.refresh_interval)
async def set_now():
    global current
    current = now.get()


@tasks.loop(seconds=config.status_interval)
async def status():
    if config.status_enabled:
        log.info('sending status message')
        message = eval('f"""' + config.status_message + '"""')
        if config.status_edit:
            await config.status_edit_message.edit(content=message) # type: ignore
        else:
            await config.status_channel.send(message) # type: ignore


@tasks.loop(seconds=config.alerts_interval)
async def alerts():
    if config.alerts_enabled:
        for alert in config.alerts:
            if eval(alert.check):
                if not alert.last_check:
                    log.debug('alerting: %s', alert.desc)
                    await config.alerts_channel.send(alert.message) # type: ignore
                alert.last_check = True
            else:
                alert.last_check = False
