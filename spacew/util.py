

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
    '9-': 300, '9': 400,
}

def gfz_kp_to_real_kp(kp):
    kp = float(kp)
    out = str(round(kp))
    if kp > int(kp):
        out += '+'
    elif kp < int(kp):
        out += '-'
    return out

_AP_TO_KP_MAP = {v: k for k, v in KP_TO_AP_MAP.items()}

def ap_to_kp(ap: int) -> str:
    if ap < 2:
        return '0'
    else:
        for k, v in _AP_TO_KP_MAP.items():
            if ap <= k:
                return v
        return '10'

LT = 1
EQ = 2
GT = 4
LE = LT & EQ
NE = LT & GT
GE = GT & EQ

def compare_kp(a, b, op):
    diff = int(b[0]) - int(a[0])
    if diff < 0:
        return op & GT
    elif diff > 0:
        return op & LT
    else:
        if len(a) == 1:
            return op & (EQ if len(b) == 1 else (LT if b[1] == '-' else GT))
        elif a[1] == '-':
            return op & (EQ if len(b) == 2 and b[1] == '-' else GT)
        else:
            return op & (EQ if len(b) == 2 and b[1] == '+' else LT)

def average_kp(*kps: str) -> str:
    avg = 0
    for kp in kps:
        avg += int(kp[0])*3
        if kp.endswith('-'):
            avg -= 1
        elif kp.endswith('+'):
            avg += 1
    kp = avg / len(kps)
    return gfz_kp_to_real_kp(avg / len(kps) / 3)

def sort_kps(*args: str) -> list[str]: # insertion sort
    kps = list(args)
    if len(kps) <= 1:
        return kps
    for i in range(1, len(kps)):
        j = i
        while j >= 0 and compare_kp(kps[j - 1], kps[j], GT):
            kps[j - 1], kps[j] = kps[j], kps[j - 1]
            j -= 1
    return kps

KP_TO_G = {
    '0': 0, '0+': 0,
    '1-': 0, '1': 0, '1+': 0,
    '2-': 0, '2': 0, '2+': 0,
    '3-': 0, '3': 0, '3+': 0,
    '4-': 0, '4': 0, '4+': 0,
    '5-': 1, '5': 1, '5+': 1,
    '6-': 2, '6': 2, '6+': 2,
    '7-': 3, '7': 3, '7+': 3,
    '8-': 4, '8': 4, '8+': 4,
    '9-': 5, '9': 5, '9+': 5,
}


def flux_to_r(flare):
    let = flare[0]
    num = float(flare[1:])
    if let == 'X' and num >= 20:
        return 5
    elif let == 'X' and num >= 10:
        return 4
    elif let == 'X' and num >= 1:
        return 3
    elif let == 'M' and num >= 5:
        return 2
    elif let == 'M' and num >= 1:
        return 1
    else:
        return 0


def pfu_to_s(pfu):
    if pfu >= 100000:
        return 5
    elif pfu >= 10000:
        return 4
    elif pfu >= 1000:
        return 3
    elif pfu >= 100:
        return 2
    elif pfu >= 10:
        return 1
    else:
        return 0
