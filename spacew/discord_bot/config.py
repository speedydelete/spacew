
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
    status_channel: Channel | None = None
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


def load_status(client: discord.Client, out: Config, config: Any) -> Config:
    status_channel = client.get_channel(int(key('status.channel')))
    if status_channel is None:
        raise ConfigError(f'unrecognized channel {key('status.channel')!r}')
    out.status_channel = status_channel
    return out


def get(client: discord.Client) -> Config:
    global config
    out = Config()
    with open('config.json', 'r', encoding='utf-8') as file:
        config = json.load(file)
    out.token = key('token')
    if key('status.enabled'):
        out.status_enabled = True
        out = load_status(client, out, key('status'))
    return out

def get_only_token() -> Config:
    global config
    out = Config()
    with open('config.json', 'r', encoding='utf-8') as file:
        config = json.load(file)
    out.token = key('token')
    return out
