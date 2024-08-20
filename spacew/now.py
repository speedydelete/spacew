
'''current space weather data'''

from datetime import datetime, date, timedelta
from datatypes import BaseData, CurrentData
import util
from apis import request, request_json, load_txt_data


def noaa_scales() -> CurrentData:
    data = request_json('products/noaa-scales.json')
    return CurrentData(
        r = data['0']['R']['Scale'],
        r_24h_max = data['-1']['R']['Scale'],
        s = data['0']['S']['Scale'],
        s_24h_max = data['-1']['S']['Scale'],
        g = data['0']['G']['Scale'],
        g_24h_max = data['-1']['G']['Scale'],
    )

def kp_ap() -> CurrentData:
    data = request('https://kp.gfz-potsdam.de/app/files/Kp_ap_nowcast.txt')
    data = load_txt_data(data, date.today(), date.today() + timedelta(days=1), mul=8)
    data = [line[7:9] for line in data]
    while data[-1][0] == '-1.000':
        data.pop()
    return CurrentData(kp=util.float_to_kp(data[-1][0]), ap=int(data[-1][1]))

def solar() -> CurrentData:
    solar_wind = request_json('products/geospace/propagated-solar-wind-1-hour.json')[-1]
    return CurrentData(
        f107 = request_json('products/summary/10cm-flux.json')['Flux'],
        wind_speed = solar_wind[1],
        wind_density = solar_wind[2],
        bt = solar_wind[7],
        bz = solar_wind[6],
    )

def goes() -> CurrentData:
    return CurrentData(
        flux = request_json('json/goes/primary/xray-flares-latest.json')[0]['current_class'],
    )

def rotation() -> CurrentData:
    # CR 2226 started on 2023-1-1 at 9:10 utc
    # rotations are 27.2753 days long
    out = datetime.now() - datetime(2023, 1, 1, 9, 10)
    out = out.days + (out.seconds + out.microseconds / 1e6) / 86400
    out = out / 27.2753 + 2266
    return CurrentData(
        rotation = int(out)
    )

def dst() -> CurrentData:
    return CurrentData(dst = request_json('products/kyoto-dst.json')[-1][1])


def _get() -> BaseData:
    return util.merge_data(
        CurrentData(dt=datetime.now()),
        noaa_scales(),
        kp_ap(),
        goes(),
        solar(),
        rotation(),
    )

def get() -> CurrentData:
    return _get() # type: ignore
