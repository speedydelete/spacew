
'''various types and dataclasses'''

from typing import Literal, Sequence
from datetime import date, time, datetime
from dataclasses import dataclass


type RSG = Literal[9, 0, 1, 2, 3, 4, 5]

type Flux = str

type Kp = Literal['-1', '0', '0+', '1-', '1', '1+',
                  '2-', '2', '2+', '3-', '3', '3+', 
                  '4-', '4', '4+', '5-', '5', '5+', 
                  '6-', '6', '6+', '7-', '7', '7+', 
                  '8-', '8', '8+', '9-', '9', '9+']

type Ap = int


@dataclass
class BaseData:
    '''base data class'''

@dataclass
class Region(BaseData):
    '''active region data'''
    id: int = -1
    latitude: int = -1
    longitude: int = -1
    carrington_longitude: int = -1
    status: str = ''
    sunspots: int = -1
    area: float = -1.0
    spot_class: str = ''
    magnitude: str = ''
    c_flares: int = -1
    m_flares: int = -1
    x_flares: int = -1
    c_flare_prob: int = -1
    m_flare_prob: int = -1
    x_flare_prob: int = -1

@dataclass
class Flare(BaseData):
    '''solar flare data'''
    start_time: datetime = datetime(9999, 12, 31)
    start_flux: str = ''
    max_time: datetime = datetime(9999, 12, 31)
    max_flux: str = ''
    end_time: datetime = datetime(9999, 12, 31)
    end_flux: str = ''

@dataclass
class DayData(BaseData):
    '''space weather for a previous day'''
    day: date = date(9999, 12, 31)
    r_avg: RSG = 9
    r_min: RSG = 9
    r_max: RSG = 9
    s_avg: RSG = 9
    s_min: RSG = 9
    s_max: RSG = 9
    g_avg: RSG = 9
    g_min: RSG = 9
    g_max: RSG = 9
    kps: Sequence[Kp] = ()
    aps: Sequence[Ap] = ()
    sunspots: int = -1
    spot_area: float = -1
    f107: float = -1
    new_regions: int = -1
    bg_flux: Flux = ''
    max_flux: Flux = ''
    c_flares: int = -1
    m_flares: int = -1
    x_flares: int = -1
    regions: Sequence[Region] = ()
    flares: Sequence[Flare] = ()
    cycle: int = -1
    rotation: int = -1
    wind_speed: float = -1.0
    wind_density: float = -1.0
    bt: float = -1
    bz: float = -1
    dst: int = -1

@dataclass
class CurrentData(BaseData):
    '''current space weather'''
    dt: datetime = datetime.now()
    r: int = 9
    s: int = 9
    g: int = 9
    r_24h_max: int = 9
    s_24h_max: int = 9
    g_24h_max: int = 9
    kp: Kp = '-1'
    ap: int = -1
    sunspots: int = -1
    f107: float = -1.0
    spot_area: float = -1.0
    new_regions: int = -1
    flux: Flux = ''
    flux_2h_max: Flux = ''
    flux_24h_max: Flux = ''
    c_flares: int = -1
    m_flares: int = -1
    x_flares: int = -1
    regions: Sequence[Region] = ()
    flares: Sequence[Flare] = ()
    cycle: int = -1
    rotation: int = -1
    wind_speed: float = -1.0
    wind_density: float = -1.0
    bt: float = -1
    bz: float = -1
    dst: int = -1


type MultiDayData = dict[date, DayData]
