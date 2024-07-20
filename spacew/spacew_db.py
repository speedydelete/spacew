
import os
import platform
from datetime import date
from database import Database, strlist, intlist, timelist


def create_db(name):
    db = Database(f'~/.spacew/{name}', {
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
        'wind_speed': intlist,
        'flux_p_1mev': intlist,
        'flux_p_10mev': intlist,
        'flux_p_50mev': intlist,
        'flux_p_100mev': intlist,
        'flux_e_08mev': intlist,
        'flux_e_2mev': intlist,
    }, date)
    db.save()


def init_db():
    if not os.path.exists('~/.spacew'):
        os.mkdir('~/.spacew')

