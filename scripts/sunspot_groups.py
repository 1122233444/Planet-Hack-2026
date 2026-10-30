"""Read the daily sunspot-group positions (D. Hathaway's compilation of Greenwich 1874-1976 and
USAF/NOAA 1977-present data, files data/groups/gYYYY.txt)."""
import glob, numpy as np, pandas as pd

from paths import D


def load_groups(first_year=1874, last_year=2100):
    rec = []
    for f in sorted(glob.glob(D + "groups/g*.txt")):
        if not first_year <= int(f[-8:-4]) <= last_year: continue
        for line in open(f):
            tok = line.split()
            if len(tok) < 11: continue
            try:
                yr, mo, dy = int(line[0:4]), int(line[4:6]), float(line[6:12])
                dist, pa, lcar, lat, cmd = map(float, tok[-5:]); area = float(tok[-6])
            except ValueError:
                continue
            if dist == 0 and lcar == 0 and lat == 0 and cmd == 0: continue    # "missing day" rows
            rec.append((yr, mo, dy, line[12:].split()[0], area, lcar, lat, cmd))
    g = pd.DataFrame(rec, columns=["yr", "mo", "dy", "gid", "area", "lcar", "lat", "cmd"])
    g["time"] = pd.to_datetime(dict(year=g.yr, month=g.mo, day=1)) + pd.to_timedelta(g.dy - 1, unit="D")
    g["era"] = np.where(g.yr <= 1976, "Greenwich 1874-1976", "USAF/NOAA 1977-2026")
    return g
