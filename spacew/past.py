
'''gets past space weather data'''

from datetime import date, timedelta
from dataclasses import asdict
from datatypes import DayData, MultiDayData
import util
from apis import request, swpc_ftp_file, load_txt_data


def kp_ap(start: date, end: date | None = None) -> MultiDayData:
    '''gets the kp/ap values for certain date(s)'''
    if end is None:
        end = start + timedelta(days=1)
    today = date.today()
    data = request('https://www-app3.gfz-potsdam.de/kp_index/Kp_ap_since_1932.txt')
    data += '\n'.join(request('https://www-app3.gfz-potsdam.de/kp_index/Kp_ap_nowcast.txt').split('\n')[-9:])
    preds = request('https://services.swpc.noaa.gov/text/3-day-forecast.txt')
    preds = preds.replace('(G1)', '    ').replace('(G2)', '    ').replace('(G3)', '    ')
    preds = preds.replace('(G4)', '    ').replace('(G5)', '    ')
    preds = [x.split(' ')[1:] for x in preds.split('\n')[14:22]]
    preds = [[y for y in x if y != ''] for x in preds]
    preds = [[str(preds[j][i]) for j in range(8)] for i in range(3)]
    data = load_txt_data(data, start, end, date(1932, 1, 1) if (today - start).days < 28 else None, mul=8)
    for i, line in enumerate(data):
        if line[7] == '-1.000':
            data[i][7] = preds[0][i % 8]
    for i, day in enumerate(preds):
        for hour in day:
            dd = today + timedelta(days=i)
            if dd >= end:
                continue
            data.append([str(dd.year).zfill(4), str(dd.month).zfill(2), str(dd.day).zfill(2), \
                        '0', '0', '0', '0', hour, str(util.kp_to_ap(util.float_to_kp(hour))), '0'])
    out = {}
    for i in range(len(data)//8):
        kps, aps = [], []
        for line in data[i*8:i*8+8]:
            kps.append(util.float_to_kp(line[7]))
            aps.append(int(line[8]))
        key = date.fromisoformat('-'.join(data[i*8][:3]))
        out[key] = DayData(kps=tuple(kps), aps=tuple(aps))
    return out


def solar_same_year(start: date, end: date | None = None) -> MultiDayData:
    '''gets data on the sun's activity for date(s) (must be the same year)'''
    if end is None:
        end = start + timedelta(days=1)
    out = {}
    if end.year < date.today().year:
        data = swpc_ftp_file(f'pub/warehouse/{start.year}/{start.year}_DSD.txt')
        data = load_txt_data(data, start, end, date(start.year, 1, 1))
        for line in data:
            key = date.fromisoformat('-'.join(line[:3]))
            out[key] = DayData(
                f107 = int(line[3]),
                sunspots = int(line[4]),
                spot_area = int(line[5])/2000000,
                new_regions = int(line[6]),
                bg_flux = str(line[8]),
                max_flux = 'X99.99',
                c_flares = int(line[9]),
                m_flares = int(line[10]),
                x_flares = int(line[11]),
            )
    elif end <= date.today():
        for day in range((end - start).days):
            out[start + timedelta(days=day)] = DayData()
    else:
        pass
    return out

def solar(start: date, end: date | None = None) -> MultiDayData:
    '''gets data on the sun's activity for date(s)'''
    if end is None:
        end = start + timedelta(days=1)
    out = {}
    for _year in range(end.year - start.year):
        year = start.year + _year
        data = solar_same_year(date(year, 1, 1), date(year + 1, 1, 1))
        for key, value in data.items():
            if key >= start and key < end:
                out[key] = value
    return out


def get(start: date, end: date | None = None) -> MultiDayData:
    if end is None:
        end = start + timedelta(days=1)
    return util.merge_mdd(
        kp_ap(start, end),
        solar(start, end),
    )
