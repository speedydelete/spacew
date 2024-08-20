
'''current space weather data'''

from datetime import datetime, date, timedelta, timezone
from datatypes import BaseData, Region, Flare, CurrentData
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
        sunspots = int(request('https://www.sidc.be/SILSO/DATA/EISN/EISN_current.txt').split('\n')[-2][20:23]),
        f107 = int(request_json('products/summary/10cm-flux.json')['Flux']),
        wind_speed = float(solar_wind[1]),
        wind_density = float(solar_wind[2]),
        bt = float(solar_wind[7]),
        bz = float(solar_wind[6]),
    )

def flares() -> CurrentData:
    dt_now = datetime.now(tz=timezone.utc)
    flux_now = request_json('json/goes/primary/xray-flares-latest.json')[0]['current_class']
    flares = request_json('json/goes/primary/xray-flares-7-day.json')
    flares = [Flare(
        start_time=datetime.fromisoformat(flare['begin_time']),
        start_flux=flare['begin_class'],
        max_time=datetime.fromisoformat(flare['max_time']),
        max_flux=flare['max_class'],
        end_time=datetime.fromisoformat(flare['end_time']),
        end_flux=flare['end_class'],
    ) for flare in flares if (dt_now - datetime.fromisoformat(flare['begin_time'])).days == 0]
    flux_24h_max = flux_now
    flux_2h_max = flux_now
    c_flares = 0
    m_flares = 0
    x_flares = 0
    for flare in flares:
        match flare.max_flux[0]:
            case 'C':
                c_flares += 1
            case 'M':
                m_flares += 1
            case 'X':
                x_flares += 1
        if (dt_now - flare.max_time).days == 0 and util.compare_flux(flux_24h_max, flare.max_flux, '<'):
            flux_24h_max = flare.max_flux
        if (dt_now - flare.max_time).seconds < 7200 and util.compare_flux(flux_2h_max, flare.max_flux, '<'):
            flux_2h_max = flare.max_flux
    return CurrentData(
        flux = flux_now,
        flux_24h_max = flux_24h_max,
        flux_2h_max = flux_2h_max,
        c_flares = c_flares,
        m_flares = m_flares,
        x_flares = x_flares,
        flares = flares,
    )

def regions() -> CurrentData:
    regions = request_json('json/solar_regions.json')
    regions = [Region(
        id = region['region'],
        latitude = region['latitude'],
        longitude = region['longitude'],
        carrington_longitude = region['carrington_longitude'],
        status = region['status'],
        magnitude = region['mag_class'],
        sunspots = region['number_spots'],
        spot_class = region['spot_class'],
        area = (region['area'] if region['area'] != None else 0)/1000000,
        c_flares = region['c_xray_events'],
        m_flares = region['m_xray_events'],
        x_flares = region['x_xray_events'],
        c_flare_prob = region['c_flare_probability'],
        m_flare_prob = region['m_flare_probability'],
        x_flare_prob = region['x_flare_probability'],
    ) for region in regions]
    regions = [Region(
        id = region.id,
        latitude = region.latitude,
        longitude = region.longitude,
        carrington_longitude = region.carrington_longitude,
        status = region.status,
        magnitude = '' if region.magnitude is None else region.magnitude,
        sunspots = 0 if region.sunspots is None else region.sunspots,
        spot_class = '' if region.spot_class is None else region.spot_class,
        area = region.area,
        c_flares = region.c_flares,
        m_flares = region.m_flares,
        x_flares = region.x_flares,
        c_flare_prob = region.c_flare_prob,
        m_flare_prob = region.m_flare_prob,
        x_flare_prob = region.x_flare_prob,
    ) for region in regions]
    regions = {region.id: region for region in regions}
    regions = list(regions.values())
    regions.sort(key = lambda region: -region.id)
    return CurrentData(regions = regions)

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
    return CurrentData(dst = int(request_json('products/kyoto-dst.json')[-1][1]))


def _get() -> BaseData:
    return util.merge_data(
        CurrentData(dt=datetime.now()),
        noaa_scales(),
        kp_ap(),
        flares(),
        regions(),
        solar(),
        rotation(),
        dst(),
    )

def get() -> CurrentData:
    return _get() # type: ignore
