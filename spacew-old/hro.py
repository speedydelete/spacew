
from typing import Any

from const import *

def color(value: Any, map_name: str, width: int | None = None, display: bool = True, reset: bool = True) -> str:
    after = ''
    if display:
        if width is not None:
            after = f'{str(value).ljust(width)}'
        else:
            after = f'{value}'
        if reset:
            after += '\x1b[0m'
    return f'\x1b[{COLOR[map_name](value)}m{after}'

def main(output):
    out = ''
    mode = output.mode
    data = output.data
    out += '\x1b[96mdate       '
    if mode & EARTH:
        out += 'kp -  +  R-+ S-+ G-+ '
        if mode & AP:
            out += 'ap  -   +   '
        if mode & HOUR:
            out += '00 03 06 09 12 15 18 21 '.replace(' ', (' ap  ' if mode & AP else ' '))
    if mode & SUN:
        out += 'f10.7 spots area   +ars bgflux mxflux C  M  X  '
        if mode & FLARES:
            out += 'flares '
    out += '\x1b[0m\n'
    for day, info in data.items():
        int_kps = tuple(KP_TO_INT[x] for x in info.kps)
        kp = INT_TO_KP[round(sum(int_kps)/len(int_kps))]
        out += f'{color(kp, KP, display=False)}{day.strftime('%x'):<10} '
        if mode & EARTH:
            min_kp = INT_TO_KP[min(int_kps)]
            max_kp = INT_TO_KP[max(int_kps)]
            out += f'{color(kp, KP, 2)} {color(min_kp, KP, 2)} {color(max_kp, KP, 2)} '
            out += f'9{color(flare_to_r(info.bgflux), RSG, 1)}{color(flare_to_r(info.mxflux), RSG, 1)} '
            out += f'{color(pfu_to_s(info.p10), RSG, 1)}99 '
            out += f'{color(KP_TO_G[kp], RSG, 1)}{color(KP_TO_G[min_kp], RSG, 1)}{color(KP_TO_G[max_kp], RSG, 1)} '
            if mode & AP:
                ap = round(sum(info.aps)/len(info.aps))
                min_ap = min(info.aps)
                max_ap = max(info.aps)
                out += f'{color(ap, AP, 3)}{color(min_ap, AP, 3)}{color(max_ap, AP, 3)}'
            if mode & HOUR:
                if mode & AP:
                    for h_kp, h_ap in zip(info.kps, info.aps):
                        out += f'{color(h_kp, KP, 2)} {h_ap:<3} '
                else:
                    for h_kp in info.kps:
                        out += f'{color(h_kp, KP, 2)} '
        if mode & SUN:
            out += f'{color(info.f107, SFU, 5)} {color(info.spots, SPOTS, 5)} '
            out += f'{color(info.area, AREA, 6)} {color(info.nars, NARS, 4)} '
            out += f'{color(info.bgflux, FLARE, 6)} {color(info.mxflux, FLARE, 6)} '
            out += f'{color(info.cfs, C_FLARE_COUNT, 2)} '
            out += f'{color(info.mfs, M_FLARE_COUNT, 2)} '
            out += f'{color(info.xfs, X_FLARE_COUNT, 2)} '
            if mode & FLARES:
                pass
        out += '\n'
    return out
