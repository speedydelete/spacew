
from typing import Iterable
from datetime import date, time, timedelta
from dataclasses import dataclass
import util
from apis import request, get_swpc_ftp_file, load_txt_data


@dataclass
class Region:
    id: int = -1
    spots: int = -1
    size: int = -1
    magnitude: str = ''
    zmcl: str = ''
    location: str = ''

@dataclass
class Flare:
    flux: str = ''
    start: time = time(-1, -1, -1)
    maximum: time = time(-1, -1, -1)
    end: time = time(-1, 1, -1)

@dataclass
class DayData:
    r_avg: int = -1
    r_min: int = -1
    r_max: int = -1
    s_avg: int = -1
    s_min: int = -1
    s_max: int = -1
    spots: int = -1
    f107: int = -1
    spot_area: int = -1
    new_regions: int = -1
    bg_flux: str = ''
    max_flux: str = ''
    c_flares: int = -1
    m_flares: int = -1
    x_flares: int = -1
    regions: Iterable[Region] = ()
    flares: Iterable[Flare] = ()
    kp: Iterable[str] = ()
    ap: Iterable[str] = ()


def get_kp_ap_data(start: date, end: date) -> dict[str, tuple[tuple[str, ...], tuple[int, ...]]]:
    '''gets the kp/ap values for certain date(s)'''
    out = {}
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
            data.append([str(dd.year).zfill(4), str(dd.month).zfill(2), str(dd.day).zfill(2), \
                        '0', '0', '0', '0', hour, str(util.KP_TO_AP_MAP[util.gfz_kp_to_real_kp(hour)]), '0'])
    for i in range(len(data)//8):
        kps, aps = [], []
        for line in data[i*8:i*8+8]:
            kps.append(util.gfz_kp_to_real_kp(line[7]))
            aps.append(int(line[8]))
        key = date.fromisoformat('-'.join(data[i*8][:3]))
        out[key] = (tuple(kps), tuple(aps))
    return out

def get_solar_data(start: date, end: date) -> dict[date, DayData]:
    '''gets data on the sun's activity for date(s)'''
    out = {}
    if end.year < date.today().year:
        data = get_swpc_ftp_file(f'pub/warehouse/{start.year}/{start.year}_DSD.txt')
        data = load_txt_data(data, start, end, date(start.year, 1, 1))
        for line in data:
            key = date.fromisoformat('-'.join(line[:3]))
            out[key] = DayData(
                f107 = int(line[3]),
                spots = int(line[4]),
                spot_area = int(line[5]),
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
