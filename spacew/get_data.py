
from typing import Any
import os
import ftplib
from datetime import date
import requests

def request(uri: str, mode: str = 'text') -> str | Any:
    req = requests.get(uri)
    if req.status_code < 400:
        if mode == 'text':
            return req.text
        elif mode == 'json':
            return req.json()
        else:
            raise ValueError(f'invalid mode {mode!r}, must be \'text\' or \'json\'')
    else:
        print(f'{req.status_code} {req.reason} while fetching {uri.split('/')[-1]}')

def get_swpc_ftp_file(file: str, encoding: str='utf-8') -> str:
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
