
'''various types and dataclasses'''

# pylint: disable=too-many-instance-attributes

from typing import Literal, Sequence
from datetime import time, datetime
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
class Region:
    '''active region data'''
    id: int = -1
    spots: int = -1
    size: int = -1
    magnitude: str = ''
    zmcl: str = ''
    location: str = ''

@dataclass
class Flare:
    '''solar flare data'''
    flux: str = ''
    start: time = time(-1, -1, -1)
    maximum: time = time(-1, -1, -1)
    end: time = time(-1, 1, -1)

@dataclass
class DayData:
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
    spots: int = -1
    f107: int = -1
    spot_area: int = -1
    new_regions: int = -1
    bg_flux: Flux = ''
    max_flux: Flux = ''
    c_flares: int = -1
    m_flares: int = -1
    x_flares: int = -1
    regions: Sequence[Region] = ()
    flares: Sequence[Flare] = ()
    kps: Sequence[Kp] = ()
    aps: Sequence[Ap] = ()

@dataclass
class CurrentData:
    '''current space weather'''
    dt: datetime = datetime.now()
    r: int = -1
    r_24h_max: int = -1
    s: int = -1
    s_24h_max: int = -1
    g: int = -1
    g_24h_max: int = -1
    spots: int = -1
    f107: int = -1
    spot_area: int = -1
    new_regions: int = -1
    flux: int = -1
    flux_2h_max: int = -1
    flux_24h_max: int = -1
    c_flares: int = -1
    m_flares: int = -1
    x_flares: int = -1
    regions: Sequence[Region] = ()
    flares: Sequence[Flare] = ()
    kp: Kp = '-1'
    ap: int = -1
