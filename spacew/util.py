

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
