
'''configuration for the Discord bot'''

from typing import Any, Sequence
import json
from dataclasses import dataclass
import discord


class ConfigError(Exception):
    '''error for config'''

type Channel = discord.abc.GuildChannel | discord.Thread | discord.abc.PrivateChannel

@dataclass
class Alert:
    '''alert'''
    desc: str = ''
    check: str = 'False'
    message: str = ''
    last_check: bool = False

@dataclass
class Config:
    '''bot configuration'''
    token: str = ''
    default_message: str = ''
    refresh_interval: int = 9999999999999
    imports: Sequence[str] = ()
    status_enabled: bool = False
    status_interval: int = 9999999999999
    status_channel_id: int | None = None
    status_channel: Channel | None = None
    status_edit: bool = False
    status_edit_message_id: int | None = None
    status_edit_message: discord.Message | None = None
    status_message: str = ''
    alerts_enabled: bool = False
    alerts_interval: int = 9999999999999
    alerts_channel_id: int = -1
    alerts_channel: Channel | None = None
    alerts: Sequence[Alert] = ()
    commands_enabled: bool = False
    command_prefix: str = ''
    commands: dict[str, str] | None = None


config = None


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
    out.status_interval = int(key('status.interval'))
    out.status_edit = key('status.edit')
    if out.status_edit:
        out.status_edit_message_id = int(key('status.edit_message'))
    return out

def load_alerts(out: Config) -> Config:
    out.alerts_channel_id = int(key('alerts.channel'))
    out.alerts_interval = int(key('alerts.interval'))
    out.alerts = []
    for alert in key('alerts.alerts'):
        out.alerts.append(Alert(
            check = alert['check'],
            message = alert['message'],
            desc = alert['desc']
        ))
    return out

def load() -> Config:
    global config
    out = Config()
    with open('discord_bot/config.json', 'r', encoding='utf-8') as file:
        config = json.load(file)
    out.token = key('token')
    out.imports = key('imports')
    out.default_message = key('default_message')
    out.refresh_interval = key('refresh_interval')
    if key('status.enabled'):
        out.status_enabled = True
        out = load_status(out)
    if key('alerts.enabled'):
        out.alerts_enabled = True
        out = load_alerts(out)
    if key('commands.enabled'):
        out.commands_enabled = True
        out.command_prefix = key('commands.prefix')
        out.commands = key('commands.commands')
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
    if out.alerts_enabled:
        out.alerts_channel = client.get_channel(out.alerts_channel_id) # type: ignore
        if out.alerts_channel is None:
            raise ConfigError(f'unrecognized channel {key('alerts.channel')!r}')
    return out
