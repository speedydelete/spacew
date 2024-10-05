
'''interaction with space weather API's'''

from typing import Any, Sequence
from types import UnionType
from datetime import date
import os
import ftplib
import requests


def _request(uri: str) -> requests.Response:
    if not uri.startswith('http'):
        uri = 'https://services.swpc.noaa.gov/' + uri
    req = requests.get(uri, timeout=3)
    if req.status_code < 400:
        return req
    else:
        raise ValueError(f'{req.status_code} {req.reason} while fetching {uri.split('/')[-1]}')

def request(uri: str) -> str:
    return _request(uri).text

def request_json(uri: str) -> Any:
    return _request(uri).json()

def swpc_ftp_file(file: str, encoding: str='utf-8') -> str:
    '''retrieves a file using ftp from swpc'''
    fdir, file = os.path.split(file)
    ftp = ftplib.FTP('ftp.swpc.noaa.gov', encoding=encoding)
    ftp.login()
    ftp.cwd(fdir)
    out = []
    ftp.retrbinary(f'RETR {file}', out.append)
    return ''.join([x.decode(encoding) for x in out])


def load_txt_data(data: str, start: date, end: date, first: date | None = None, mul: int = 1) -> list[list[str]]:
    '''loads data in the .txt format used by api's'''
    lines = [line for line in data.split('\n') if len(line) > 0 and not line[0] in ('#', ':')]
    lines += [''] * mul
    if first is None:
        first = date.fromisoformat('-'.join(lines[0].split(' ')[:3]))
    info = lines[(start - first).days * mul:(end - first).days * mul]
    out = []
    for line in info:
        line = line.split(' ')
        line = [x for x in line if x != '']
        out.append(line)
    if out[-1] == []:
        out = out[:-mul]
    return out


def validate(data: Any, schema: Any) -> bool:
    if isinstance(schema, type | UnionType):
        if not isinstance(data, schema):
            return False
    elif isinstance(schema, dict):
        if isinstance(data, dict):
            for key, value in schema.items():
                if key not in data:
                    return False
                if not validate(data[key], value):
                    return False
        elif isinstance(data, Sequence):
            for key, value in schema.items():
                if key >= len(data) or key < -len(data):
                    return False
                if not validate(data[key], value):
                    return False
        else:
            return False
    elif isinstance(schema, Sequence):
        if not isinstance(data, Sequence) or len(schema) != len(data):
            return False
        for item, item_schema in zip(data, schema):
            if not validate(item, item_schema):
                return False
    else:
        raise ValueError(f'invalid schema: {schema!r}')
    return True
