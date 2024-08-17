
from typing import Any
import os
import ftplib
from datetime import datetime, date, timedelta
from dataclasses import dataclass
from util import gfz_kp_to_real_kp, KP_TO_AP_MAP
import requests


GFZ_URL = 'https://www-app3.gfz-potsdam.de/'
GFZ_FIRST_DATE = date(1932, 1, 1)

SWPC_URL = 'https://services.swpc.noaa.gov/'

@dataclass
class DayData:
    dt: datetime = datetime.now()
    kp: str = '-1'
    ap: int = -1
    r: int = -1
    s: int = -1
    g: int = -1


def _request(uri: str) -> requests.Response:
    req = requests.get(uri)
    if req.status_code < 400:
        return req
    else:
        raise ValueError(f'{req.status_code} {req.reason} while fetching {uri.split('/')[-1]}')

def request(uri: str) -> str:
    return _request(uri).text

def request_json(uri: str) -> Any:
    return _request(uri).json

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


def get_kp_ap_data(start: date, end: date) -> dict[str, tuple[tuple[str, ...], tuple[int, ...]]]:
    '''gets the kp/ap values for certain date(s)'''
    out = {}
    today = date.today()
    data = request(GFZ_URL + 'kp_index/Kp_ap_since_1932.txt')
    data += '\n'.join(request(GFZ_URL + 'kp_index/Kp_ap_nowcast.txt').split('\n')[-9:])
    preds = request(SWPC_URL + 'text/3-day-forecast.txt')
    preds = preds.replace('(G1)', '    ').replace('(G2)', '    ').replace('(G3)', '    ')
    preds = preds.replace('(G4)', '    ').replace('(G5)', '    ')
    preds = [x.split(' ')[1:] for x in preds.split('\n')[14:22]]
    preds = [[y for y in x if y != ''] for x in preds]
    preds = [[str(preds[j][i]) for j in range(8)] for i in range(3)]
    data = load_txt_data(data, start, end, GFZ_FIRST_DATE if (today - start).days < 28 else None, mul=8)
    for i, line in enumerate(data):
        if line[7] == '-1.000':
            data[i][7] = preds[0][i % 8]
    for i, day in enumerate(preds):
        for hour in day:
            dd = today + timedelta(days=i)
            data.append([str(dd.year).zfill(4), str(dd.month).zfill(2), str(dd.day).zfill(2), \
                        '0', '0', '0', '0', hour, str(KP_TO_AP_MAP[gfz_kp_to_real_kp(hour)]), '0'])
    for i in range(len(data)//8):
        kps, aps = [], []
        for line in data[i*8:i*8+8]:
            kps.append(gfz_kp_to_real_kp(line[7]))
            aps.append(int(line[8]))
        key = date.fromisoformat('-'.join(data[i*8][:3]))
        out[key] = (tuple(kps), tuple(aps))
    return out
