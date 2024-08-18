
'''configuration for the Discord bot'''

from typing import Any
import json
from dataclasses import dataclass
import discord


class ConfigError(Exception):
    '''error for config'''

type Channel = discord.abc.GuildChannel | discord.Thread | discord.abc.PrivateChannel


@dataclass
class Config:
    '''bot configuration'''
    token: str = ''
    default_message: str = ''
    status_enabled: bool = False
    status_channel_id: int | None = None
    status_channel: Channel | None = None
    status_edit: bool = False
    status_edit_message_id: int | None = None
    status_edit_message: discord.Message | None = None
    status_message: str = ''
    alerts_enabled: bool = False
    alerts_channel: Channel | None = None

config = Config()


def key(k: str) -> Any:
    conf = config
    skey = k.split('.')
    for i, part in enumerate(skey):
        if part in conf: # type: ignore
            conf = conf[part] # type: ignore
        else:
            raise ConfigError(f'{'.'.join(skey[:i])!r} key is required')
    return conf


def load_status(out: Config) -> Config:
    out.status_channel_id = int(key('status.channel'))
    status_message = key('status.message')
    if status_message is None:
        out.status_message = out.default_message
    else:
        out.status_message = status_message
    out.status_edit = key('status.edit')
    if out.status_edit:
        out.status_edit_message_id = int(key('status.edit_message'))
    return out


def load() -> Config:
    global config
    out = Config()
    with open('config.json', 'r', encoding='utf-8') as file:
        config = json.load(file)
    out.token = key('token')
    out.default_message = key('default_message')
    if key('status.enabled'):
        out.status_enabled = True
        out = load_status(out)
    return out

async def add_client(out: Config, client: discord.Client) -> Config:
    if out.status_enabled:
        out.status_channel = client.get_channel(out.status_channel_id) # type: ignore
        if out.status_channel is None:
            raise ConfigError(f'unrecognized channel {key('status.channel')!r}')
        if out.status_edit_message_id is not None:
            out.status_edit_message = await out.status_channel.fetch_message(out.status_edit_message_id) # type: ignore
            if out.status_edit_message is None:
                raise ConfigError(f'unrecognized message {key('status.edit_message')!r}')
    return out
