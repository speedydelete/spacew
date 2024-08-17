
from typing import Any
from datetime import date, time, timedelta
import os
from database import Database, strlist, intlist, timelist
from get_data import get_kp_ap_data


def create_db(name):
    db = Database(os.path.expanduser(f'~/.spacew/{name}.sdb'), {
        'time': time,
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
        'kp': strlist,
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
    return db

def load_db(name: Any) -> Database:
    return Database(os.path.expanduser(f'~/.spacew/{name}.sdb'))

def init_dbs() -> None:
    path = os.path.expanduser('~/.spacew')
    if not os.path.exists(path):
        os.mkdir(path)


def add_kp_ap(year: int, db: Database) -> Database:
    data = get_kp_ap_data(date(year, 1, 1), date(year + 1, 1, 1))
    for row in db:
        row.kp, row.ap = data[row.name]
        row.save()
    return db


def make_db_for_year(year):
    db = create_db(year)
    day = date(year, 1, 1)
    end = date(year + 1, 1, 1)
    while day < end:
        db.add_row(day)
        day += timedelta(days=1)
    db = add_kp_ap(year, db)
    db.save()


if __name__ == '__main__':
    #init_dbs()
    #make_db_for_year(2003)
    db = load_db(2003)
    print(db[date(2003, 10, 30)].kp)
