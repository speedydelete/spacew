
from datetime import date
from old_data import Region, Flare, DayData, get_day_data
from current_data import CurrentData, get_current_data

__all__ = ['Region', 'Flare', 'DayData', 'CurrentData', 'get_data']

def get_data(start: date, end: date | None = None) -> DayData:
    pass
