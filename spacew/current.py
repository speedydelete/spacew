
from datetime import datetime, date, timedelta
from get_data import DayData, request, request_json, load_txt_data
import util
from db_loader import load_db


def noaa_scales() -> tuple[int, int, int]:
    data = request_json('https://services.swpc.noaa.gov/products/noaa-scales.json')
    data = data['0']
    r = data['R']['Scale']
    s = data['S']['Scale']
    g = data['G']['Scale']
    return int(r), int(s), int(g)

def kp_ap() -> tuple[str, int]:
    data = request('https://kp.gfz-potsdam.de/app/files/Kp_ap_nowcast.txt')
    data = load_txt_data(data, date.today(), date.today() + timedelta(days=1), mul=8)
    data = [line[7:9] for line in data]
    data = [[util.gfz_kp_to_real_kp(x[0]), int(x[1])] for x in data]
    data = [x for x in data if x[0] != '-1']
    return tuple(data[-1])


def now():
    out = DayData()
    out.dt = datetime.now()
    out.r, out.s, out.g = noaa_scales()
    out.kp, out.ap = kp_ap()
    return out
