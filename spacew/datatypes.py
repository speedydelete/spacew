
'''various types and dataclasses'''

from typing import Literal, Sequence
from datetime import date, time, datetime
from dataclasses import dataclass


type RSG = Literal[-1, 0, 1, 2, 3, 4, 5]

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
    sn: int = -1
    size: int = -1
    magnitude: str = ''
    zmcl: str = ''
    location: str = ''

@dataclass
class Flare(BaseData):
    '''solar flare data'''
    flux: str = ''
    start: time | None = None
    maximum: time | None = None
    end: time | None = None

@dataclass
class DayData(BaseData):
    '''space weather for a previous day'''
    r_avg: RSG = -1
    r_min: RSG = -1
    r_max: RSG = -1
    s_avg: RSG = -1
    s_min: RSG = -1
    s_max: RSG = -1
    g_avg: RSG = -1
    g_min: RSG = -1
    g_max: RSG = -1
    kps: Sequence[Kp] = ()
    aps: Sequence[Ap] = ()
    sn: int = -1
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

@dataclass
class CurrentData(BaseData):
    '''current space weather'''
    dt: datetime = datetime.now()
    r: int = -1
    r_24h_max: int = -1
    s: int = -1
    s_24h_max: int = -1
    g: int = -1
    g_24h_max: int = -1
    kp: Kp = '-1'
    ap: int = -1
    sn: int = -1
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
    rotation: int = -1
    wind_speed: float = -1.0
    wind_density: float = -1.0
    bt: float = -1
    bz: float = -1
    dst: float = -1


type MultiDayData = dict[date, DayData]
