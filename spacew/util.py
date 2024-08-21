
'''various utilities'''

# pylint: disable=eval-used

from typing import Literal
import math
from dataclasses import asdict
from datatypes import Kp, Ap, RSG, Flux, BaseData, MultiDayData


type Operation = Literal['==', '!=', '>', '>=', '<', '<=']

def assert_operation(op: Operation):
    assert op in ('==', '!=', '>', '>=', '<', '<=')


_KP_TO_AP: dict[Kp, Ap] = {
    '0': 0, '0+': 2, '1-': 3, '1': 4, '1+': 5,
    '2-': 6, '2': 7, '2+': 9, '3-': 12, '3': 15, '3+': 18,
    '4-': 22, '4': 27, '4+': 32, '5-': 39, '5': 48, '5+': 56,
    '6-': 67, '6': 80, '6+': 94, '7-': 111, '7': 132, '7+': 154,
    '8-': 179, '8': 207, '8+': 236, '9-': 300, '9': 400, '9+': 500,
}

_AP_TO_KP: dict[Ap, Kp] = {(v if v != 0 else 1): k for k, v in _KP_TO_AP.items()}

def float_to_kp(kp: int | float | str) -> Kp:
    kp = float(kp)
    out = str(round(kp))
    if kp > int(kp):
        out += '+'
    elif kp < int(kp):
        out += '-'
    return out # type: ignore

def kp_to_float(kp: Kp) -> float:
    if len(kp) == 1:
        return float(kp)
    elif kp.endswith('-'):
        return float(kp[0]) - 1/6
    else:
        return float(kp[0]) + 1/6

def kp_to_g(kp: Kp) -> RSG:
    return int(kp[0]) - 4 # type: ignore

def kp_to_ap(kp: Kp) -> Ap:
    return _KP_TO_AP[kp]

def ap_to_kp(ap: Ap) -> Kp:
    for k, v in _AP_TO_KP.items():
        if ap <= k:
            return v
    return '9+'

def compare_kp(kp1: Kp, kp2: Kp, op: Operation) -> bool:
    assert_operation(op)
    x, y = kp_to_float(kp1), kp_to_float(kp2)
    return eval(str(x) + op + str(y))

def average_kp(*kps: Kp) -> Kp:
    return float_to_kp(sum(map(kp_to_float, kps))/len(kps))

def sort_kps(*args: Kp) -> tuple[Kp, ...]:
    kps = list(args)
    kps.sort(key=kp_to_float)
    return tuple(kps)


FLUX_LETTER_MULS = {'X': 10000, 'M': 1000, 'C': 100, 'B': 10, 'A': 1}

def flux_to_float(flux: Flux) -> float:
    return FLUX_LETTER_MULS[flux[0]] * float(flux[1:])

def float_to_flux(flux: float) -> Flux:
    for letter, mul in FLUX_LETTER_MULS.items():
        if flux >= mul or letter == 'A':
            before, after = str(float(flux)).split('.')
            return letter + before.zfill(2) + '.' + after[:2]
    return ''

def compare_flux(flux1: Flux, flux2: Flux, op: Operation) -> bool:
    assert_operation(op)
    x, y = flux_to_float(flux1), flux_to_float(flux2)
    return eval(str(x) + op + str(y))

def flux_to_r(flux: Flux) -> RSG:
    if flux == '':
        return 0
    letter = flux[0]
    number = float(flux[1:])
    if number == 0:
        return 0
    if letter == 'X':
        return (5 if number >= 20 else (4 if number >= 10 else 3))
    elif letter == 'M':
        return (2 if number >= 5 else 1)
    else:
        return 0


def pfu_to_s(pfu):
    return min(5, math.floor(math.log10(pfu)))


def merge_data(first: BaseData, *datas: BaseData) -> BaseData:
    if not all(isinstance(data, type(first)) for data in datas):
        raise TypeError('all arguments of merge_data must be of the same type')
    blank = type(first)()
    for data in datas:
        for key, value in asdict(data).items():
            if value != getattr(blank, key):
                setattr(first, key, value)
    return first

def merge_multi_day_data(first: MultiDayData, *datas: MultiDayData) -> MultiDayData:
    for key in vars(first):
        filtered = [getattr(data, key) for data in datas]
        setattr(first, key, merge_data(getattr(first, key), *filtered))
    return first
