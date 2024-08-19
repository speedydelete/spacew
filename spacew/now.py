
'''current space weather data'''

from datetime import datetime, date, timedelta
from datatypes import RSG, Kp, Ap, CurrentData
import util
from apis import request, request_json, load_txt_data


def curr_noaa_scales() -> tuple[RSG, RSG, RSG]:
    data = request_json('https://services.swpc.noaa.gov/products/noaa-scales.json')
    data = data['0']
    r = data['R']['Scale']
    s = data['S']['Scale']
    g = data['G']['Scale']
    return int(r), int(s), int(g) # type: ignore

def curr_kp_ap() -> tuple[Kp, Ap]:
    data = request('https://kp.gfz-potsdam.de/app/files/Kp_ap_nowcast.txt')
    data = load_txt_data(data, date.today(), date.today() + timedelta(days=1), mul=8)
    data = [line[7:9] for line in data]
    data = [[util.float_to_kp(x[0]), int(x[1])] for x in data]
    data = [x for x in data if x[0] != '-1']
    return tuple(data[-1])


def get() -> CurrentData:
    out = CurrentData(dt=datetime.now())
    out.r, out.s, out.g = curr_noaa_scales()
    out.kp, out.ap = curr_kp_ap()
    return out
