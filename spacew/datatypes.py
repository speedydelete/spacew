
'''various types and dataclasses'''

from typing import Literal, Sequence
from datetime import date, datetime
from dataclasses import dataclass


type RSG = Literal[9, 0, 1, 2, 3, 4, 5] | None

type Flux = str | None

type KpNotNone = Literal['-1', '0', '0+', '1-', '1', '1+',
                         '2-', '2', '2+', '3-', '3', '3+', 
                         '4-', '4', '4+', '5-', '5', '5+', 
                         '6-', '6', '6+', '7-', '7', '7+', 
                         '8-', '8', '8+', '9-', '9', '9+']
type Kp = KpNotNone | None

type ApNotNone = int
type Ap = int | None


@dataclass
class BaseData:
    '''base data class'''

@dataclass
class Region(BaseData):
    '''active region data'''
    id: int | None = None
    latitude: int | None = None
    longitude: int | None = None
    carrington_longitude: int | None = None
    status: str | None = None
    sunspots: int | None = None
    area: float | None = None
    spot_class: str | None = None
    magnitude: str | None = None
    c_flares: int | None = None
    m_flares: int | None = None
    x_flares: int | None = None
    c_flare_prob: int | None = None
    m_flare_prob: int | None = None
    x_flare_prob: int | None = None

@dataclass
class Flare(BaseData):
    '''solar flare data'''
    start_time: datetime | None = None
    start_flux: str | None = None
    max_time: datetime | None = None
    max_flux: str | None = None
    end_time: datetime | None = None
    end_flux: str | None = None

@dataclass
class DayData(BaseData):
    '''space weather for a previous day'''
    day: date = date(9999, 12, 31)
    r_avg: RSG | None = None
    r_min: RSG | None = None
    r_max: RSG | None = None
    s_avg: RSG | None = None
    s_min: RSG | None = None
    s_max: RSG | None = None
    g_avg: RSG | None = None
    g_min: RSG | None = None
    g_max: RSG | None = None
    kps: Sequence[Kp] = ()
    aps: Sequence[Ap] = ()
    sunspots: int | None = None
    spot_area: float | None = None
    f107: float | None = None
    new_regions: int | None = None
    bg_flux: Flux = None
    max_flux: Flux = None
    c_flares: int | None = None
    m_flares: int | None = None
    x_flares: int | None = None
    regions: Sequence[Region] = ()
    flares: Sequence[Flare] = ()
    cycle: int | None = None
    rotation: int | None = None
    wind_speed: float | None = None
    wind_density: float | None = None
    bt: float | None = None
    bz: float | None = None
    dst: int | None = None

@dataclass
class CurrentData(BaseData):
    '''current space weather'''
    dt: datetime = datetime.now()
    r: int | None = None
    s: int | None = None
    g: int | None = None
    r_24h_max: int | None = None
    s_24h_max: int | None = None
    g_24h_max: int | None = None
    kp: Kp = None
    ap: int | None = None
    sunspots: int | None = None
    f107: float | None = None
    spot_area: float | None = None
    new_regions: int | None = None
    flux: Flux = None
    flux_2h_max: Flux = None
    flux_24h_max: Flux = None
    flux_72h_max: Flux = None
    c_flares: int | None = None
    m_flares: int | None = None
    x_flares: int | None = None
    regions: Sequence[Region] = ()
    flares: Sequence[Flare] = ()
    cycle: int | None = None
    rotation: int | None = None
    wind_speed: float | None = None
    wind_density: float | None = None
    bt: float | None = None
    bz: float | None = None
    dst: int | None = None


type MultiDayData = dict[date, DayData]
