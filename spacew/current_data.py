
from datetime import datetime, date, timedelta
from dataclasses import dataclass
from apis import request, request_json, load_txt_data
from old_data import DayData
import util

@dataclass
class CurrentData(DayData):
    dt: datetime = datetime.now()
    r: int = -1
    s: int = -1
    g: int = -1

def curr_noaa_scales() -> tuple[int, int, int]:
    data = request_json('https://services.swpc.noaa.gov/products/noaa-scales.json')
    data = data['0']
    r = data['R']['Scale']
    s = data['S']['Scale']
    g = data['G']['Scale']
    return int(r), int(s), int(g)

def curr_kp_ap() -> tuple[str, int]:
    data = request('https://kp.gfz-potsdam.de/app/files/Kp_ap_nowcast.txt')
    data = load_txt_data(data, date.today(), date.today() + timedelta(days=1), mul=8)
    data = [line[7:9] for line in data]
    data = [[util.gfz_kp_to_real_kp(x[0]), int(x[1])] for x in data]
    data = [x for x in data if x[0] != '-1']
    return tuple(data[-1])


def now():
    out = CurrentData(dt=datetime.now())
    out.r, out.s, out.g = curr_noaa_scales()
    out.kp, out.ap = curr_kp_ap()
    return out
