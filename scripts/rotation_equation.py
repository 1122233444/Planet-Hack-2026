"""Deriving the equation for rotation speed vs latitude, step by step.

Plotted against s = sin²(latitude), the rotation rate falls on a straight line, so the
equation is  omega = A + B·sin²(lat)  and A, B are just the intercept and slope of a
straight-line (least-squares) fit - school-level linear regression.
"""
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from solar_geometry import R_SUN_KM
import manual_rotation as mr

from paths import D, F
r = pd.read_csv(D + "rotation_groups.csv")
A, B = pd.read_csv(D + "rotation_fit.csv").iloc[0]

# 1. median rotation rate in 2.5° latitude bands (both hemispheres together)
r["band"] = pd.cut(r.lat.abs(), np.arange(0, 42.5, 2.5))
b = r.groupby("band", observed=True).agg(lat=("lat", lambda x: x.abs().mean()), w=("omega", "median"),
                                         sd=("omega", "std"), n=("omega", "size"))
b = b[b.n >= 20]
b["s"] = np.sin(np.radians(b.lat)) ** 2
b["se"] = 1.253 * b.sd / np.sqrt(b.n)

# 2. straight line through the band medians:  slope = Σ(s-s̄)(w-w̄) / Σ(s-s̄)²,  intercept = w̄ - slope·s̄
wt = 1 / b.se**2
sb, wb = np.average(b.s, weights=wt), np.average(b.w, weights=wt)
slope = np.sum(wt * (b.s - sb) * (b.w - wb)) / np.sum(wt * (b.s - sb) ** 2)
icpt = wb - slope * sb
print(f"Straight line through {len(b)} band medians: omega = {icpt:.3f} {slope:+.3f}·sin²(lat)")
print(f"Fit to all {len(r):,} single groups (rotation.py):  omega = {A:.3f} {B:+.3f}·sin²(lat)")

# 3. from angular rate to period and speed
k = np.pi / 180 / 86400 * R_SUN_KM          # (deg/day) -> km/s at the equator
v0 = A * k
print("\nThe equations:")
print(f"   angular rate   omega(lat) = {A:.2f} − {-B:.2f}·sin²(lat)   [degrees per day, sidereal]")
print(f"   period         P(lat)     = 360 / omega(lat)            [days]")
print(f"   speed          v(lat)     = omega · (π/180) / 86400 · R☉ · cos(lat)")
print(f"                             = {v0:.3f} · cos(lat) · (1 − {-B / A:.3f}·sin²(lat))   [km/s]")
for lat in [0, 15, 30]:
    w = A + B * np.sin(np.radians(lat)) ** 2
    print(f"   check at {lat:2d}°: omega {w:.2f} °/day, P {360 / w:.2f} d, v {w * k * np.cos(np.radians(lat)):.2f} km/s")

# 4. our own spots on the same plot
sdo = pd.read_csv(D + "rotation/sdo_spot_results.csv")
mm = mr.load(D + "rotation/manual_walkthrough.csv"); wk, _ = mr.analyse(mm)
fig, ax = plt.subplots(figsize=(10, 6))
ax.errorbar(b.s, b.w, yerr=b.se, fmt="o", c="tab:red", ms=6, capsize=3,
            label=f"150 years: median of each 2.5° band ({len(r):,} groups)")
s = np.linspace(0, 0.45, 50)
ax.plot(s, icpt + slope * s, c="tab:red", lw=2, label=f"straight line through the red points: ω = {icpt:.2f} − {-slope:.2f}·sin²(lat)")
ax.plot(s, A + B * s, c="tab:red", lw=1.2, ls="--",
        label=f"fit to every single group: ω = {A:.2f} − {-B:.2f}·sin²(lat) (mean, not median)")
ax.scatter(np.sin(np.radians(sdo.lat)) ** 2, sdo.omega, c="tab:blue", s=40, zorder=3,
           label="our 9 SDO spots (automatic, Dec 2014)")
ax.scatter(np.sin(np.radians(wk.lat)) ** 2, wk.omega_sid, marker="*", c="gold", edgecolor="k", s=260, zorder=4,
           label="spots A and E, measured step by step")
for _, q in wk.iterrows():
    ax.annotate(f"{q.spot} ({q.lat:+.0f}°)", (np.sin(np.radians(q.lat)) ** 2, q.omega_sid), xytext=(8, 6),
                textcoords="offset points", fontsize=10)
top = ax.secondary_xaxis("top", functions=(lambda x: np.degrees(np.arcsin(np.sqrt(np.clip(x, 0, 1)))),
                                           lambda d: np.sin(np.radians(d)) ** 2))
top.set_xticks([0, 10, 15, 20, 25, 30, 35, 40]); top.set_xlabel("latitude (°)")
ax.set_xlim(0, 0.45); ax.set_ylim(13.2, 15.4)
ax.set_xlabel("sin²(latitude)"); ax.set_ylabel("sidereal rotation rate ω (°/day)")
ax.set_title("Against sin²(latitude) the points lie on a straight line:\nintercept = equator rate A, slope = B",
             fontsize=11)
ax.legend(fontsize=9, loc="upper right")
plt.tight_layout(); plt.savefig(F + "rotation_equation.png", dpi=150)
