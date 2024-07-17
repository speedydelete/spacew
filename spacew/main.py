
import argparse
import pprint
from datetime import date, timedelta
import dateutil
from const import *
import hro
import data

def cli(args):
    out = {}
    start = dateutil.parser.parse(args.date).date()
    if args.end_date is None:
        end = start
    else:
        end = dateutil.parser.parse(args.end_date).date()
    end += timedelta(days=1)
    for day in range((end - start).days):
        out[str(start + timedelta(days=day))] = {}
    if start <= date.today() + timedelta(days=3):
        kp_ap = data.get_kp_ap_data(start, end, args.refresh)
        solar = data.get_solar_data(start, end, args.refresh)
        for key in out:
            out[key].update(kp_ap[key] | solar[key])
    else:
        pass
    out = {
        'version': VERSION,
        'mode': args.more - args.less,
        'data': out,
    }
    if args.json:
        out = pprint.pformat(out, sort_dicts=False)
    else:
        out = hro.main(out)
    if args.nocolor:
        out = ANSI_ESCAPE.sub('', out)
    return out

parser = argparse.ArgumentParser(
    prog='spacew',
    description='outputs space weather information for date(s)',
)
parser.add_argument('date', action='store', help='the date to get data for')
parser.add_argument('end_date', nargs='?', action='store', help='the end date for a date range, ' + \
                    'when provided it gives all dates between date and this')
parser.add_argument('-v', '--version', action='version', version=VERSION, help='print the version')
parser.add_argument('-j', '--json', action='store_true', help='output json')
parser.add_argument('-c', '--nocolor', '--no-color', action='store_true', help='disable color output')
parser.add_argument('-m', '--more', action='count', default=0, help='output more data')
parser.add_argument('-l', '--less', action='count', default=0, help='output less data')
parser.add_argument('-r', '--refresh', action='store_true', help='force data refresh instead of loading from cache ' + \
                    '(done automatically if it has been more than an hour since data was cached)')

try:
    print(cli(parser.parse_args()))
except SpaceWError as e:
    print(f'spacew: error: {e}')
