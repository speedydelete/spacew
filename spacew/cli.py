
'''spacew command line interface'''

from typing import Any, Callable, Sequence
from datetime import date, timedelta
import math
import re
import json
import sys
import os
import pprint
from dataclasses import asdict
import argparse
import dateutil
from datatypes import DayData, CurrentData, MultiDayData
from cache import get_past_data
from now import get as get_current_data
import util


VERSION = '1.0'

KP_COLOR = {
    None: '39', '0': '39', '0+': '39',
    '1-': '39', '1': '39', '1+': '39',
    '2-': '32', '2': '32', '2+': '32',
    '3-': '32', '3': '32', '3+': '32',
    '4-': '92', '4': '92', '4+': '92',
    '5-': '92', '5': '92', '5+': '92',
    '6-': '93', '6': '93', '6+': '93',
    '7-': '93', '7': '93', '7+': '93',
    '8-': '31', '8': '31', '8+': '31',
    '9-': '31', '9': '31', '9+': '31',
}

RSG_COLOR = {0: '39', 1: '32', 2: '92', 3: '93', 4: '31', 5: '31', 9: '39'}
FLUX_COLOR = {'A': '39', 'B': '32', 'C': '92', 'M': '93', 'X': '31'}
C_FLARE_COLOR = ('39', '32', '92', '93', '31')


ARCHIVE_CMDS = ('archive', 'history', 'on')
CURRENT_CMDS = ('current', 'now')
DISCORD_CMDS = ('discord', 'bot')
COMMANDS = ARCHIVE_CMDS + CURRENT_CMDS + DISCORD_CMDS

EARTH = 1
HOUR = 2
SUN = 4
FLARES = 8
REGIONS = 16
AP = 32
MODE_FLAG_MAP = {
    'default': EARTH | SUN,
    'earth': EARTH | HOUR,
    'sun': SUN | REGIONS | FLARES,
    'all': EARTH | HOUR | SUN | REGIONS | FLARES,
}


def color_log_scale(mul: int | float, add: int | float = 0) -> Callable:
    def wrapper(value: int | float):
        if value < 0:
            return RSG_COLOR[0]
        return RSG_COLOR[util.pfu_to_s(math.exp(math.log(value)*mul+add))]
    return wrapper

COLOR = {
    'kp': KP_COLOR.get,
    'ap': lambda ap: KP_COLOR[util.ap_to_kp(ap)],
    'rsg': RSG_COLOR.get,
    'sfu': color_log_scale(1.45),
    'sunspots': color_log_scale(1.45),
    'spot_area': lambda area: color_log_scale(1.25, -2.3)(area*2000000),
    'new_regions': RSG_COLOR.get,
    'flux': lambda flux: '39' if flux is None else FLUX_COLOR[flux[0]],
    'c_flare_count': lambda count: '39' if count is None else ('31' if count > 4 else C_FLARE_COLOR[count]),
    'm_flare_count': lambda count: '39' if count is None else (('31' if count > 1 else '92') if count > 0 else '39'),
    'x_flare_count': lambda count: '39' if count is None else ('31' if count > 0 else '39'),
}

def color(value: Any, map_name: str, width: int | None = None, actual: str | None = None, \
          display: bool = True, reset: bool = True, before: str = '') -> str:
    if actual is None:
        actual = str(value)
    text = ''
    if display:
        text = before + actual
        if width is not None:
            text = text.ljust(width)
        if reset:
            text += '\x1b[0m'
    return f'\x1b[{COLOR[map_name](value)}m{text}'


def format_current_data_text(info: CurrentData, flags: int) -> str:
    out = f'space weather conditions at {info.dt.strftime('%Y-%m-%d %H:%M:%S')}:\n'
    out += f'{color(info.r, 'rsg', before='R')} '
    out += f'{color(info.s, 'rsg', before='S')} '
    out += f'{color(info.g, 'rsg', before='G')} '
    out += f'(24h maxes: {color(info.r_24h_max, 'rsg', before='R')} '
    out += f'{color(info.s_24h_max, 'rsg', before='S')} '
    out += f'{color(info.g_24h_max, 'rsg', before='G')})\n'
    if flags & EARTH:
        out += f'{color(info.kp, 'kp', before='Kp')}{f' (ap: {color(info.ap, 'ap')})' if flags & AP else ''}, '
        out += f'Bt: {info.bt}, Bz: {info.bz}, Dst: {info.dst}\n'
    if flags & SUN:
        out += f'{color(info.sunspots, 'sunspots')} sunspots\n'
        out += f'10.7cm radio flux: {color(info.f107, 'sfu')} sfu\n'
        out += f'X-ray flux: {color(info.flux, 'flux')} '
        out += f'(2h max: {color(info.flux_2h_max, 'flux')}, 24h max: {color(info.flux_24h_max, 'flux')})\n'
        out += f'Flares in past 24 hours: {color(info.c_flares, 'c_flare_count')} c-class, '
        out += f'{color(info.m_flares, 'm_flare_count')} m-class, and {color(info.x_flares, 'x_flare_count')} x-class\n'
        out += f'Solar cycle {info.cycle}, Carrington rotation {info.rotation}\n'
        out += f'Solar wind speed: {info.wind_speed} km/s\n'
        out += f'Solar wind density: {info.wind_density} p/cm^3\n'
    # if flags & REGIONS:
    #     out += 'Active regions:\n'
    #     out += 'region location spots area class_mag C  M  X  C% M% X%\n'
    #     for region in info.regions:
    #         out += f'{str(region.id).ljust(6)} {region.latitude} {region.longitude}'
    return out.rstrip('\n')

def format_mdd_table(data: MultiDayData, flags: int) -> str:
    out = '\x1b[96mdate       '
    if flags & EARTH:
        out += 'kp -  +  R-+ S-+ G-+ '
        if flags & AP:
            out += 'ap  -   +   '
        if flags & HOUR:
            out += '00 03 06 09 12 15 18 21 '.replace(' ', (' ap  ' if flags & AP else ' '))
    if flags & SUN:
        out += 'sn area    f10.7 +ars bgflux mxflux C  M  X  '
        if flags & FLARES:
            out += 'flares '
        if flags & REGIONS:
            out += 'regions '
    out += '\x1b[0m\n'
    for day, info in data.items():
        avg_kp = util.average_kp(*info.kps)
        out += f'{color(avg_kp, 'kp', display=False)}{day.strftime('%Y-%m-%d'):<10} '
        if flags & EARTH:
            kps = util.sort_kps(*info.kps)
            min_kp, max_kp = kps[0], kps[-1]
            out += f'{color(avg_kp, 'kp', 2)} {color(min_kp, 'kp', 2)} {color(max_kp, 'kp', 2)} '
            out += f'9{color(util.flux_to_r(info.bg_flux), 'rsg', 1)}'
            out += f'{color(util.flux_to_r(info.max_flux), 'rsg', 1)} '
            # out += f'{color(util.pfu_to_s(info.flux_p_10mev), 'rsg', 1)}99 '
            out += '999 '
            out += f'{color(util.kp_to_g(avg_kp), 'rsg', 1)}'
            out += f'{color(util.kp_to_g(min_kp), 'rsg', 1)}'
            out += f'{color(util.kp_to_g(max_kp), 'rsg', 1)} '
            if flags & AP:
                aps = [0 if ap is None else ap for ap in info.aps]
                ap, min_ap, max_ap = round(sum(aps)/len(info.aps)), min(aps), max(aps)
                out += f'{color(ap, 'ap', 3)}{color(min_ap, 'ap', 3)}{color(max_ap, 'ap', 3)}'
            if flags & HOUR:
                if flags & AP:
                    for h_kp, h_ap in zip(info.kps, info.aps):
                        out += f'{color(h_kp, 'kp', 2)} {h_ap:<3} '
                else:
                    for h_kp in info.kps:
                        out += f'{color(h_kp, 'kp', 2)} '
        if flags & SUN:
            out += f'{color(info.sunspots, 'sunspots', 5)} {color(info.spot_area, 'spot_area', 7)} '
            out += f'{color(info.f107, 'sfu', 5)} {color(info.new_regions, 'new_regions', 4)} '
            out += f'{color(info.bg_flux, 'flux', 6)} {color(info.max_flux, 'flux', 6)} '
            out += f'{color(info.c_flares, 'c_flare_count', 2)} '
            out += f'{color(info.m_flares, 'm_flare_count', 2)} '
            out += f'{color(info.x_flares, 'x_flare_count', 2)} '
            if flags & FLARES:
                pass
            if flags & REGIONS:
                pass
    return out + '\n'

def format_day_data_text(info: DayData, flags: int, include_time: bool = True) -> str:
    if include_time:
        out = f'space weather conditions at {info.day.strftime('%Y-%m-%d %H:%M:%S')}:\n'
    else:
        out = f'space weather conditions on {info.day.strftime('%Y-%m-%d')}:\n'
    out += f'{color(info.r_avg, 'rsg', before='R')} '
    out += f'{color(info.s_avg, 'rsg', before='S')} '
    out += f'{color(info.g_avg, 'rsg', before='G')} '
    out += f'(min: {color(info.r_min, 'rsg', before='R')} '
    out += f'{color(info.s_min, 'rsg', before='S')} '
    out += f'{color(info.g_min, 'rsg', before='G')}, '
    out += f'max: {color(info.r_max, 'rsg', before='R')} '
    out += f'{color(info.s_max, 'rsg', before='S')} '
    out += f'{color(info.g_max, 'rsg', before='G')})\n'
    if flags & EARTH:
        out += '   00  03  06  09  12  15  18  21\n'
        out += f'kp {' '.join([str(kp).ljust(3) for kp in info.kps])}\n'
        if flags & AP:
            out += f'ap {' '.join([str(ap).ljust(3) for ap in info.aps])}\n'
        out += f'bt: {info.bt}, bz: {info.bz}, dst: {info.dst}\n'
    if flags & SUN:
        out += f'{color(info.sunspots, 'sunspots')} sunspots'
        out += f' ({color(info.spot_area, 'spot_area')}%)\n'
        out += f'10.7cm radio flux: {color(info.f107, 'sfu')} sfu\n'
        out += f'background flux: {color(info.bg_flux, 'flux')}, max flux: {color(info.max_flux, 'flux')}\n'
        out += f'flares: {color(info.c_flares, 'c_flare_count')} c-class, '
        out += f'{color(info.m_flares, 'm_flare_count')} m-class, and {color(info.x_flares, 'x_flare_count')} x-class\n'
        out += f'solar cycle {info.cycle}, carrington rotation {info.rotation}\n'
        out += f'solar wind: speed: {info.wind_speed} km/s, density: {info.wind_density} p/cm^3'
    return out


def parse_date_arg(arg: str) -> date | None:
    #try:
    return dateutil.parser.parse(arg).date() # type: ignore
    #except ValueError:
    #    return None

def parse_mode(arg: str) -> int | None:
    try:
        return int(arg)
    except ValueError:
        if arg in MODE_FLAG_MAP:
            return MODE_FLAG_MAP[arg]
        else:
            arg_re = re.compile(re.escape(arg))
            for k, v in MODE_FLAG_MAP.items():
                if arg_re.search(k):
                    return v
            return None

def parse(args: Sequence[str] = sys.argv) -> argparse.Namespace | None:
    parser = argparse.ArgumentParser(
        prog='spacew',
        description='outputs space weather information for date(s)',
    )
    parser.add_argument('command', action='store', nargs='?', type=str, default='current', \
                        help='the command to run (current|now|archive|history|on|bot)')
    parser.add_argument('start_date', nargs='?', action='store', type=str, default='', \
                        help='the date to get data for (default is today)')
    parser.add_argument('end_date', nargs='?', action='store', type=str, default='', \
                        help='the end date for a date range, when provided it gives all dates between date and this')
    parser.add_argument('mode', nargs='?', action='store', type=parse_mode, default='default', \
                        help='the data to output (default|sun|earth|all|flags)')
    parser.add_argument('-m', '--mode', action='store', dest='mode', type=parse_mode, default='defualt', \
                        help='the data to output (default|sun|earth|all|flags)')
    parser.add_argument('-v', '--version', action='version', version=VERSION, help='print the version')
    parser.add_argument('-j', '--json', action='store_true', help='output json')
    parser.add_argument('-n', '--nocolor', '--no-color', action='store_true', help='disable color output')
    parser.add_argument('-r', '--refresh', action='store_true', help='force data refresh instead of loading from cache')
    parser.add_argument('-c', '--cache', action='store_false', help='disable auto saving to cache')
    parser.add_argument('-a', '-p', '-ap', '--ap', action='store_true', help='whether to output ap')
    out = parser.parse_args(args)
    arg1, arg2, arg3 = out.command, out.start_date, out.end_date
    if arg1 not in COMMANDS:
        temp = parse_date_arg(arg1)
        if temp is not None:
            out.start_date = temp
            out.command = 'archive'
        else:
            temp = parse_mode(arg1)
            if temp:
                out.mode = temp
                out.command = 'current'
            else:
                parser.print_usage()
                print(f'spacew: error: argument 1: not a command, date, or mode: {arg1!r}')
                return None
    if arg2 != '':
        temp = parse_date_arg(arg2)
        if temp is not None:
            out.start_date = temp
        else:
            temp = parse_mode(arg2)
            if temp is not None:
                out.mode = temp
            else:
                parser.print_usage()
                print(f'spacew: error: argument 2: not a date or mode: {arg2!r}')
                return None
    if arg3 != '':
        temp = parse_date_arg(arg3)
        if temp is not None:
            out.end_date = temp
        else:
            temp = parse_mode(arg3)
            if temp is not None:
                out.end_date = out.start_date
                out.mode = temp
            else:
                parser.print_usage()
                print(f'spacew: error: argument 3: not a date or mode: {arg3!r}')
                return None
    else:
        out.end_date = out.start_date
    return out

def main(argv: Sequence[str] = sys.argv, path: str = '.', secure: bool = False, discord_ansi: bool = False) -> str | None:
    args = parse(argv)
    if args is None:
        return None
    cmd = args.command
    flags = args.mode | (AP if args.ap else 0)
    if cmd in ARCHIVE_CMDS:
        start, end = args.start_date, args.end_date
        if end is None:
            end = start
        end += timedelta(days=1)
        flags = args.mode | (AP if args.ap else 0)
        data = get_past_data(start, end, args.refresh, args.cache)
        if args.json:
            out = {key: asdict(value) for key, value in data.items()}
        elif len(data) == 1:
            out = format_day_data_text(data[next(iter(data))], flags, include_time=False)
        else:
            out = format_mdd_table(data, flags)
    elif cmd in CURRENT_CMDS:
        info = get_current_data()
        out = asdict(info) if args.json else format_current_data_text(info, flags)
    elif cmd in DISCORD_CMDS:
        if not secure:
            os.chdir(path)
            if os.name == 'nt':
                os.system('py -u discord_bot_main.py')
            else:
                os.system('python3 -u discord_bot_main.py')
        return ''
    if args.json or not isinstance(out, str):
        return pprint.pformat(json.loads(json.dumps({
            'version': VERSION,
            'args': vars(args),
            'data': out,
        })), sort_dicts=False)
    else:
        if args.nocolor:
            out = re.sub(r'\x1b(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', out)
        if discord_ansi:
            out = re.sub(r'\x1b\[9(\d)m', '\x1b[3\\1m', out)
        return out


def main_sys_argv() -> None:
    argv = sys.argv
    while not argv[0].endswith('cli.py'):
        argv = argv[1:]
    path = '/'.join((argv[0].split('/'))[:-1]) + '/'
    argv = argv[1:]
    out = main(argv, path)
    if out is not None:
        print(out)


if __name__ == '__main__':
    main_sys_argv()
