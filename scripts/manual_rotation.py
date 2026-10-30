"""Rotation rate from YOUR OWN measurements on solar images.

1. Open images of the Sun from several days (e.g. data/sdo/hmi_20141212.jpg ... hmi_20141218.jpg,
   or any image with solar north up from helioviewer.org or sdo.gsfc.nasa.gov).
2. On every image write down, in pixels (any image program shows the position under the mouse):
   the centre of the spot (x, y), the centre of the disk and the radius of the disk.
3. Put them in a CSV file with these columns and run:   python3 scripts/manual_rotation.py my_spots.csv
       spot, time_utc, x_px, y_px, disk_cx_px, disk_cy_px, disk_r_px
   Example: data/rotation/sdo_spot_positions.csv (positions measured automatically by track_sdo.py).
"""
import sys, numpy as np, pandas as pd
from solar_geometry import (YEAR_DAYS, julian_day, sun_ephemeris, earth_orbital_rate, pixel_to_helio,
                            simple_pixel_to_helio, fit_line, speed_km_s)

m = pd.read_csv(sys.argv[1] if len(sys.argv) > 1 else "/home/user/planethack/data/rotation/sdo_spot_positions.csv")
m["jd"] = julian_day(pd.to_datetime(m.time_utc).values)
B0, L0, _ = sun_ephemeris(m.jd.values)
args = (m.x_px, m.y_px, m.disk_cx_px, m.disk_cy_px, m.disk_r_px)
m["lat"], m["cmd"] = pixel_to_helio(*args, B0)              # full method (includes B0)
m["lat_simple"], m["cmd_simple"] = simple_pixel_to_helio(*args)  # school formulas
m["B0"] = B0
print("Each measurement -> latitude and longitude from the central meridian (CMD):")
print(m[["spot", "time_utc", "B0", "lat", "cmd", "lat_simple", "cmd_simple"]].round(2).to_string(index=False))

print("\nspot    lat   seen from Earth   true (sidereal)    period     speed     | simple formulas")
for spot, p in m.groupby("spot"):
    p = p[p.cmd.abs() <= 60]                                 # near the limb positions are unreliable
    if len(p) < 2:
        print(f"  {spot}: need at least 2 days with the spot within 60° of the disk centre"); continue
    t = p.jd - p.jd.min()
    w_syn, err, _ = fit_line(t, p.cmd)
    w_sid = w_syn + earth_orbital_rate(p.jd.mean())
    w_simple = fit_line(t, p.cmd_simple)[0] + 360 / YEAR_DAYS
    e = f" ± {err:.2f}" if len(p) > 2 else ""
    print(f"  {spot}   {p.lat.mean():+5.1f}°   {w_syn:6.2f}°/day     {w_sid:6.2f}{e} °/day   {360 / w_sid:5.2f} d"
          f"   {speed_km_s(w_sid, p.lat.mean()):4.2f} km/s  | {w_simple:6.2f} °/day, {360 / w_simple:5.2f} d")
