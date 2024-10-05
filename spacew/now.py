
'''current space weather data'''

from typing import Sequence
from datetime import datetime, timezone
from datatypes import Region, Flare, CurrentData
import util
from apis import request, request_json, validate


NOAA_SCALES_SCHEMA = {'0': {'R': {'Scale': str}, 'S': {'Scale': str}, 'G': {'Scale': str}}, \
                      '-1': {'R': {'Scale': str}, 'S': {'Scale': str}, 'G': {'Scale': str}}}
SOLAR_WIND_DATA_SCHEMA = {-1: [str, str, str, str, str, str, str, str, str | None, str | None, str | None, str]}

def get_regions() -> Sequence[Region]:
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
        area = (region['area'] if region['area'] is not None else 0)/1000000,
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
    regions.sort(key = lambda region: 0 if region.id is None else -region.id)
    return regions

def get_flares() -> CurrentData:
    dt_now = datetime.now(tz=timezone.utc)
    flux_now = request_json('json/goes/primary/xray-flares-latest.json')[0]['current_class']
    flares = request_json('json/goes/primary/xray-flares-7-day.json')
    flares = [Flare(
        start_time = datetime.fromisoformat(flare['begin_time']),
        start_flux = flare['begin_class'],
        max_time = datetime.fromisoformat(flare['max_time']) if flare['max_time'] is not None else None,
        max_flux = flare['max_class'],
        end_time = datetime.fromisoformat(flare['end_time']),
        end_flux = flare['end_class'],
    ) for flare in flares if (dt_now - datetime.fromisoformat(flare['begin_time'])).days == 0]
    flux_72h_max = flux_now
    flux_24h_max = flux_now
    flux_2h_max = flux_now
    c_flares = 0
    m_flares = 0
    x_flares = 0
    for flare in flares:
        if flare.max_time is None or flare.max_flux is None:
            continue
        match flare.max_flux[0]:
            case 'C':
                c_flares += 1
            case 'M':
                m_flares += 1
            case 'X':
                x_flares += 1
        diff = dt_now - flare.max_time
        if diff.days < 3 and util.compare_flux(flux_24h_max, flare.max_flux, '<'):
            flux_72h_max = flare.max_flux
        if diff.days == 0 and util.compare_flux(flux_24h_max, flare.max_flux, '<'):
            flux_24h_max = flare.max_flux
        if diff.seconds < 7200 and util.compare_flux(flux_2h_max, flare.max_flux, '<'):
            flux_2h_max = flare.max_flux
    return CurrentData(
        flux = flux_now,
        flux_72h_max = flux_72h_max,
        flux_24h_max = flux_24h_max,
        flux_2h_max = flux_2h_max,
        c_flares = c_flares,
        m_flares = m_flares,
        x_flares = x_flares,
        flares = flares,
    )

def get() -> CurrentData:
    out = CurrentData()
    out.dt = datetime.now()
    out.cycle = util.cycle(out.dt)
    out.rotation = util.rotation(out.dt)
    noaa_scales = request_json('products/noaa-scales.json')
    if validate(noaa_scales, NOAA_SCALES_SCHEMA):
        out.r = int(noaa_scales['0']['R']['Scale'])
        out.r_24h_max = int(noaa_scales['-1']['R']['Scale'])
        out.s = int(noaa_scales['0']['S']['Scale'])
        out.s_24h_max = int(noaa_scales['-1']['S']['Scale'])
        out.g = int(noaa_scales['0']['G']['Scale'])
        out.g_24h_max = int(noaa_scales['-1']['G']['Scale'])
    kp_ap_data = request_json('products/noaa-planetary-k-index.json')
    if validate(kp_ap_data, {-1: [str, str, str, str]}):
        out.kp = util.float_to_kp(kp_ap_data[-1][1])
        out.ap = int(kp_ap_data[-1][2])
    dst_data = request_json('products/kyoto-dst.json')
    if validate(dst_data, {-1: [str, str]}):
        out.dst = int(dst_data[-1][1])
    solar_wind_data = request_json('products/geospace/propagated-solar-wind-1-hour.json')
    if validate(solar_wind_data, SOLAR_WIND_DATA_SCHEMA):
        solar_wind_data = solar_wind_data[-1]
        out.wind_speed = float(solar_wind_data[1])
        out.wind_density = float(solar_wind_data[2])
        out.bz = float(solar_wind_data[6])
        out.bt = float(solar_wind_data[7])
    out.sunspots = int(request('https://www.sidc.be/SILSO/DATA/EISN/EISN_current.txt').split('\n')[-2][20:23])
    f107_data = request_json('products/summary/10cm-flux.json')
    if validate(f107_data, {'Flux': str}):
        out.f107 = int(f107_data['Flux'])
    out.regions = get_regions()
    out = util.merge_data(out, get_flares())
    return out # type: ignore
