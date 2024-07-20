
import os
import ftplib
from datetime import date
from database import Database, strlist, intlist, timelist


def create_db(name):
    db = Database(f'~/.spacew/{name}.sdb', {
        'spots': int,
        'f107': int,
        'new_regions': int,
        'bg_flux': str,
        'max_flux': str,
        'c_flares': int,
        'm_flares': int,
        'x_flares': int,
        'regions': intlist,
        'region_spots': intlist,
        'region_sizes': intlist,
        'region_mags': strlist,
        'region_zmcls': strlist,
        'region_locs': strlist,
        'kp': intlist,
        'ap': intlist,
        'noaa_kp': intlist,
        'flare_regions': intlist,
        'flares': intlist,
        'flare_starts': timelist,
        'flare_maxes': timelist,
        'flare_ends': timelist,
        'flux_p_1mev': intlist,
        'flux_p_10mev': intlist,
        'flux_p_50mev': intlist,
        'flux_p_100mev': intlist,
        'flux_e_08mev': intlist,
        'flux_e_2mev': intlist,
        'wind_speed': intlist,
        'wind_density': intlist,
        'imf_bt': intlist,
        'imf_bz': intlist,
    }, date)
    db.save()
t
def load_db(name):
    return Database(f'~/.spacew/{name}.sdb')

def init_dbs():
    if not os.path.exists('~/.spacew'):
        os.mkdir('~/.spacew')


def get_swpc_ftp_file(file: str, encoding='utf-8') -> str:
    '''retrieves a file using ftp from swpc'''
    fdir, file = os.path.split(file)
    ftp = ftplib.FTP('ftp.swpc.noaa.gov', encoding=encoding)
    ftp.login()
    ftp.cwd(fdir)
    out = []
    ftp.retrbinary(f'RETR {file}', out.append)
    return ''.join([x.decode(encoding) for x in out])


def load_txt_data(data: str, start: date, end: date, first: date | None, mul: int = 1) -> list[list[str]]:
    '''loads data in the .txt format used by api's'''
    lines = [line for line in data.split('\n') if len(line) > 0 and not line[0] in ('#', ':')]
    lines += [''] * mul
    if first is None:
        first = date.fromisoformat('-'.join(lines[0].split(' ')[:3]))
    info = lines[(start - first).days * mul:(end - first).days * mul]
    out = []
    for line in info:
        line = line.split(' ')
        line = [x for x in line if x != '']
        out.append(line)
    if out[-1] == []:
        out = out[:-mul]
    return out

