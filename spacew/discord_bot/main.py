
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


config = config_parser.get_only_token()

@client.event
async def on_ready():
    global config
    print(f'logged in as {client.user}')
    config = config_parser.get(client)
    if config.status_enabled:
        await config.status_channel.send('current kp: ' + now.kp) # type:ignore
        print('sent')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    # if message.content.startswith('$hello'):
    #     await message.channel.send('Hello!')


now = current.now()
# @tasks.loop(seconds=14)
# async def set_now():
#     global now
#     now = current.now()


# @tasks.loop(seconds=30)
# async def status():
#     if config.status_enabled:
#         await config.status_channel.send('current kp: ' + now.kp) # type: ignore

client.run(config.token)
