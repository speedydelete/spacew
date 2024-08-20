
'''current space weather data'''

from datetime import datetime, date, timedelta, timezone
from datatypes import BaseData, CurrentData
import util
from apis import request, request_json, load_txt_data


def noaa_scales() -> CurrentData:
    data = request_json('products/noaa-scales.json')
    return CurrentData(
        r = int(data['0']['R']['Scale']),
        r_24h_max = int(data['-1']['R']['Scale']),
        s = int(data['0']['S']['Scale']),
        s_24h_max = int(data['-1']['S']['Scale']),
        g = int(data['0']['G']['Scale']),
        g_24h_max = int(data['-1']['G']['Scale']),
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
    if solar_wind[6] is None:
        solar_wind[6] = -1
    if solar_wind[7] is None:
        solar_wind[7] = -1
    return CurrentData(
        f107 = int(request_json('products/summary/10cm-flux.json')['Flux']),
        wind_speed = float(solar_wind[1]),
        wind_density = float(solar_wind[2]),
        bt = float(solar_wind[7]),
        bz = float(solar_wind[6]),
    )

def goes() -> CurrentData:
    dt_now = datetime.now(tz=timezone.utc)
    flux_now = request_json('json/goes/primary/xray-flares-latest.json')[0]['current_class']
    flux_maxes = request_json('json/goes/primary/xray-flares-7-day.json')
    flux_maxes = [(datetime.fromisoformat(flux['max_time']), flux['max_class']) for flux in flux_maxes]
    flux_maxes = [flux for flux in flux_maxes if (dt_now - flux[0]).days == 0]
    flux_24h_max = max((flux[1] for flux in flux_maxes), key=util.flux_to_float)
    flux_2h_max = max((flux[1] for flux in flux_maxes if (dt_now - flux[0]).seconds < 7200), key=util.flux_to_float)
    return CurrentData(
        flux = flux_now,
        flux_24h_max = flux_24h_max,
        flux_2h_max = flux_2h_max,
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
