
from typing import Literal, Iterable, NewType
from datetime import time, datetime
from dataclasses import dataclass


type RSG = Literal[0, 1, 2, 3, 4, 5]

type Flux = str

type Kp = Literal['0', '0+', '1-', '1', '1+', 
                  '2-', '2', '2+', '3-', '3', '3+', 
                  '4-', '4', '4+', '5-', '5', '5+', 
                  '6-', '6', '6+', '7-', '7', '7+', 
                  '8-', '8', '8+', '9-', '9', '9+']

type Ap = int


@dataclass
class Region:
    id: int = -1
    spots: int = -1
    size: int = -1
    magnitude: str = ''
    zmcl: str = ''
    location: str = ''

@dataclass
class Flare:
    flux: str = ''
    start: time = time(-1, -1, -1)
    maximum: time = time(-1, -1, -1)
    end: time = time(-1, 1, -1)

@dataclass
class DayData:
    r_avg: int = -1
    r_min: int = -1
    r_max: int = -1
    s_avg: int = -1
    s_min: int = -1
    s_max: int = -1
    spots: int = -1
    f107: int = -1
    spot_area: int = -1
    new_regions: int = -1
    bg_flux: str = ''
    max_flux: str = ''
    c_flares: int = -1
    m_flares: int = -1
    x_flares: int = -1
    regions: Iterable[Region] = ()
    flares: Iterable[Flare] = ()
    kp: Iterable[str] = ()
    ap: Iterable[str] = ()

@dataclass
class CurrentData:
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
    regions: Iterable[Region] = ()
    flares: Iterable[Flare] = ()
    kp: str = ''
    ap: int = -1
