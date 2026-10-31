"""Read the daily geomagnetic and solar indices from GFZ Potsdam (data/Kp_ap_Ap_SN_F107_since_1932.txt):
eight 3-hour Kp and ap values per UT day, the daily Ap, the sunspot number and the F10.7 radio flux."""
import pandas as pd

from paths import D, assert_data

KP = [f"kp{i}" for i in range(1, 9)]
AP3 = [f"ap{i}" for i in range(1, 9)]


def load_kp():
    f = D + "Kp_ap_Ap_SN_F107_since_1932.txt"
    assert_data(f)
    cols = ["Y", "M", "D", "days", "days_m", "bsr", "db"] + KP + AP3 + ["Ap", "SN", "F107obs", "F107adj", "flag"]
    k = pd.read_csv(f, sep=r"\s+", comment="#", header=None, names=cols)
    k["date"] = pd.to_datetime(dict(year=k.Y, month=k.M, day=k.D))
    k["kp"] = k[KP].max(axis=1)          # highest 3-hour Kp of the day
    return k
