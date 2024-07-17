
from const import *

def main(output):
    out = []
    mode = output['mode']
    data = output['data']
    out.append('\x1b[96mdate       R S G kp ')
    out.append('ap  ' if mode >= MORE else '')
    out.append('sunspots +ars flux ' if mode >= LESS else 'sunspots')
    out.append('C    M    X    00 03 06 09 12 15 18 21 ' if mode >= DEFAULT else 'flares')
    out.append('\x1b[0m\n')
    for day, info in data.items():
        kp = INT_TO_KP_MAP[round(sum(KP_TO_INT_MAP[x] for x in info['kp'])/len(info['kp']))]
        out.append(f'\x1b[{KP_COLOR_MAP[kp]}m{day} 9 9 {int(kp[:1]) - 4 if int(kp[:1]) >= 5 else 0:<1} {kp:<2} ')
        if mode >= MORE:
            out.append(f'{round(sum(info['ap'])/len(info['ap'])):<3} ')
        out.append(f'{info['spots']:<8} ')
        out.append(f'{info['new_regions']:<4} {info['flux']:<4} ' if mode >= LESS else '')
        if mode >= DEFAULT:
            out.append(f'{info['c_flares']:<4} {info['m_flares']:<4} {info['x_flares']:<4} ')
            out.append(' '.join(f'\x1b[{KP_COLOR_MAP[x]}m{x:<2}' for x in info['kp']))
        else:
            out.append(f'({(info['c_flares'] + info['m_flares'] + info['x_flares'])/3:<6} ')
        out.append('\x1b[0m\n')
    out = ''.join(out).split('\n')
    out = [line for line in out if line != '']
    return '\n'.join(out)
