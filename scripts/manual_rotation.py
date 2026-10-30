"""Rotation from sunspot positions read off solar images (by hand, or by track_sdo.py).

Input CSV columns: spot, time_utc (or jd), x_px, y_px, disk_cx_px, disk_cy_px, disk_r_px
Run:   python3 scripts/manual_rotation.py my_spots.csv [figure.png]

Two trigonometric methods on the same pixel positions:
  1. arcsin:   latitude = arcsin(Y), longitude = arcsin(X / cos latitude). Longitude grows in a
               straight line with time; the slope is the rotation rate seen from Earth.
  2. sine fit: a spot on a turning sphere moves across the image as x(t) = xc + R·cos(lat)·sin(2π(t-t0)/P).
               Fitting this curve to x(t) gives the period P seen from Earth; y(t) stays ~constant.
True (sidereal) rate = rate seen from Earth + Earth's orbital motion (0.9856 °/day on average).
"""
import sys, numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from paths import D, F
from solar_geometry import (YEAR_DAYS, R_SUN_KM, julian_day, sun_ephemeris, earth_orbital_rate,
                            pixel_to_helio, simple_pixel_to_helio, fit_line, fit_sine, speed_km_s)

MAX_CMD = 60     # positions closer than 30° to the limb are distorted; leave them out


def load(path):
    m = pd.read_csv(path, dtype={"spot": str})
    if "jd" not in m:
        m["jd"] = julian_day(pd.to_datetime(m.time_utc).values)
    m["B0"] = sun_ephemeris(m.jd.values)[0]
    px = (m.x_px, m.y_px, m.disk_cx_px, m.disk_cy_px, m.disk_r_px)
    m["lat"], m["cmd"] = pixel_to_helio(*px, m.B0)              # full method (with B0)
    m["lat_simple"], m["cmd_simple"] = simple_pixel_to_helio(*px)  # school formulas
    return m


def analyse(m):
    rows, fits = [], {}
    for spot, p in m.groupby("spot", sort=False):
        p = p[p.cmd.abs() <= MAX_CMD]
        if len(p) < 3:
            print(f"  {spot}: need at least 3 days within {MAX_CMD}° of the centre"); continue
        t = (p.jd - p.jd.min()).values
        lat = p.lat.mean()
        xc, R = p.disk_cx_px.mean(), p.disk_r_px.mean()
        A = R * np.cos(np.radians(lat))                          # radius of the spot's latitude circle
        w_arcsin = fit_line(t, p.cmd)[0]                           # method 1
        s_fix = fit_sine(t, p.x_px, xc, A_fixed=A)                 # method 2, amplitude from geometry
        s_free = fit_sine(t, p.x_px, xc, A_guess=A)                # method 2, amplitude also fitted
        earth = earth_orbital_rate(p.jd.mean())
        w_sid = 360 / s_fix["P"] + earth
        fits[spot] = dict(t0=p.jd.min(), fit=s_fix, xc=xc, R=R, A=A)
        rows.append(dict(spot=spot, lat=lat, n=len(p), y_mean=p.y_px.mean(), y_range=p.y_px.max() - p.y_px.min(),
                         P_syn_arcsin=360 / w_arcsin, P_syn_sine=s_fix["P"], P_syn_sine_err=s_fix["P_err"],
                         P_syn_free=s_free["P"], A_free=s_free["A"], A_geom=A, rms_px=s_fix["rms"],
                         omega_sid=w_sid, P_sid=360 / w_sid,
                         P_sid_simple=1 / (1 / s_fix["P"] + 1 / YEAR_DAYS),
                         v_px_day=2 * np.pi * A / s_fix["P"],
                         v_seen_km_s=2 * np.pi * A / s_fix["P"] * R_SUN_KM / R / 86400,
                         v_true_km_s=speed_km_s(w_sid, lat)))
    return pd.DataFrame(rows), fits


def report(m, res):
    print("Measurements (JD = Julian Date):")
    print(m[["spot", "time_utc", "jd", "x_px", "y_px", "disk_cx_px", "disk_cy_px", "disk_r_px", "lat", "cmd"]]
          .round({"lat": 2, "cmd": 2}).to_string(index=False, formatters={"jd": "{:.5f}".format}))
    print("\nPeriod seen from Earth (synodic) by both trigonometric methods, then the true (sidereal) rotation:")
    print(" spot   lat   days | arcsin+line | sine fit (A=R·cos lat) | sine fit (A free)  | sidereal: omega   period"
          "  | speed: across disk   true")
    for _, r in res.iterrows():
        print(f"  {r.spot:3s} {r.lat:+6.1f}  {r.n:3d} |  {r.P_syn_arcsin:6.2f} d   |  {r.P_syn_sine:6.2f} ± {r.P_syn_sine_err:.2f} d"
              f"        | {r.P_syn_free:6.2f} d (A={r.A_free:.0f} vs {r.A_geom:.0f}px) | {r.omega_sid:6.2f} °/d  {r.P_sid:5.2f} d"
              f" | {r.v_px_day:5.1f} px/d = {r.v_seen_km_s:.2f} km/s   {r.v_true_km_s:.2f} km/s")
    print(f"\n(simple formula 1/P_sid = 1/P_syn + 1/365.25 gives P_sid = "
          + ", ".join(f"{r.spot}: {r.P_sid_simple:.2f} d" for _, r in res.iterrows()) + ")")
    print("y stays almost constant: " + ", ".join(f"{r.spot}: range {r.y_range:.0f} px" for _, r in res.iterrows())
          + "  (small drift: the Sun's axis tilt B0 and the spot's own motion)")


def plot(m, res, fits, out):
    jd0 = 2457000
    cols = plt.cm.tab10(np.arange(len(res)))
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(12, 9), sharex=True, gridspec_kw=dict(height_ratios=[3, 1.4]))
    tmin, tmax = m.jd.min() - jd0, m.jd.max() - jd0
    for (_, r), c in zip(res.iterrows(), cols):
        p = m[m.spot == r.spot]; f = fits[r.spot]
        T = f["fit"]["P"]; tc = f["fit"]["t0"] + f["t0"] - jd0       # time the spot crossed the centre line
        tt = np.linspace(tc - 0.75 * T, tc + 0.75 * T, 600)
        x = f["fit"]["curve"](tt - (f["t0"] - jd0))
        front = np.cos(2 * np.pi * (tt - tc) / T) > 0                  # only the front half is visible
        a1.plot(tt, np.where(front, x, np.nan), c=c, lw=1.8,
                label=f"Spot {r.spot} (lat {r.lat:+.0f}°): x = {f['xc']:.0f} + {f['A']:.0f}·sin(2π(t − t₀)/{T:.2f})")
        a1.plot(tt, np.where(front, np.nan, x), c=c, lw=1, ls=":")
        a1.plot(p.jd - jd0, p.x_px, "o", c=c, mec="k", ms=7, zorder=3)
        a2.plot(p.jd - jd0, p.y_px, "o-", c=c, mec="k", ms=6)
    xc, R = m.disk_cx_px.mean(), m.disk_r_px.mean()
    for v, lab in [(xc - R, "east limb (left edge)"), (xc, "disk centre"), (xc + R, "west limb (right edge)")]:
        a1.axhline(v, c="0.6", ls="--", lw=0.8); a1.text(tmin - 14, v + 15, lab, fontsize=8, color="0.4")
    a1.set_ylabel("x pixel position"); a1.legend(fontsize=8, loc="lower right")
    a1.set_title("x(t) follows a sine wave (solid: spot on the side facing us, dotted: behind the Sun) — dots are the measurements")
    a1.set_xlim(tmin - 15, tmax + 15)
    a2.set_ylabel("y pixel position"); a2.invert_yaxis()
    a2.set_xlabel(f"Julian Date − {jd0}")
    a2.set_title("y(t) stays almost constant: the spot keeps its latitude")
    plt.tight_layout(); plt.savefig(out, dpi=140)


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else D + "rotation/sdo_spot_positions.csv"
    out = sys.argv[2] if len(sys.argv) > 2 else F + "xy_sine_fit_all.png"
    m = load(path)
    res, fits = analyse(m)
    report(m, res)
    plot(m, res, fits, out)
