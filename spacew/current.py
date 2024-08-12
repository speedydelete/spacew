
from datetime import date, timedelta
from dataclasses import dataclass
from .get_data import request, load_txt_data
from . import util


def kp_ap() -> tuple[str, int]:
    data = request('https://kp.gfz-potsdam.de/app/files/Kp_ap_nowcast.txt')
    data = load_txt_data(data, date.today(), date.today() + timedelta(days=1), mul=8)
    data = [line[7:9] for line in data]
    data = [[util.gfz_kp_to_real_kp(x[0]), int(x[1])] for x in data]
    data = [x for x in data if x[0] != '-1']
    return tuple(data[-1])


@dataclass
class Now:
    kp: str = '-1'
    ap: int = -1
    g: int = -1

def now():
    out = Now()
    out.kp, out.ap = kp_ap()
    out.g = int(out.kp[0]) - 4
    if out.g < 0:
        out.g = 0
    return out
