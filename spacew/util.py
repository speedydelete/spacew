

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
