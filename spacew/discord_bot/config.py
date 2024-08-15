
from typing import Any
import json
import dataclasses
from dataclasses import dataclass
import discord


class ConfigError(Exception):
    pass

type Channel = discord.abc.GuildChannel | discord.Thread | discord.abc.PrivateChannel


global config

@dataclass
class Config:
    token: str = ''
    status_enabled: bool = False
    status_channel_id: int = -1
    status_channel: Channel | None = None
    status_message: str = ''
    alerts_enabled: bool = False
    alerts_channel: Channel | None = None


def key(key: str) -> Any:
    conf = config
    skey = key.split('.')
    for i, part in enumerate(skey):
        if part in conf:
            conf = conf[part]
        else:
            raise ConfigError(f'{'.'.join(skey[:i])!r} key is required')
    return conf


def load_status(out: Config) -> Config:
    out.status_channel_id = int(key('status.channel'))
    out.status_message = key('status.message')
    return out


def load() -> Config:
    global config
    out = Config()
    with open('config.json', 'r', encoding='utf-8') as file:
        config = json.load(file)
    out.token = key('token')
    if key('status.enabled'):
        out.status_enabled = True
        out = load_status(out)
    return out

def add_client(out: Config, client: discord.Client) -> Config:
    out.status_channel = client.get_channel(out.status_channel_id) # type: ignore
    if out.status_channel is None:
        raise ConfigError(f'unrecognized channel {key('status.channel')!r}')
    return out
