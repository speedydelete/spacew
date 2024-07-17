
from datetime import date, timedelta
import os
import ftplib
import pickle
from time import time
import requests
from const import *


def get_swpc_ftp_file(file: str, encoding='utf-8') -> str:
    '''retrieves a file using ftp from swpc'''
    fdir, file = os.path.split(file)
    ftp = ftplib.FTP('ftp.swpc.noaa.gov', encoding=encoding)
    ftp.login()
    ftp.cwd(fdir)
    out = []
    ftp.retrbinary(f'RETR {file}', out.append)
    return ''.join([x.decode(encoding) for x in out])


def load_txt_data(data: str | None, start: date, end: date, first: date | None, mul: int = 1) -> list[list[str]]:
    '''loads data in the .txt format used by api's'''
    data = [line for line in data.split('\n') if len(line) > 0 and not line[0] in ('#', ':')]
    data += [''] * mul
    if first is None:
        first = date.fromisoformat('-'.join(data[0].split(' ')[:3]))
    start = (start - first).days
    end = (end - first).days
    data = data[start * mul:end * mul]
    out = []
    for line in data:
        line = line.split(' ')
        line = [x for x in line if x != '']
        out.append(line)
    if out[-1] == []:
        out = out[:-mul]
    return out


def get_kp_ap_data(start: date, end: date, refresh: bool = False) -> dict[str, dict[str, str | int]]:
    '''gets the kp/ap values for certain date(s)'''
    out = {}
    today = date.today()
    if end <= today + timedelta(days=3):
        if os.path.exists('.spacew_cache'):
            with open('.spacew_cache', 'rb') as file:
                cache_time, data, preds, _ = pickle.loads(file.read())
            if time() - cache_time > 3600:
                refresh = True
        else:
            refresh = True
        if refresh:
            data = requests.get(GFZ_URL + 'Kp_ap_since_1932.txt').text
            data += '\n'.join(requests.get(GFZ_URL + 'Kp_ap_nowcast.txt').text.split('\n')[-9:])
            preds = requests.get('https://services.swpc.noaa.gov/text/3-day-forecast.txt').text
            preds = [x.split(' ')[1:] for x in preds.split('\n')[14:22]]
            preds = [[y for y in x if y != ''] for x in preds]
            preds = [[preds[j][i] for j in range(8)] for i in range(3)]
            with open('.spacew_cache', 'wb+') as file:
                file.write(pickle.dumps([time(), data, preds, None]))
        data = load_txt_data(data, start, end, GFZ_FIRST_DATE if (today - start).days < 28 else None, mul=8)
        for i, line in enumerate(data):
            if line[7] == '-1.000':
                data[i][7] = preds[0][i % 8]
        for i, day in enumerate(preds):
            for hour in day:
                dd = today + timedelta(days=i)
                data.append((str(dd.year).zfill(4), str(dd.month).zfill(2), str(dd.day).zfill(2), \
                            0, 0, 0, 0, hour, KP_TO_AP_MAP[KP_VALUE_MAP[hour]], '0'))
        for i in range(len(data)//8):
            kps, aps = [], []
            for line in data[i*8:i*8+8]:
                kps.append(KP_VALUE_MAP[line[7]])
                aps.append(int(line[8]))
            key = '-'.join(data[i*8][:3])
            out[key] = {
                'kp': tuple(kps),
                'ap': tuple(aps),
            }
    return out


def get_solar_data(start: date, end: date, refresh: bool = False):
    '''gets data on the sun's activity for date(s)'''
    out = {}
    if end.year < date.today().year:
        data = get_swpc_ftp_file(f'pub/warehouse/{start.year}/{start.year}_DSD.txt')
        data = load_txt_data(data, start, end, date(start.year, 1, 1))
        for line in data:
            out['-'.join(line[:3])] = {
                'flux': int(line[4]),
                'spots': int(line[5]),
                'spotarea': int(line[6]),
                'new_regions': int(line[7]),
                'c_flares': int(line[10]),
                'm_flares': int(line[11]),
                'x_flares': int(line[12]),
            }
    elif end.year == date.today().year:
        for day in range((end - start).days):
            out[str(start + timedelta(days=day))] = {
                'flux': '-999',
                'spots': '-999',
                'new_regions': '-999',
                'c_flares': '-999',
                'm_flares': '-999',
                'x_flares': '-999',
            }
    else:
        pass
    return out
