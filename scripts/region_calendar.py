"""Active-region calendar: an operations tool built on our rotation law (Steps 1-3).

From one look at an active region (its latitude and its distance from the central meridian on a given day) it
predicts when the region enters the 'danger zone' E30-W90 (85% of proton events start there, see protons.py),
when it faces Earth, when it rotates off the visible disk and when it comes back. Rate seen from Earth =
ω(latitude) from rotation.py minus Earth's orbital motion on that date.

    python3 region_calendar.py                      check with the region of the May 2024 G5 storm
    python3 region_calendar.py 2035-06-01 -15 -60   region at 15°S, 60° east of the central meridian on 1 June 2035

Check: NOAA 13664, which caused the May 2024 G5 storm, predicted from its first day on the disk and compared with
its observed positions, including its return a month later as NOAA 13697 (the same Carrington longitude).
"""
import sys, numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from paths import D, F
from solar_geometry import julian_day, earth_orbital_rate

A, B = pd.read_csv(D + "rotation_fit.csv").iloc[0]
MARKS = [("enters the danger zone (E30)", -30), ("faces Earth (central meridian)", 0),
         ("rotates off the disk (W90)", 90), ("back at the east limb (E90)", 270)]


def rate_seen_from_earth(lat, t):
    """°/day: our sidereal rotation law minus Earth's orbital motion on date t."""
    return A + B * np.sin(np.radians(lat)) ** 2 - float(earth_orbital_rate(julian_day(np.datetime64(pd.Timestamp(t)))))


def calendar(t, lat, cmd, rotations=2):
    """Dates when a region seen at central-meridian distance cmd (degrees, east negative) on day t reaches each mark."""
    w = rate_seen_from_earth(lat, t)
    out = []
    for r in range(rotations):
        for name, target in MARKS:
            days = (target + 360 * r - cmd) / w
            if days >= 0:
                out.append((pd.Timestamp(t) + pd.Timedelta(days=days), name, r))
    return w, out


if len(sys.argv) == 4:
    t, lat, cmd = pd.Timestamp(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3])
    w, cal = calendar(t, lat, cmd)
    print(f"Region at latitude {lat:+.0f}°, {abs(cmd):.0f}° {'east' if cmd < 0 else 'west'} of the central meridian on {t:%d %b %Y}:")
    print(f"turns {w:.2f}° per day as seen from Earth (one turn in {360 / w:.1f} days)")
    for d, name, r in cal:
        print(f"   {d:%a %d %b %Y %H:%M}  {name}" + ("  [next rotation]" if r else ""))
    sys.exit()

# ---------- check: the region of the May 2024 G5 storm ----------
from sunspot_groups import load_groups
from kp_index import load_kp

g = load_groups(2024, 2024)
r1, r2 = g[g.gid == "13664"].sort_values("time"), g[g.gid == "13697"].sort_values("time")
first = r1.iloc[0]
w, cal = calendar(first.time, first.lat, first.cmd)
print(f"NOAA 13664 first seen {first.time:%d %b %Y} at latitude {first.lat:+.0f}°, {abs(first.cmd):.0f}° east of the "
      f"central meridian (Carrington longitude {first.lcar:.0f}°)")
print(f"Our rotation law at that latitude: {w:.2f}° per day seen from Earth, one turn in {360 / w:.1f} days")
print(f"NOAA 13697 first seen {r2.time.iloc[0]:%d %b %Y} at Carrington longitude {r2.lcar.iloc[0]:.0f}°, latitude "
      f"{r2.lat.iloc[0]:+.0f}°: the same region one rotation later")


def observed(track, target):
    """When a region's observed central-meridian distance reached `target` (straight line through its daily positions)."""
    d = (track.time - track.time.iloc[0]).dt.total_seconds() / 86400
    m, b = np.polyfit(d, track.cmd, 1)
    return track.time.iloc[0] + pd.Timedelta(days=(target - b) / m)


obs = {("enters the danger zone (E30)", 0): observed(r1, -30), ("faces Earth (central meridian)", 0): observed(r1, 0),
       ("rotates off the disk (W90)", 0): observed(r1, 90), ("back at the east limb (E90)", 0): observed(r2, -90),
       ("enters the danger zone (E30)", 1): observed(r2, -30), ("faces Earth (central meridian)", 1): observed(r2, 0),
       ("rotates off the disk (W90)", 1): observed(r2, 90)}
print(f"\nPredicted from the first day only ({first.time:%d %b}) vs observed:")
errs = []
for d, name, r in cal:
    if (name, r) in obs:
        o = obs[(name, r)]; e = (d - o).total_seconds() / 86400; errs.append(e)
        print(f"   {name:32s}{' (next turn)' if r else '            '}: predicted {d:%d %b %H:%M}, observed {o:%d %b %H:%M}"
              f"  ({e:+.1f} days, {(d - first.time).days} days ahead)")
print(f"   largest error {max(map(abs, errs)):.1f} days")

fl = pd.read_csv(D + "flares_1975_2026.csv", parse_dates=["time"])
xf = fl[(fl.flux >= 1e-4) & (fl.time >= "2024-05-01") & (fl.time < "2024-06-16")]
k = load_kp()
storm = k[(k.date >= "2024-05-01") & (k.date < "2024-06-16") & (k.kp >= 7.66)]
zone = [(d, name, r) for d, name, r in cal if "E30" in name or "W90" in name]
win = [(zone[i][0], zone[i + 1][0]) for i in range(0, len(zone) - 1, 2)]
inside = sum(((xf.time >= a - pd.Timedelta(days=1)) & (xf.time <= b + pd.Timedelta(days=1))).sum() for a, b in win)
print(f"\nPredicted danger windows: " + "; ".join(f"{a:%d %b}–{b:%d %b}" for a, b in win))
print(f"X-class flares 1 May-15 June 2024 (all regions): {len(xf)}, of which {inside} fell inside these windows (±1 day)")
print("Severe (G4+) storm days: " + ", ".join(f"{d:%d %b} (Kp {kp:.1f})" for d, kp in zip(storm.date, storm.kp)))
print("The CMEs behind the 10-11 May G5 storm left the Sun on 8-9 May (NOAA SWPC reports), inside the first window.")

# ---------- figure ----------
fig, ax = plt.subplots(figsize=(13, 5.5))
t0, t1 = pd.Timestamp("2024-04-30"), pd.Timestamp("2024-06-16")
ax.axhspan(-30, 90, color="tab:orange", alpha=0.12, zorder=0, label="danger zone E30–W90 (85% of proton events start here)")
for d in storm.date:
    ax.axvspan(d, d + pd.Timedelta(days=1), color="tab:purple", alpha=0.25, lw=0, zorder=0)
ax.plot([], [], color="tab:purple", alpha=0.4, lw=8, label="severe geomagnetic storm days (G4–G5)")
tt = pd.date_range(first.time, t1, freq="2h")
cmd_pred = (first.cmd + w * (tt - first.time).total_seconds() / 86400 + 180) % 360 - 180
ax.plot(tt, np.where(np.abs(cmd_pred) <= 90, cmd_pred, np.nan), c="k", lw=1.5, ls="--",
        label=f"our prediction from {first.time:%d %b} only ({w:.2f}°/day)")
ax.plot(r1.time, r1.cmd, "o", c="tab:orange", ms=7, label="NOAA 13664 observed")
ax.plot(r2.time, r2.cmd, "o", c="tab:red", ms=7, label="NOAA 13697 observed (same region, next turn)")
ax.plot(xf.time, np.full(len(xf), 97), "v", c="tab:red", ms=7, label="X-class flares (all regions)")
for d, name, r in cal:
    if d <= t1:
        ax.axvline(d, c="gray", lw=0.7, ls=":")
        ax.text(d, -97, name.split(" (")[0].replace("rotates off the disk", "off the disk").replace("back at the east limb", "returns")
                .replace("enters the danger zone", "enters danger zone"), rotation=90, fontsize=7.5, va="bottom", ha="right", color="dimgray")
ax.set_xlim(t0, t1); ax.set_ylim(-100, 102)
ax.set_ylabel("Degrees from the central meridian (east −, west +)")
ax.set_title("Our rotation law as a forecasting tool: the region behind the May 2024 G5 storm, predicted from its first day", fontsize=11)
ax.legend(fontsize=8, loc="center", bbox_to_anchor=(0.46, 0.42))
import matplotlib.dates as mdates
ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b %Y"))
plt.tight_layout(); plt.savefig(F + "region_calendar.png", dpi=150)
