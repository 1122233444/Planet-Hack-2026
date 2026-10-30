"""Steps 1-2 (large sample): differential rotation from 150 years of tracked sunspot groups.

For every passage of a sunspot group across the disk we fit its longitude against time.
The slope is how fast that group rotates; collecting thousands of groups at different
latitudes gives rotation rate, period and speed as a function of latitude.
"""
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sunspot_groups import load_groups
from solar_geometry import (CARRINGTON_RATE, YEAR_DAYS, julian_day, earth_orbital_rate,
                            fit_line, speed_km_s)

from paths import D, F
MAX_CMD = 60          # only use positions within 60° of the central meridian (less foreshortening)
rng = np.random.default_rng(0)

# ---------- read Greenwich (1874-1976) and USAF/NOAA (1977-2026) group positions ----------
g = load_groups()
print(f"Read {len(g):,} daily group positions, {g.time.min():%Y-%m} to {g.time.max():%Y-%m}")

# ---------- one rotation rate per disk passage ----------
g = g[g.cmd.abs() <= MAX_CMD].sort_values(["era", "gid", "time"])
new = (g.gid != g.gid.shift()) | ((g.time - g.time.shift()).dt.days > 3)
g["passage"] = new.cumsum()
out = []
for _, p in g.groupby("passage"):
    t = julian_day(p.time.values)
    if p.time.dt.normalize().nunique() < 4 or t.max() - t.min() < 3: continue
    lon = np.degrees(np.unwrap(np.radians(p.lcar.values)))
    s, s_err, rms = fit_line(t - t[0], lon)                       # drift in Carrington frame
    w_syn, _, _ = fit_line(t - t[0], p.cmd.values)                # motion across the disk (seen from Earth)
    out.append(dict(era=p.era.iloc[0], gid=p.gid.iloc[0], start=p.time.iloc[0], n=len(p),
                    days=t.max() - t.min(), lat=p.lat.mean(), area=p.area.max(),
                    omega=CARRINGTON_RATE + s, omega_err=s_err, rms=rms,
                    omega_syn=w_syn, omega_earth=earth_orbital_rate(t.mean())))
r = pd.DataFrame(out)
n_all = len(r)
r = r[(r.rms <= 2) & r.omega.between(10, 18)].copy()   # drop mis-identified / badly tracked groups
r["abslat"] = r.lat.abs(); r["s2"] = np.sin(np.radians(r.lat)) ** 2
print(f"Disk passages tracked: {n_all:,}; kept after quality cuts: {len(r):,} "
      f"(Greenwich {sum(r.era.str.startswith('G')):,}, USAF/NOAA {sum(r.era.str.startswith('U')):,})")
r.to_csv(D + "rotation_groups.csv", index=False)

# two ways to get the sidereal rate must agree: Carrington drift vs (motion across disk + Earth's orbit)
d = r.omega - (r.omega_syn + r.omega_earth)
print(f"Check: sidereal rate from Carrington longitudes minus (synodic rate + Earth's orbital rate): "
      f"median {d.median():+.3f} deg/day")
e = r.omega_earth - 360 / YEAR_DAYS
print(f"       Using a constant 0.9856 deg/day for the Earth (the simple formula) instead is off by "
      f"{e.min():+.3f} .. {e.max():+.3f} deg/day depending on the season")

# ---------- fit omega = A + B sin^2(lat) (+ C sin^4) ----------
def fit(df, terms=2):
    X = np.vstack([np.ones(len(df)), df.s2, df.s2 ** 2][:terms]).T
    keep = np.ones(len(df), bool)
    for _ in range(5):                                     # 3-sigma clipping of outliers
        c, *_ = np.linalg.lstsq(X[keep], df.omega.values[keep], rcond=None)
        res = df.omega.values - X @ c
        keep = np.abs(res) < 3 * res[keep].std()
    boot = [np.linalg.lstsq(X[keep][i], df.omega.values[keep][i], rcond=None)[0]
            for i in [rng.integers(0, keep.sum(), keep.sum()) for _ in range(200)]]
    return c, np.std(boot, axis=0), keep.sum()

print("\nFit  omega(lat) = A + B sin²(lat)   [deg/day, sidereal]")
print("   (each fit removes its own outliers beyond 3 standard deviations, so the counts of the two eras")
print("    need not add up exactly to the count of the combined fit)")
fits = {}
for lab, df in [("All groups", r)] + list(r.groupby("era")):
    c, e, n = fit(df); fits[lab] = (c, e)
    print(f"   {lab:22s}: A = {c[0]:.3f} ± {e[0]:.3f}, B = {c[1]:.2f} ± {e[1]:.2f}   "
          f"({n:,} groups used, {len(df) - n:,} outliers removed)")
(cA, eA), (cG, _), (cU, _) = fits["All groups"], fits["Greenwich 1874-1976"], fits["USAF/NOAA 1977-2026"]
sA, sB = abs(cG[0] - cU[0]) / 2, abs(cG[1] - cU[1]) / 2
print(f"   Result: A = {cA[0]:.3f} ± {eA[0]:.3f} (statistical) ± {sA:.3f} (systematic), "
      f"B = {cA[1]:.2f} ± {eA[1]:.2f} (statistical) ± {sB:.2f} (systematic)")
print("   systematic = half the difference between the two independent datasets (Greenwich vs USAF/NOAA)")
fits = {k: v[0] for k, v in fits.items()}
c3, e3, _ = fit(r, 3)
print(f"   with sin⁴ term       : A = {c3[0]:.3f} ± {e3[0]:.3f}, B = {c3[1]:.2f} ± {e3[1]:.2f}, "
      f"C = {c3[2]:.2f} ± {e3[2]:.2f}  (C is poorly fixed: almost no sunspots above 40°)")
A, B = fits["All groups"]
lat_carr = np.degrees(np.arcsin(np.sqrt((CARRINGTON_RATE - A) / B)))
print(f"   Carrington's 14.184 deg/day matches sunspots at latitude {lat_carr:.1f}°")
for lab, df in [("North", r[r.lat > 0]), ("South", r[r.lat < 0])]:
    c, e, _ = fit(df); print(f"   {lab} hemisphere      : A = {c[0]:.3f} ± {e[0]:.3f}, B = {c[1]:.2f} ± {e[1]:.2f}")

omega = lambda lat, c=(A, B): c[0] + c[1] * np.sin(np.radians(lat)) ** 2
SU = lambda lat: 14.713 - 2.396 * np.sin(np.radians(lat))**2 - 1.787 * np.sin(np.radians(lat))**4

# ---------- binned values and the summary table ----------
bins = np.arange(0, 42.5, 2.5)
r["bin"] = pd.cut(r.abslat, bins)
b = r.groupby("bin", observed=True).agg(lat=("abslat", "mean"), omega=("omega", "median"),
                                         sd=("omega", "std"), n=("omega", "size"))
b["se"] = 1.253 * b.sd / np.sqrt(b.n)
b = b[b.n >= 20]
print("\nMeasured rotation by latitude band (median of groups):")
print(b[["lat", "omega", "se", "n"]].round(3).to_string())

print("\nRotation period and speed (from the fit; * = beyond the sunspot belt, extrapolated):")
print(" lat   omega(deg/d)  P_sidereal(d)  P_seen-from-Earth(d)  speed(km/s)")
for lat in [0, 10, 15, 20, 30, 40, 60, 90]:
    w = omega(lat); wsyn = w - 360 / YEAR_DAYS
    print(f" {lat:3d}{'*' if lat > 40 else ' '}   {w:7.3f}       {360 / w:6.2f}          {360 / wsyn:6.2f}"
          f"               {speed_km_s(w, lat):5.3f}")

# ---------- figure 1: rate, period, speed vs latitude ----------
L = np.linspace(-40, 40, 161); Lx = np.linspace(0, 90, 181)
fig, (a1, a2, a3) = plt.subplots(1, 3, figsize=(17, 5.2))
a1.hexbin(r.lat, r.omega, gridsize=(60, 40), extent=(-42, 42, 12, 16), cmap="Greys", mincnt=1, bins="log")
sb = r.assign(sbin=pd.cut(r.lat, np.arange(-40, 42.5, 2.5))).groupby("sbin", observed=True).omega
mid = np.array([i.mid for i in sb.median().index])
se = 1.253 * sb.std() / np.sqrt(sb.size())
ok = sb.size().values >= 20
a1.errorbar(mid[ok], sb.median().values[ok], yerr=se.values[ok], fmt="o", c="tab:red", ms=4,
            label="Median of each 2.5° band")
a1.plot(L, omega(L), c="tab:red", lw=2, label=f"Fit: {A:.2f} {B:+.2f} sin²(lat)")
a1.plot(L, SU(L), c="tab:blue", ls="--", label="Snodgrass & Ulrich 1990 (Doppler features)")
a1.axhline(CARRINGTON_RATE, c="k", ls=":", lw=1); a1.text(-41, CARRINGTON_RATE + 0.05, "Carrington rate", fontsize=8)
a1.set_xlim(-42, 42); a1.set_ylim(12.5, 15.5)
a1.set_xlabel("Latitude (°, south negative)"); a1.set_ylabel("Sidereal rotation rate (°/day)")
a1.set_title(f"(a) Rotation rate of {len(r):,} sunspot groups"); a1.legend(fontsize=8, loc="lower center")

for per, lab, col in [(lambda x: 360 / omega(x), "Sidereal (true rotation)", "tab:red"),
                      (lambda x: 360 / (omega(x) - 360 / YEAR_DAYS), "Synodic (seen from Earth)", "tab:orange")]:
    a2.plot(Lx[Lx <= 40], per(Lx[Lx <= 40]), c=col, lw=2, label=lab)
    a2.plot(Lx[Lx >= 40], per(Lx[Lx >= 40]), c=col, lw=1.5, ls="--")
a2.plot(Lx, 360 / SU(Lx), c="tab:blue", ls="--", lw=1, label="Sidereal, Doppler measurement (Snodgrass & Ulrich)")
a2.scatter(b.lat, 360 / b.omega, c="tab:red", s=15, zorder=3)
a2.axvspan(40, 90, color="0.92"); a2.text(42, 24.6, "no sunspots here:\nextrapolated (dashed)", fontsize=8)
a2.set_xlabel("|Latitude| (°)"); a2.set_ylabel("Rotation period (days)"); a2.set_xlim(0, 90)
a2.set_title("(b) Rotation period"); a2.legend(fontsize=8, loc="upper left")

a3.plot(Lx[Lx <= 40], speed_km_s(omega(Lx[Lx <= 40]), Lx[Lx <= 40]), c="tab:red", lw=2,
        label="v = ω · R · cos(lat)  (measured ω)")
a3.plot(Lx[Lx >= 40], speed_km_s(omega(Lx[Lx >= 40]), Lx[Lx >= 40]), c="tab:red", lw=1.5, ls="--")
a3.plot(Lx, speed_km_s(omega(0), Lx), c="0.5", ls=":", label="If the Sun rotated like a solid ball")
a3.scatter(b.lat, speed_km_s(b.omega, b.lat), c="tab:red", s=15, zorder=3)
a3.axvspan(40, 90, color="0.92")
a3.set_xlabel("|Latitude| (°)"); a3.set_ylabel("Surface speed (km/s)"); a3.set_xlim(0, 90); a3.set_ylim(0, None)
a3.set_title("(c) Speed of the surface"); a3.legend(fontsize=8)
plt.tight_layout(); plt.savefig(F + "rotation_vs_latitude.png", dpi=150)

# ---------- figure 2: what differential rotation does to a straight line (the Omega effect) ----------
fig, axs = plt.subplots(1, 4, figsize=(15, 4.2))
lat_line = np.linspace(-40, 40, 81)
th = np.linspace(0, 2 * np.pi, 200)
for ax, days in zip(axs, [0, 27, 54, 108]):
    ax.plot(np.cos(th), np.sin(th), c="k", lw=1)
    for gl in range(-60, 61, 30):                       # latitude grid
        ax.plot(np.cos(np.radians(gl)) * np.sin(np.linspace(-np.pi/2, np.pi/2, 50)),
                np.full(50, np.sin(np.radians(gl))), c="0.85", lw=.6)
    lag = (omega(lat_line) - omega(0)) * days           # degrees behind the equator
    for off, alpha in [(0, 1)]:
        lon = np.radians(lag + off)
        vis = np.cos(lon) > 0
        x, y = np.cos(np.radians(lat_line)) * np.sin(lon), np.sin(np.radians(lat_line))
        ax.plot(np.where(vis, x, np.nan), np.where(vis, y, np.nan), c="tab:red", lw=3)
    ax.set_title(f"after {days} days" + ("" if days == 0 else f" (≈{days / 27:.0f} rotation{'s' if days > 27 else ''})"),
                 fontsize=10)
    ax.set_aspect("equal"); ax.axis("off"); ax.set_xlim(-1.1, 1.1); ax.set_ylim(-1.1, 1.1)
fig.suptitle("A straight line of gas from 40°S to 40°N, carried by the measured differential rotation "
             "(view rotating with the equator)", fontsize=11)
plt.tight_layout(); plt.savefig(F + "differential_rotation_shear.png", dpi=150)
pd.DataFrame({"A": [A], "B": [B]}).to_csv(D + "rotation_fit.csv", index=False)
