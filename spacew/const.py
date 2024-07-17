
import re
from datetime import date

class SpaceWError(Exception):
    pass

VERSION = '1.0'

EVEN_LESS = -2
LESS = -1
DEFAULT = 0
MORE = 1
EVEN_MORE = 2

ANSI_ESCAPE = re.compile(r'\x1b(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

GFZ_URL = 'https://www-app3.gfz-potsdam.de/kp_index/'
GFZ_FIRST_DATE = date(1932, 1, 1)
SWPC_FIRST_DATE = date(1996, 1, 1)

DAYS_IN_MONTH = (None, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)

KP_VALUE_MAP = {
    '0.000': '0', '0.333': '0+',
    '0.667': '1-', '1.000': '1', '1.333': '1+',
    '1.667': '2-', '2.000': '2', '2.333': '2+',
    '2.667': '3-', '3.000': '3', '3.333': '3+',
    '3.667': '4-', '4.000': '4', '4.333': '4+',
    '4.667': '5-', '5.000': '5', '5.333': '5+',
    '5.667': '6-', '6.000': '6', '6.333': '6+',
    '6.667': '7-', '7.000': '7', '7.333': '7+',
    '7.667': '8-', '8.000': '8', '8.333': '8+',
    '8.667': '9-', '9.000': '9', '9.333': '9+',
    '0.00': '0', '0.33': '0+',
    '0.67': '1-', '1.00': '1', '1.33': '1+',
    '1.67': '2-', '2.00': '2', '2.33': '2+',
    '2.67': '3-', '3.00': '3', '3.33': '3+',
    '3.67': '4-', '4.00': '4', '4.33': '4+',
    '4.67': '5-', '5.00': '5', '5.33': '5+',
    '5.67': '6-', '6.00': '6', '6.33': '6+',
    '6.67': '7-', '7.00': '7', '7.33': '7+',
    '7.67': '8-', '8.00': '8', '8.33': '8+',
    '8.67': '9-', '9.00': '9', '9.33': '9+',
}

KP_TO_INT_MAP = {
    '0': 0, '0+': 1,
    '1-': 2, '1': 3, '1+': 4,
    '2-': 5, '2': 6, '2+': 7,
    '3-': 8, '3': 9, '3+': 10,
    '4-': 11, '4': 12, '4+': 13,
    '5-': 14, '5': 15, '5+': 16,
    '6-': 17, '6': 18, '6+': 19,
    '7-': 20, '7': 21, '7+': 22,
    '8-': 23, '8': 24, '8+': 25,
    '9-': 26, '9': 27, '9+': 28,
}

INT_TO_KP_MAP = {value: key for key, value in KP_TO_INT_MAP.items()}

KP_TO_AP_MAP = {
    '0': 0, '0+': 2,
    '1-': 3, '1': 4, '1+': 5,
    '2-': 6, '2': 7, '2+': 9,
    '3-': 12, '3': 15, '3+': 18,
    '4-': 22, '4': 27, '4+': 32,
    '5-': 39, '5': 48, '5+': 56,
    '6-': 67, '6': 80, '6+': 94,
    '7-': 111, '7': 132, '7+': 154,
    '8-': 179, '8': 207, '8+': 236,
    '9-': 300, '9': 400, '9+': 500,
}

KP_COLOR_MAP = {
    '0': '39', '0+': '39',
    '1-': '39', '1': '39', '1+': '39',
    '2-': '32', '2': '92', '2+': '32',
    '3-': '32', '3': '92', '3+': '32',
    '4-': '92', '4': '92', '4+': '92',
    '5-': '92', '5': '92', '5+': '92',
    '6-': '93', '6': '93', '6+': '93',
    '7-': '93', '7': '93', '7+': '93',
    '8-': '91', '8': '91', '8+': '91',
    '9-': '91', '9': '91', '9+': '91',
}

FLUX_COLOR_MAP = {}
