
from spacew import current
import config as config_parser
import discord
from discord.ext import tasks


intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(
    intents=intents,
    allowed_mentions=discord.AllowedMentions(everyone=True)
)


config = config_parser.load()

@client.event
async def on_ready():
    global config
    print(f'logged in as {client.user}')
    config = config_parser.add_client(config, client)


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


@tasks.loop(seconds=30)
async def status():
    print('running status')
    if config.status_enabled:
        await config.status_channel.send(eval('f"' + config.status_message + '"')) # type: ignore


client.run(config.token)

set_now.start()
status.start()
