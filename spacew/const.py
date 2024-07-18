
from __future__ import annotations

from typing import Callable

import re
import math
from datetime import date


class SpaceWError(Exception):
    pass

class Namespace:
    
    def __init__(self, **kwargs):
        self.dict = kwargs
        self.__dict__.update(kwargs)

    def __getattr__(self, attr):
        try:
            return self.dict[attr]
        except KeyError:
            raise AttributeError(f'\'Namespace\' object has no attribute \'{attr}\'')
    
    def __setattr__(self, attr, value):
        self.__dict__[attr] = value
        self.dict[attr] = value
    
    def __add__(self, other: Namespace) -> Namespace:
        return Namespace(**(self.dict | other.dict))
    
    __or__ = __add__


VERSION = '1.0'


EARTH = 1
HOUR = 2
SUN = 4
FLARES = 8
AP = 16

TEXT_FLAG_MAP = {
    'default': EARTH | SUN,
    'all': EARTH | HOUR | SUN | FLARES,
    'sun': SUN | FLARES,
    'earth': EARTH | HOUR,
}

ANSI_ESCAPE = re.compile(r'\x1b(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')


GFZ_URL = 'https://www-app3.gfz-potsdam.de/kp_index/'
GFZ_FIRST_DATE = date(1932, 1, 1)
SWPC_FIRST_DATE = date(1996, 1, 1)
GOES14_END_DATE = date(2020, 1, 1)

DAYS_IN_MONTH = (None, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)


KP_VALUE = {
    '0.000': '0', '0.333': '0+',
    '0.667': '1-', '1.000': '1', '1.333': '1+',
    '1.667': '2-', '2.000': '2', '2.333': '2+',
    '2.667': '3-', '3.000': '3', '3.333': '3+',
    '3.667': '4-', '4.000': '4', '4.333': '4+',
    '4.667': '5-', '5.000': '5', '5.333': '5+',
    '5.667': '6-', '6.000': '6', '6.333': '6+',
    '6.667': '7-', '7.000': '7', '7.333': '7+',
    '7.667': '8-', '8.000': '8', '8.333': '8+',
    '8.667': '9-', '9.000': '9', '9.333': '9+',
    '0.00': '0', '0.33': '0+',
    '0.67': '1-', '1.00': '1', '1.33': '1+',
    '1.67': '2-', '2.00': '2', '2.33': '2+',
    '2.67': '3-', '3.00': '3', '3.33': '3+',
    '3.67': '4-', '4.00': '4', '4.33': '4+',
    '4.67': '5-', '5.00': '5', '5.33': '5+',
    '5.67': '6-', '6.00': '6', '6.33': '6+',
    '6.67': '7-', '7.00': '7', '7.33': '7+',
    '7.67': '8-', '8.00': '8', '8.33': '8+',
    '8.67': '9-', '9.00': '9', '9.33': '9+',
}

KP_TO_INT = {
    '0': 0, '0+': 1,
    '1-': 2, '1': 3, '1+': 4,
    '2-': 5, '2': 6, '2+': 7,
    '3-': 8, '3': 9, '3+': 10,
    '4-': 11, '4': 12, '4+': 13,
    '5-': 14, '5': 15, '5+': 16,
    '6-': 17, '6': 18, '6+': 19,
    '7-': 20, '7': 21, '7+': 22,
    '8-': 23, '8': 24, '8+': 25,
    '9-': 26, '9': 27, '9+': 28,
}

INT_TO_KP = {value: key for key, value in KP_TO_INT.items()}

KP_TO_AP = {
    '0': 0, '0+': 2,
    '1-': 3, '1': 4, '1+': 5,
    '2-': 6, '2': 7, '2+': 9,
    '3-': 12, '3': 15, '3+': 18,
    '4-': 22, '4': 27, '4+': 32,
    '5-': 39, '5': 48, '5+': 56,
    '6-': 67, '6': 80, '6+': 94,
    '7-': 111, '7': 132, '7+': 154,
    '8-': 179, '8': 207, '8+': 236,
    '9-': 300, '9': 400, '9+': 500,
}

_AP_TO_KP = {v: k for k, v in KP_TO_AP.items()}

def ap_to_kp(ap: int) -> str:
    if ap < 2:
        return '0'
    else:
        for k, v in _AP_TO_KP.items():
            if ap <= k:
                return v

KP_TO_G = {
    '0': 0, '0+': 0,
    '1-': 0, '1': 0, '1+': 0,
    '2-': 0, '2': 0, '2+': 0,
    '3-': 0, '3': 0, '3+': 0,
    '4-': 0, '4': 0, '4+': 0,
    '5-': 1, '5': 1, '5+': 1,
    '6-': 2, '6': 2, '6+': 2,
    '7-': 3, '7': 3, '7+': 3,
    '8-': 4, '8': 4, '8+': 4,
    '9-': 5, '9': 5, '9+': 5,
}

def flare_to_r(flare):
    let = flare[0]
    num = float(flare[1:])
    if let == 'X' and num >= 20:
        return 5
    elif let == 'X' and num >= 10:
        return 4
    elif let == 'X' and num >= 1:
        return 3
    elif let == 'M' and num >= 5:
        return 2
    elif let == 'M' and num >= 1:
        return 1
    else:
        return 0


def pfu_to_s(pfu):
    if pfu >= 100000:
        return 5
    elif pfu >= 10000:
        return 4
    elif pfu >= 1000:
        return 3
    elif pfu >= 100:
        return 2
    elif pfu >= 10:
        return 1
    else:
        return 0


def color_log_scale(mul: int | float, add: int | float = 0) -> Callable:
    def wrapper(value: int | float):
        return RSG_COLOR[pfu_to_s(math.exp(math.log(value)*mul+add))]
    return wrapper


KP_COLOR = {
    '0': '39', '0+': '39',
    '1-': '39', '1': '39', '1+': '39',
    '2-': '32', '2': '92', '2+': '32',
    '3-': '32', '3': '92', '3+': '32',
    '4-': '92', '4': '92', '4+': '92',
    '5-': '92', '5': '92', '5+': '92',
    '6-': '93', '6': '93', '6+': '93',
    '7-': '93', '7': '93', '7+': '93',
    '8-': '91', '8': '91', '8+': '91',
    '9-': '91', '9': '91', '9+': '91',
}

RSG_COLOR = {0: '39', 1: '32', 2: '92', 3: '93', 4: '91', 5: '91'}

KP = 'kp'
RSG = 'rsg'
SFU = 'sfu'
SPOTS = 'spots'
AREA = 'area'
NARS = 'nars'
FLARE = 'flare'
C_FLARE_COUNT = 'c_flare_count'
M_FLARE_COUNT = 'm_flare_count'
X_FLARE_COUNT = 'x_flare_count'

COLOR = {
    KP: KP_COLOR.get,
    AP: lambda ap: KP_COLOR[ap_to_kp(ap)],
    RSG: RSG_COLOR.get,
    SFU: color_log_scale(1.45),
    SPOTS: color_log_scale(1.45),
    AREA: color_log_scale(1.45, -2.3),
    NARS: RSG_COLOR.get,
    FLARE: lambda flare: RSG_COLOR[flare_to_r(flare)],
    C_FLARE_COUNT: lambda count: RSG_COLOR[flare_to_r('C' + str(count))],
    M_FLARE_COUNT: lambda count: RSG_COLOR[flare_to_r('M' + str(count))],
    X_FLARE_COUNT: lambda count: RSG_COLOR[flare_to_r('X' + str(count))],
}
