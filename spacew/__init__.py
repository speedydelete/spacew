
'''spacew - space weather library, CLI, and Discord bot
todo: write this'''

from datetime import date
from .datatypes import Region, Flare, DayData, CurrentData
from .past_data import get as _get_past_data
from .current_data import get as get_current_data

__all__ = ['Region', 'Flare', 'DayData', 'CurrentData', 'get_past_data', 'get_current_data']

def get_past_data(start: date, end: date | None = None, use_cache: bool = True, \
             add_to_cache: bool = True) -> dict[date, DayData]:
    return _get_past_data(start, end)
