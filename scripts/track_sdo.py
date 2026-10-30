"""Steps 1-2 (hands-on version): track sunspots on 7 daily SDO/HMI images (12-18 Dec 2014).

This is what a student can do by hand, automated:
  1. find the centre and radius of the solar disk on each image,
  2. find the pixel position of each sunspot,
  3. turn pixels into heliographic latitude / longitude with trigonometry (solar_geometry.py),
  4. follow the same spot from day to day and fit a straight line: slope = rotation rate.
Dates chosen because B0 is almost 0 (|B0| < 1.3°) and big spots sit at 4°-30° latitude.
"""
import json, os, string, urllib.request, numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image
from scipy import ndimage
from scipy.optimize import linear_sum_assignment
from solar_geometry import (CARRINGTON_RATE, YEAR_DAYS, julian_day, sun_ephemeris, earth_orbital_rate,
                            pixel_to_helio, helio_to_pixel, simple_pixel_to_helio, fit_line, speed_km_s)
from sunspot_groups import load_groups

from paths import D, F
IMG = D + "sdo/"; os.makedirs(IMG, exist_ok=True); os.makedirs(D + "rotation", exist_ok=True)
DAYS = pd.date_range("2014-12-12", "2014-12-18")
API = "https://api.helioviewer.org/v2/"
SPOT_LEVEL = 0.80     # darker than 80% of the normal surface brightness = sunspot
MIN_AREA = 20         # pixels; smaller dark specks are ignored
MAX_CMD = 60          # use positions within 60° of the central meridian for the fit


def get_image(day):
    """HMI continuum image, 2048x2048, 1 arcsec/pixel, solar north up (helioviewer.org)."""
    stamp = f"{day:%Y-%m-%d}T00:00:00Z"
    png, meta_file = IMG + f"hmi_{day:%Y%m%d}.png", IMG + f"hmi_{day:%Y%m%d}.json"
    jpg = png.replace(".png", ".jpg")
    if not os.path.exists(meta_file):
        meta = json.load(urllib.request.urlopen(f"{API}getClosestImage/?date={stamp}&sourceId=18", timeout=60))
        json.dump(meta, open(meta_file, "w"))
    if not os.path.exists(png) and os.path.exists(jpg):
        # the repository keeps only the JPG copies; results agree with the PNG originals within 0.01 °/day
        return jpg, json.load(open(meta_file))
    if not os.path.exists(png):
        urllib.request.urlretrieve(f"{API}takeScreenshot/?date={stamp}&imageScale=1.0&layers=%5B18,1,100%5D"
                                   "&x0=0&y0=0&width=2048&height=2048&display=true&watermark=false", png)
    if not os.path.exists(png.replace(".png", ".jpg")):          # small copy for measuring by hand
        Image.open(png).convert("L").save(png.replace(".png", ".jpg"), quality=92)
    return png, json.load(open(meta_file))


def find_disk(gray):
    """Disk centre and radius: take the edge of the bright disk and fit a circle through it."""
    # The outermost ring is only ~45% as bright as the disk centre (limb darkening) and then drops to
    # black within about 3 pixels. Half the median would cut inside that ring, so cut at a quarter.
    level = 0.25 * np.median(gray[gray > 50])
    lab, _ = ndimage.label(gray > level)
    disk = ndimage.binary_fill_holes(lab == np.bincount(lab.ravel())[1:].argmax() + 1)
    yy, xx = np.nonzero(disk & ~ndimage.binary_erosion(disk))
    # circle x² + y² = 2a·x + 2b·y + c  ->  centre (a, b), radius sqrt(c + a² + b²)
    (a, b, c), *_ = np.linalg.lstsq(np.c_[2 * xx, 2 * yy, np.ones(len(xx))], xx**2 + yy**2, rcond=None)
    return a, b, np.sqrt(c + a * a + b * b)


def find_spots(gray, xc, yc, r):
    """Dark patches inside the disk; position = darkness-weighted centre."""
    yy, xx = np.indices(gray.shape)
    rr = np.hypot(xx - xc, yy - yc) / r
    edges = np.linspace(0, 0.97, 50)
    ring = np.digitize(rr, edges)
    prof = ndimage.median(gray, ring, index=np.arange(1, len(edges)))      # normal brightness per ring
    norm = gray / np.interp(rr, (edges[:-1] + edges[1:]) / 2, prof)
    lab, n = ndimage.label((norm < SPOT_LEVEL) & (rr < 0.95))
    spots = []
    for i, sl in enumerate(ndimage.find_objects(lab), 1):
        m = lab[sl] == i
        if m.sum() < MIN_AREA: continue
        w = np.clip(1 - norm[sl], 0, None) * m
        y0, x0 = sl[0].start, sl[1].start
        spots.append(dict(x=(w * xx[sl]).sum() / w.sum(), y=(w * yy[sl]).sum() / w.sum(),
                          area_px=int(m.sum()), darkest=norm[sl][m].min()))
    return pd.DataFrame(spots)


# ---------- 1-3: measure every image ----------
det, disks = [], {}
for day in DAYS:
    png, meta = get_image(day)
    t = pd.Timestamp(meta["date"])
    gray = np.asarray(Image.open(png).convert("L"), float)
    xc, yc, r = find_disk(gray)
    B0, L0, _ = sun_ephemeris(julian_day(t.to_datetime64()))
    disks[day] = dict(time=t, xc=xc, yc=yc, r=r, B0=float(B0), L0=float(L0), png=png)
    s = find_spots(gray, xc, yc, r)
    s["lat"], s["cmd"] = pixel_to_helio(s.x, s.y, xc, yc, r, B0)
    s["lat_simple"], s["cmd_simple"] = simple_pixel_to_helio(s.x, s.y, xc, yc, r)
    s["lon"] = (L0 + s.cmd) % 360                                           # Carrington longitude
    s["day"], s["time"] = day, t
    det.append(s)
    print(f"{t:%Y-%m-%d %H:%M} UT  disk centre ({xc:7.1f},{yc:7.1f}) px, radius {r:6.1f} px, "
          f"B0 {float(B0):+.2f}°  ->  {len(s)} dark spots")
det = pd.concat(det, ignore_index=True)

# ---------- 4: follow each spot from day to day (match by latitude and Carrington longitude) ----------
tracks = []
for day in DAYS:
    today = det[det.day == day]
    active = [tr for tr in tracks if 1 <= (day - det.day[tr[-1]]).days <= 2]
    used = set()
    if active and len(today):
        cost = np.full((len(active), len(today)), 99.0)
        for i, tr in enumerate(active):
            last = det.loc[tr[-1]]; dt = (day - last.day).days
            dlat = (today.lat.values - last.lat) / 1.5                       # within 1.5° in latitude
            dlon = ((today.lon.values - last.lon + 180) % 360 - 180) / (1.5 * dt + 0.5)   # 2° per day
            darea = np.abs(np.log(today.area_px.values / last.area_px)) / np.log(5)  # not 5x bigger/smaller
            cost[i] = np.sqrt(dlat**2 + dlon**2 + darea**2)
        for i, j in zip(*linear_sum_assignment(cost)):
            if cost[i, j] < 1: active[i].append(today.index[j]); used.add(j)
    tracks += [[today.index[j]] for j in range(len(today)) if j not in used]

noaa = load_groups(2014, 2014)
noaa = noaa[noaa.time.dt.normalize().isin(DAYS)]
rows = []
for k, tr in enumerate(tracks):
    p = det.loc[tr]
    p = p[p.cmd.abs() <= MAX_CMD]
    if len(p) < 4: continue
    t = julian_day(p.time.values); t0 = julian_day(np.datetime64("2014-12-12"))
    s, s_err, rms = fit_line(t - t0, np.degrees(np.unwrap(np.radians(p.lon.values))))
    w_syn, w_syn_err, _ = fit_line(t - t0, p.cmd.values)
    w_simple, _, _ = fit_line(t - t0, p.cmd_simple.values)
    # which NOAA active region is this spot in? (nearest NOAA group on the same days)
    reg = []
    for _, q in p.iterrows():
        cand = noaa[(noaa.time.dt.normalize() == q.time.round("D"))]
        dist = np.hypot(cand.lat - q.lat, cand.cmd - q.cmd)
        if len(cand) and dist.min() < 10: reg.append(cand.gid[dist.idxmin()])
    region = max(set(reg), key=reg.count) if reg else "-"
    rows.append(dict(track=k, noaa=region, n=len(p), lat=p.lat.mean(), area_px=p.area_px.mean(),
                     omega=CARRINGTON_RATE + s, omega_err=s_err, rms=rms, omega_syn=w_syn,
                     omega_check=w_syn + earth_orbital_rate(t.mean()),
                     omega_simple=w_simple + 360 / YEAR_DAYS,
                     noaa_lat=noaa[noaa.gid == region].lat.mean() if region != "-" else np.nan))
res = pd.DataFrame(rows)
# one spot per active region: the one followed longest, then the biggest
best = (res[res.noaa != "-"].sort_values(["n", "area_px"], ascending=False)
        .drop_duplicates("noaa").sort_values("lat", ascending=False).reset_index(drop=True))
best["label"] = list(string.ascii_uppercase[:len(best)])
A, B = pd.read_csv(D + "rotation_fit.csv").iloc[0]
best["omega_150yr"] = A + B * np.sin(np.radians(best.lat)) ** 2
best["P_sid"], best["P_syn"] = 360 / best.omega, 360 / best.omega_syn
best["speed"] = speed_km_s(best.omega, best.lat)
print(f"\n{len(det)} spot detections, {len(tracks)} tracks, {len(res)} followed for >= 4 days "
      f"within {MAX_CMD}° of the central meridian; best spot of each NOAA region:")
print(" spot  NOAA   our lat  NOAA lat  days   omega (°/day)   150-yr fit  P_sid  P_syn  speed(km/s)")
for _, b in best.iterrows():
    print(f"  {b.label}   {b.noaa}  {b.lat:+6.1f}   {b.noaa_lat:+6.1f}    {b.n:d}    {b.omega:6.2f} ± {b.omega_err:.2f}"
          f"     {b.omega_150yr:6.2f}    {b.P_sid:5.2f}  {b.P_syn:5.2f}   {b.speed:5.2f}")
r150 = pd.read_csv(D + "rotation_groups.csv")
res150 = r150.omega - (A + B * np.sin(np.radians(r150.lat)) ** 2)
d = best.omega - best.omega_150yr
print(f"Our spots minus the 150-year fit: mean {d.mean():+.2f}, spread {d.std():.2f} °/day. "
      f"Single groups in the 150-year data spread by {res150.std():.2f} °/day "
      f"(middle 68%: {res150.quantile(.16):+.2f} .. {res150.quantile(.84):+.2f})")
X = np.c_[np.ones(len(best)), np.sin(np.radians(best.lat)) ** 2]
own, rss, *_ = np.linalg.lstsq(X, best.omega.values, rcond=None)
own_err = np.sqrt(np.diag(rss[0] / (len(best) - 2) * np.linalg.inv(X.T @ X)))
print(f"Fit to our {len(best)} spots only: omega = {own[0]:.2f} ± {own_err[0]:.2f} {own[1]:+.2f} ± {own_err[1]:.2f} sin²(lat)"
      f"   (150-year fit: {A:.2f} {B:+.2f} sin²(lat))")
print(f"Latitude check vs NOAA: mean |difference| {np.mean(np.abs(best.lat - best.noaa_lat)):.1f}° "
      f"(NOAA gives the centre of the whole group, we measure one spot)")
print(f"Simple school formulas (no B0, Earth = 0.9856 °/day) vs full method: "
      f"max difference {np.max(np.abs(best.omega_simple - best.omega)):.3f} °/day")
print(f"Two ways to the sidereal rate (Carrington drift vs synodic + Earth): "
      f"max difference {np.max(np.abs(best.omega_check - best.omega)):.3f} °/day")
best.to_csv(D + "rotation/sdo_spot_results.csv", index=False)

# positions of the chosen spots, in the format a student would write down by hand
pos = []
for _, b in best.iterrows():
    for i in tracks[int(b.track)]:
        q = det.loc[i]; dk = disks[q.day]
        pos.append(dict(spot=b.label, noaa=b.noaa, time_utc=f"{q.time:%Y-%m-%d %H:%M:%S}",
                        jd=round(float(julian_day(q.time.to_datetime64())), 5),
                        x_px=round(q.x, 1), y_px=round(q.y, 1), disk_cx_px=round(dk["xc"], 1),
                        disk_cy_px=round(dk["yc"], 1), disk_r_px=round(dk["r"], 1),
                        image=os.path.basename(dk["png"]).replace(".png", ".jpg")))
pos = pd.DataFrame(pos); pos.to_csv(D + "rotation/sdo_spot_positions.csv", index=False)

# ---------- worked example (for the write-up) ----------
ex = best.sort_values(["n", "area_px"], ascending=False).iloc[0]     # the spot followed longest
e = pos[pos.spot == ex.label].reset_index(drop=True)
e = e[[abs(c) <= MAX_CMD for c in pixel_to_helio(e.x_px, e.y_px, e.disk_cx_px, e.disk_cy_px, e.disk_r_px)[1]]]
e1, e2 = e.iloc[0], e.iloc[-1]
print(f"\nWorked example, spot {ex.label} (NOAA {ex.noaa}):")
for q in [e1, e2]:
    X = (q.x_px - q.disk_cx_px) / q.disk_r_px; Y = -(q.y_px - q.disk_cy_px) / q.disk_r_px
    la = np.degrees(np.arcsin(Y)); cm = np.degrees(np.arcsin(X / np.cos(np.radians(la))))
    print(f"   {q.time_utc}: spot ({q.x_px}, {q.y_px}) px, disk centre ({q.disk_cx_px}, {q.disk_cy_px}), "
          f"R = {q.disk_r_px} px -> X = {X:+.4f}, Y = {Y:+.4f} -> latitude {la:+.2f}°, CMD {cm:+.2f}°")
dt = (pd.Timestamp(e2.time_utc) - pd.Timestamp(e1.time_utc)).total_seconds() / 86400
cm1 = np.degrees(np.arcsin(((e1.x_px - e1.disk_cx_px) / e1.disk_r_px) / np.cos(np.arcsin(-(e1.y_px - e1.disk_cy_px) / e1.disk_r_px))))
cm2 = np.degrees(np.arcsin(((e2.x_px - e2.disk_cx_px) / e2.disk_r_px) / np.cos(np.arcsin(-(e2.y_px - e2.disk_cy_px) / e2.disk_r_px))))
wsyn = (cm2 - cm1) / dt
print(f"   moved {cm2 - cm1:.2f}° in {dt:.3f} days -> synodic {wsyn:.3f} °/day -> sidereal {wsyn + 360 / YEAR_DAYS:.3f} °/day"
      f" -> period {360 / (wsyn + 360 / YEAR_DAYS):.2f} days, speed {speed_km_s(wsyn + 360 / YEAR_DAYS, ex.lat):.2f} km/s")

# ---------- figures ----------
cols = plt.cm.tab10(np.arange(len(best)))


def draw_grid(ax, dk):
    for la in range(-60, 61, 15):
        cm = np.linspace(-90, 90, 181); x, y = helio_to_pixel(la, cm, dk["xc"], dk["yc"], dk["r"], dk["B0"])
        ax.plot(x, y, c="tab:cyan", lw=0.5, alpha=0.6)
    for cm in range(-75, 76, 15):
        la = np.linspace(-90, 90, 181); x, y = helio_to_pixel(la, cm, dk["xc"], dk["yc"], dk["r"], dk["B0"])
        ax.plot(x, y, c="tab:cyan", lw=0.5, alpha=0.6, ls="-" if cm else "--")


fig, axs = plt.subplots(1, 2, figsize=(16, 8.4))
for ax, day, title in [(axs[0], DAYS[0], f"{disks[DAYS[0]]['time']:%d %b %Y %H:%M} UT: spots found and labelled"),
                       (axs[1], DAYS[-1], f"{disks[DAYS[-1]]['time']:%d %b %Y %H:%M} UT: where each spot was on every day")]:
    dk = disks[day]
    ax.imshow(Image.open(dk["png"]).convert("L"), cmap="gray", vmin=0, vmax=255)
    draw_grid(ax, dk)
    for (_, b), c in zip(best.iterrows(), cols):
        q = det.loc[tracks[int(b.track)]]
        if ax is axs[1]:
            ax.plot(q.x, q.y, "-o", c=c, ms=3, lw=1.2)
            last = q.iloc[-1]
        else:
            q0 = q[q.day == day]
            if not len(q0): continue
            last = q0.iloc[0]
        ax.plot(last.x, last.y, "o", mfc="none", mec=c, ms=16, mew=2)
        ax.text(last.x + 22, last.y - 22, f"{b.label}", color=c, fontsize=13, fontweight="bold")
    ax.set_xlim(dk["xc"] - 1.03 * dk["r"], dk["xc"] + 1.03 * dk["r"])
    ax.set_ylim(dk["yc"] + 1.03 * dk["r"], dk["yc"] - 1.03 * dk["r"])
    ax.set_title(title + "  (grid: every 15° of latitude / longitude)", fontsize=11); ax.axis("off")
plt.tight_layout(); plt.savefig(F + "sdo_tracking.png", dpi=110)

fig, axs = plt.subplots(1, len(DAYS), figsize=(18, 3.2))
for ax, day in zip(axs, DAYS):
    dk = disks[day]
    ax.imshow(Image.open(dk["png"]).convert("L"), cmap="gray", vmin=0, vmax=255)
    for (_, b), c in zip(best.iterrows(), cols):
        q = det.loc[tracks[int(b.track)]]; q = q[q.day == day]
        if len(q):
            ax.plot(q.x, q.y, "o", mfc="none", mec=c, ms=9, mew=1.5)
            ax.text(q.x.iloc[0] + 40, q.y.iloc[0] - 40, b.label, color=c, fontsize=9, fontweight="bold")
    ax.set_xlim(dk["xc"] - 1.02 * dk["r"], dk["xc"] + 1.02 * dk["r"])
    ax.set_ylim(dk["yc"] + 1.02 * dk["r"], dk["yc"] - 1.02 * dk["r"])
    ax.set_title(f"{dk['time']:%d %b %H:%M} UT", fontsize=10); ax.axis("off")
plt.tight_layout(); plt.savefig(F + "sdo_daily_strip.png", dpi=110)

fig, (a1, a2) = plt.subplots(1, 2, figsize=(15, 5.5))
t0 = julian_day(np.datetime64("2014-12-12"))
for (_, b), c in zip(best.iterrows(), cols):
    q = det.loc[tracks[int(b.track)]]; q = q[q.cmd.abs() <= MAX_CMD]
    t = julian_day(q.time.values) - t0
    a1.plot(t, q.cmd, "o", c=c)
    k = np.polyfit(t, q.cmd, 1); tt = np.array([t.min(), t.max()])
    a1.plot(tt, np.polyval(k, tt), c=c, label=f"{b.label} (lat {b.lat:+.0f}°): {k[0]:.2f}°/day across the disk")
a1.set_xlabel("Days since 12 Dec 2014 00:00 UT (images taken 20 s before midnight)"); a1.set_ylabel("Longitude from central meridian (°)")
a1.set_title("Each spot moves along a straight line: slope = rotation rate (seen from Earth)")
a1.set_ylim(-65, 135); a1.legend(fontsize=8, ncol=2, loc="upper left")
r150 = pd.read_csv(D + "rotation_groups.csv")
L = np.linspace(-35, 35, 141)
a2.hexbin(r150.lat, r150.omega, gridsize=(50, 30), extent=(-36, 36, 12.5, 16), cmap="Greys", mincnt=1, bins="log")
a2.plot(L, A + B * np.sin(np.radians(L)) ** 2, c="tab:red", lw=2, label="150-year fit (21,003 groups)")
a2.plot(L, own[0] + own[1] * np.sin(np.radians(L)) ** 2, c="k", lw=1.5, ls="--", label=f"Fit to our {len(best)} spots only")
for (_, b), c in zip(best.iterrows(), cols):
    a2.errorbar(b.lat, b.omega, yerr=b.omega_err, fmt="o", c=c, ms=9, mec="k", capsize=4,
                label=f"Spot {b.label} (NOAA {b.noaa})")
a2.set_xlim(-36, 36); a2.set_ylim(12.8, 15.6)
a2.set_xlabel("Latitude (°)"); a2.set_ylabel("Sidereal rotation rate (°/day)")
a2.set_title("Our 7-day measurement vs 150 years of data"); a2.legend(fontsize=8, ncol=2, loc="lower center")
plt.tight_layout(); plt.savefig(F + "sdo_rotation_result.png", dpi=150)
