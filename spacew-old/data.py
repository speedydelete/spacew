
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


def get_kp_ap_data(start: date, end: date, refresh: bool = False) -> dict[str, dict[str, str | int]]:
    '''gets the kp/ap values for certain date(s)'''
    out = {}
    today = date.today()
    if end <= today + timedelta(days=3):
        if os.path.exists('.spacew_cache'):
            with open('.spacew_cache', 'rb') as file:
                cache_time, data, preds, _, _ = pickle.loads(file.read())
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
                file.write(pickle.dumps([time(), data, preds, None, None]))
        data = load_txt_data(data, start, end, GFZ_FIRST_DATE if (today - start).days < 28 else None, mul=8)
        for i, line in enumerate(data):
            if line[7] == '-1.000':
                data[i][7] = preds[0][i % 8]
        for i, day in enumerate(preds):
            for hour in day:
                dd = today + timedelta(days=i)
                data.append((str(dd.year).zfill(4), str(dd.month).zfill(2), str(dd.day).zfill(2), \
                            0, 0, 0, 0, hour, KP_TO_AP[KP_VALUE[hour]], '0'))
        for i in range(len(data)//8):
            kps, aps = [], []
            for line in data[i*8:i*8+8]:
                kps.append(KP_VALUE[line[7]])
                aps.append(int(line[8]))
            key = date.fromisoformat('-'.join(data[i*8][:3]))
            out[key] = Namespace(
                kps = tuple(kps),
                aps = tuple(aps),
            )
    return out


def get_solar_data(start: date, end: date, refresh: bool = False):
    '''gets data on the sun's activity for date(s)'''
    out = {}
    if end.year < date.today().year:
        data = get_swpc_ftp_file(f'pub/warehouse/{start.year}/{start.year}_DSD.txt')
        data = load_txt_data(data, start, end, date(start.year, 1, 1))
        for line in data:
            key = date.fromisoformat('-'.join(line[:3]))
            out[key] = Namespace(
                f107 = int(line[3]),
                spots = int(line[4]),
                area = int(line[5]),
                nars = int(line[6]),
                bgflux = str(line[8]),
                mxflux = 'X99.99',
                cfs = int(line[9]),
                mfs = int(line[10]),
                xfs = int(line[11]),
            )
    elif end <= date.today():
        for day in range((end - start).days):
            out[start + timedelta(days=day)] = Namespace(
                f107 = 9999,
                spots = 99999,
                nars = 9999,
                area = 9999,
                bgflux = 'X99.99',
                mxflux = 'X99.99',
                cfs = 99,
                mfs = 99,
                xfs = 99,
            )
    else:
        pass
    return out


def get_goes_data(start: date, end: date, refresh: bool = False):
    '''gets GOES data for date(s)'''
    out = {}
    if end < GOES14_END_DATE:
        data = get_swpc_ftp_file(f'pub/warehouse/{start.year}/{start.year}_DPD.txt')
        data = load_txt_data(data, start, end, date(start.year, 1, 1))
        for line in data:
            key = date.fromisoformat('-'.join(line[:3]))
            out[key] = Namespace(
                p1 = float(line[3])/86400,
                p10 = float(line[4])/86400,
                p100 = float(line[5])/86400,
                e08 = float(line[6])/86400,
                e2 = float(line[7])/86400,
            )
    elif end <= date.today():
        for day in range((end - start).days):
            out[start + timedelta(days=day)] = Namespace(
                p1 = -1,
                p10 = -1,
                p100 = -1,
                e08 = -1,
                e2 = -1,
            )
    else:
        pass
    return out
