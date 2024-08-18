
'''spacew - space weather library, CLI, and Discord bot
todo: write this'''

from datetime import date, timedelta
import pickle
import os
from .datatypes import RSG, Flux, Kp, Ap, Region, Flare, DayData, CurrentData, MultiDayData
from .past_data import get as _get_past_data
from .current_data import get as get_current_data

__all__ = ['RSG', 'Flux', 'Kp', 'Ap', 'Region', 'Flare', 'DayData', 'CurrentData', 'MultiDayData', \
           'get_cache', 'set_cache', 'get_past_data', 'get_current_data']


CACHE_PATH = os.path.expanduser('~/.spacew_cache')


def get_cache() -> MultiDayData:
    if not os.path.exists(CACHE_PATH):
        with open(CACHE_PATH, 'wb') as file:
            pickle.dump({}, file)
        return {}
    else:
        with open(CACHE_PATH, 'rb') as file:
            return pickle.load(file)

def set_cache(cache: MultiDayData) -> None:
    with open(CACHE_PATH, 'wb') as file:
        pickle.dump(cache, file)


def get_past_data(start: date, end: date | None = None, use_cache: bool = True, \
                  add_to_cache: bool = True) -> MultiDayData:
    if end is None:
        end = start + timedelta(days=1)
    cache = get_cache() if use_cache else {}
    data: MultiDayData = {}
    no_cache: list[date] = []
    day = start
    while day < end:
        if day in cache:
            data[day] = cache[day]
        else:
            no_cache.append(day)
        day += timedelta(days=1)
    already_done_years = []
    for day in no_cache:
        if day not in already_done_years:
            data |= _get_past_data(date(day.year, 1, 1), date(day.year + 1, 1, 1))
    if add_to_cache:
        set_cache(get_cache() | data)
    return data
