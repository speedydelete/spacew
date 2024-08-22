
'''spacew command line interface'''

from typing import Any, Callable, Sequence
from datetime import date as date, timedelta
import math
import re
import json
import sys
import os
import pprint
import argparse
import dateutil
from cache import get_past_data
from now import get as get_current_data
import util

VERSION = '1.0'

KP_COLOR = {
    '0': '39', '0+': '39',
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

C_FLARE_COLOR = ('39', '32', '92', '93', '31')
RSG_COLOR = {-1: '39', 0: '39', 1: '32', 2: '92', 3: '93', 4: '31', 5: '31'}

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
    'flux': lambda flux: RSG_COLOR[util.flux_to_r(flux)],
    'c_flare_count': lambda count: '31' if count > 4 else C_FLARE_COLOR[count],
    'm_flare_count': lambda count: ('31' if count > 1 else '92') if count > 0 else '39',
    'x_flare_count': lambda count: '31' if count > 0 else '39',
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


def archive(args: argparse.Namespace) -> dict | str:
    start, end = args.start_date, args.end_date
    if end is None:
        end = start
    end += timedelta(days=1)
    flags = args.mode | (AP if args.ap else 0)
    data = get_past_data(start, end, args.refresh, args.cache)
    if args.json:
        return data
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
        out += f'{color(avg_kp, 'kp', display=False)}{day.strftime('%x'):<10} '
        if flags & EARTH:
            kps = util.sort_kps(*info.kps)
            min_kp, max_kp = kps[0], kps[-1]
            out += f'{color(avg_kp, 'kp', 2)} {color(min_kp, 'kp', 2)} {color(max_kp, 'kp', 2)} '
            out += f'9{color(util.flux_to_r(info.bg_flux), 'rsg', 1)}'
            out += f'{color(util.flux_to_r(info.max_flux), 'rsg', 1)} '
            #out += f'{color(util.pfu_to_s(info.flux_p_10mev), 'rsg', 1)}99 '
            out += '999 '
            out += f'{color(util.kp_to_g(avg_kp), 'rsg', 1)}'
            out += f'{color(util.kp_to_g(min_kp), 'rsg', 1)}'
            out += f'{color(util.kp_to_g(max_kp), 'rsg', 1)} '
            if flags & AP:
                ap, min_ap, max_ap = round(sum(info.aps)/len(info.aps)), min(info.aps), max(info.aps)
                out += f'{color(ap, 'ap', 3)}{color(min_ap, 'ap', 3)}{color(max_ap, 'ap', 3)}'
            if flags & HOUR:
                if flags & AP:
                    for h_kp, h_ap in zip(info.kps, info.aps):
                        out += f'{color(h_kp, 'kp', 2)} {h_ap:<3} '
                else:
                    for h_kp in info.kps:
                        out += f'{color(h_kp, 'kp', 2)} '
        if flags & SUN:
            spot_area = f'{format(info.spot_area*100, f'<6.{math.ceil(-math.log(info.spot_area*100))}f').rstrip()}%'
            out += f'{color(info.sunspots, 'sunspots', 5)} {color(info.spot_area, 'spot_area', 7, actual=spot_area)} '
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

def current(args: argparse.Namespace) -> dict | str:
    from dataclasses import asdict
    info = get_current_data()
    if args.json:
        return asdict(info)
    out = f'space weather conditions at {info.dt.strftime('%Y-%m-%d %H:%M:%S')}:\n'
    out += f'{color(info.r, 'rsg', before='R')} '
    out += f'{color(info.s, 'rsg', before='S')} '
    out += f'{color(info.g, 'rsg', before='G')} '
    out += f'(24h maxes: {color(info.r_24h_max, 'rsg', before='R')} '
    out += f'{color(info.s_24h_max, 'rsg', before='S')} '
    out += f'{color(info.g_24h_max, 'rsg', before='G')})\n'
    flags = args.mode | (AP if args.ap else 0)
    if flags & EARTH:
        out += f'kp{color(info.kp, 'kp')} {f'(ap: {color(info.ap, 'ap')})' if flags & AP else ''}, '
        out += f'bt: {info.bt}, bz: {info.bz}, dst: {info.dst}\n'
    if flags & SUN:
        out += f'{color(info.sunspots, 'sunspots')} sunspots'
        out += f' ({color(info.spot_area, 'spot_area', actual=str(info.spot_area*100))}%)\n'
        out += f'10.7cm radio flux: {color(info.f107, 'sfu')} sfu\n'
        out += f'x-ray flux: {color(info.flux, 'flux')} '
        out += f'(2h max: {color(info.flux_2h_max, 'flux')}, 24h max: {color(info.flux_24h_max, 'flux')})\n'
        out += f'flares today: {color(info.c_flares, 'c_flare_count')} c-class, '
        out += f'{color(info.m_flares, 'm_flare_count')} m-class, and {color(info.x_flares, 'x_flare_count')} x-class\n'
        out += f'carrington rotation {info.rotation}\n'
        out += f'solar wind: speed: {info.wind_speed} km/s, density: {info.wind_density} p/cm^3'
    return out


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
    'sun': SUN | FLARES,
    'all': EARTH | HOUR | SUN | FLARES,
}

def mode(arg: str) -> int:
    try:
        return int(arg)
    except ValueError:
        if arg in MODE_FLAG_MAP:
            return MODE_FLAG_MAP[arg]
        else:
            o_arg = str(arg)
            arg_re = re.compile(arg)
            for k, v in MODE_FLAG_MAP.items():
                if arg_re.search(k):
                    return v
            raise argparse.ArgumentTypeError(f'not a valid mode: {o_arg}') from None

def date_arg(arg: str) -> date:
    try:
        return dateutil.parser.parse(arg).date() # type: ignore
    except ValueError:
        raise argparse.ArgumentTypeError(f'not a valid date: {arg}') from None

def command_or_date(arg: str) -> str | tuple[str, date]:
    if arg in COMMANDS:
        return arg
    else:
        try:
            return ('archive', date_arg(arg))
        except argparse.ArgumentTypeError:
            raise argparse.ArgumentTypeError(f'not a valid command or date: {arg}') from None


def parse(args: Sequence[str] = sys.argv) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog='spacew',
        description='outputs space weather information for date(s)',
    )
    parser.add_argument('command_or_date', action='store', nargs='?', type=command_or_date, default='now')
    parser.add_argument('start_date', nargs='?', action='store', type=date_arg, \
                        default=str(date.today()), help='the date to get data for (default is today)')
    parser.add_argument('end_date', nargs='?', action='store', type=date_arg, help='the end date for a date range, ' + \
                        'when provided it gives all dates between date and this')
    parser.add_argument('mode', nargs='?', action='store', type=mode, default='default', \
                        help='the data to output (default|sun|earth|all)')
    parser.add_argument('-m', '--mode', action='store', dest='mode', type=mode, default='default', \
                        help='the data to output (default|sun|earth|all)')
    parser.add_argument('-v', '--version', action='version', version=VERSION, help='print the version')
    parser.add_argument('-j', '--json', action='store_true', help='output json')
    parser.add_argument('-n', '--nocolor', '--no-color', action='store_true', help='disable color output')
    parser.add_argument('-r', '--refresh', action='store_true', help='force data refresh instead of loading from cache')
    parser.add_argument('-c', '--cache', action='store_false', help='disable auto saving to cache')
    parser.add_argument('-a', '-p', '-ap', '--ap', action='store_true', help='whether to output ap')
    return parser.parse_args(args)

def main(argv: Sequence[str] = sys.argv, path: str = '.', secure: bool = False) -> str:
    args = parse(argv)
    cmd = args.command_or_date
    if isinstance(cmd, tuple):
        args.cmd, args.start_date = cmd
        cmd = args.cmd
    if cmd in ARCHIVE_CMDS:
        out = archive(args)
    elif cmd in CURRENT_CMDS:
        out = current(args)
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
        return out


def main_sys_argv() -> None:
    argv = sys.argv
    while not argv[0].endswith('cli.py'):
        argv = argv[1:]
    path = '/'.join((argv[0].split('/'))[:-1]) + '/'
    argv = argv[1:]
    print(main(argv, path))


if __name__ == '__main__':
    main_sys_argv()
