
'''spacew - space weather library, CLI, and Discord bot
todo: write this'''

from datetime import date
from .datatypes import Region, Flare, DayData, CurrentData
from .old_data import get_day_data
from .current_data import get_current_data

__all__ = ['Region', 'Flare', 'DayData', 'CurrentData', 'get_data']


def get_data(start: date, end: date | None = None) -> dict[date, DayData]:
    pass
