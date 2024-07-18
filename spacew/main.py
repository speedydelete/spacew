
import re
import argparse
import pprint
from datetime import date as ddate, timedelta
import dateutil
from const import *
import hro
import data

def cli(args):
    out = {}
    start = args.date
    end = args.end_date
    if end is None:
        end = start
    end += timedelta(days=1)
    for day in range((end - start).days):
        out[start + timedelta(days=day)] = Namespace()
    if start <= ddate.today() + timedelta(days=3):
        kp_ap = data.get_kp_ap_data(start, end, args.refresh)
        solar = data.get_solar_data(start, end, args.refresh)
        goes = data.get_goes_data(start, end, args.refresh)
        for key in out:
            out[key] += kp_ap[key] + solar[key] + goes[key]
    else:
        pass
    out = Namespace(
        version = VERSION,
        mode = args.mode | (AP if args.ap else 0),
        data = out
    )
    if args.json:
        out = pprint.pformat(out, sort_dicts=False)
    else:
        out = hro.main(out)
    if args.nocolor:
        out = ANSI_ESCAPE.sub('', out)
    return out

def mode(arg: str) -> int:
    try:
        return int(arg)
    except ValueError:
        if arg in TEXT_FLAG_MAP:
            return TEXT_FLAG_MAP[arg]
        else:
            o_arg = str(arg)
            arg = re.compile(arg)
            for k, v in TEXT_FLAG_MAP.items():
                if arg.search(k):
                    return v
            raise argparse.ArgumentTypeError(f'not a valid mode: {o_arg}') from None

def date(arg: str) -> ddate:
    try:
        return dateutil.parser.parse(arg).date()
    except ValueError:
        raise argparse.ArgumentTypeError(f'not a valid date: {arg}') from None

parser = argparse.ArgumentParser(
    prog='spacew',
    description='outputs space weather information for date(s)',
)
parser.add_argument('mode', nargs='?', action='store', type=mode, default='default', \
                    help='the data to output (flags|default|d|all|sun|earth)')
parser.add_argument('date', nargs='?', action='store', type=date, default=str(ddate.today()), \
                    help='the date to get data for (default is current date)')
parser.add_argument('end_date', nargs='?', action='store', type=date, help='the end date for a date range, ' + \
                    'when provided it gives all dates between date and this')
parser.add_argument('-v', '--version', action='version', version=VERSION, help='print the version')
parser.add_argument('-j', '--json', action='store_true', help='output json')
parser.add_argument('-c', '--nocolor', '--no-color', action='store_true', help='disable color output')
parser.add_argument('-r', '--refresh', action='store_true', help='force data refresh instead of loading from cache ' + \
                    '(done automatically if it has been more than an hour since data was cached)')
parser.add_argument('-a', '-p', '-ap', '--ap', action='store_true', help='whether to output ap')

try:
    print(cli(parser.parse_args()))
except SpaceWError as e:
    print(f'spacew: error: {e}')
