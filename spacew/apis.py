
'''interaction with space weather API's'''

from typing import Any
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
    if isinstance(schema, dict):
        if not isinstance(data, dict):
            return False
        for key, value in schema.items():
            if key not in data:
                return False
            if not validate(data[key], value):
                return False
    elif isinstance(schema, list):
        if not isinstance(data, list) or len(schema) != len(data):
            return False
        for item in schema:
            if not validate(data[item], item):
                return False
    elif isinstance(schema, type):
        if not isinstance(data, schema):
            return False
    else:
        raise ValueError(f'invalid schema: {schema!r}')
    return True
