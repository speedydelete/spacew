
import ppigrf
from datetime import datetime


lon = 5.32415
lat = 60.39299
h   = 0
date = datetime(2021, 3, 28)

Be, Bn, Bu = ppigrf.igrf(lon, lat, h, date)

print(Be, Bn, Bu)
