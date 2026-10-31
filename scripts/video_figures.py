"""Video / slide figures (16:9, 1920x1080) built from the results of steps 1-4.

All numbers are read from the data and result files, so the figures follow any rerun.
Output: figures/video/*.png
"""
import json, numpy as np, pandas as pd
from PIL import Image
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Patch, Arc
from video_style import canvas, save, num, BODY, BG, PANEL, TXT, MUT, GRID, SUN, RED, CYAN, GREEN, BLUE
from paths import D
from sunspot_groups import load_groups
from solar_geometry import YEAR_DAYS, earth_orbital_rate
import manual_rotation as mr

# ---------------------------------------------------------------- shared data
sn = pd.read_csv(D + "SN_m_tot_V2.0.csv", sep=";", header=None, names=["y", "m", "t", "ssn", "sd", "n", "p"])
sn["smooth"] = np.convolve(sn.ssn, np.r_[0.5, np.ones(11), 0.5] / 12, mode="same")
sn.loc[:5, "smooth"] = np.nan; sn.loc[len(sn) - 6:, "smooth"] = np.nan
fc = json.load(open(D + "forecast_v2_summary.json"))
ens = pd.read_csv(D + "forecast_v2_ensemble.csv")
ssn35 = pd.read_csv(D + "forecast_v2_ssn2035_samples.csv").ssn_2035
A, B = pd.read_csv(D + "rotation_fit.csv").iloc[0]
yr = pd.read_csv(D + "flares_per_year.csv", index_col=0)
bc = pd.read_csv(D + "butterfly_cycles.csv", index_col=0)
R3_RATE = yr["R3+ (≥X1)"].sum() / yr.SSN.sum()          # X-class flares per year per unit sunspot number
R1_RATE = yr["R1+ (≥M1)"].sum() / yr.SSN.sum()
MAX35 = fc["max_mean"]
SRC_SSN = "Sunspot number: WDC-SILSO, Royal Observatory of Belgium"
WALK = D + "rotation/manual_walkthrough.csv"


def omega(lat):
    return A + B * np.sin(np.radians(lat)) ** 2


def note(ax, x, y, text, color=TXT, size=16, **kw):
    ax.text(x, y, text, color=color, fontsize=size, **kw)


def hemi(lat):
    return f"{abs(lat):.0f}°{'N' if lat > 0 else 'S'}"


def yearly_forecast():
    return ens.assign(yy=ens.year.astype(int)).groupby("yy")[["p10", "p50", "p90"]].mean().loc[2030:2041]


# ---------------------------------------------------------------- 1. cover
def cover():
    fig = plt.figure(figsize=(16, 9), dpi=120)
    img = np.asarray(Image.open(D + "sdo/hmi_20141215.png").convert("L"), float)
    yy, xx = np.indices(img.shape)
    lit = img > 0.25 * np.median(img[img > 50])                 # same disk threshold as the measurements
    cy, cx, r = yy[lit].mean(), xx[lit].mean(), np.sqrt(lit.sum() / np.pi)
    img[(xx - cx) ** 2 + (yy - cy) ** 2 > (r + 2) ** 2] = np.nan
    cmap = plt.get_cmap("afmhot").copy(); cmap.set_bad(BG)
    ax = fig.add_axes([0.49, 0.04, 0.50, 0.50 * 16 / 9]); ax.imshow(img, cmap=cmap, vmin=0, vmax=290); ax.axis("off")
    fig.text(0.05, 0.70, "Forecasting the Sun\nfor the 2035 launch", fontsize=50, fontweight="bold", va="center", linespacing=1.15)
    fig.text(0.05, 0.47, "Sunspot tracking  ·  differential rotation\nbutterfly diagram  ·  solar-cycle and flare forecast",
             fontsize=21, color=MUT, va="center", linespacing=1.5)
    fig.text(0.05, 0.30, "Pitch to the ISECG launch panel", fontsize=22, color=SUN, fontweight="semibold")
    fig.text(0.05, 0.06, "Planet Hack 2026 · Seniors Challenge", fontsize=14, color=MUT)
    fig.text(0.05, 0.03, "Image: SDO/HMI continuum, 15 Dec 2014 (NASA SDO, via helioviewer.org)", fontsize=12, color=MUT)
    save(fig, "v01_cover.png")


# ---------------------------------------------------------------- 2. incidents
def incidents():
    fig = canvas("Solar storms hit Earth when the Sun is busy — 2035 will be busy",
                 "Yearly sunspot number (bars), our forecast to 2041 (orange) and six reported space-weather incidents",
                 "Sunspot number: WDC-SILSO. Incidents: Boteler 2019; NOAA 2004; Cerruti et al. 2008; "
                 "Redmon et al. 2018; SpaceX 2022; NOAA SWPC 2024")
    ax = fig.add_axes(BODY)
    ys = sn.groupby("y").ssn.mean().loc[1976:2026]
    ax.bar(ys.index, ys.values, color="#3B4C6E", width=0.8)
    e = yearly_forecast()
    ax.fill_between(e.index, e.p10, e.p90, color=SUN, alpha=0.25, step="mid", lw=0)
    ax.step(e.index, e.p50, where="mid", color=SUN, lw=3)
    ax.axvspan(2034.5, 2035.5, color=RED, alpha=0.22, lw=0)
    note(ax, 2035, 292, "2035\nlaunch", color=RED, size=16, ha="center", va="top", fontweight="bold")
    # (label text, label position) chosen so that no label or leader line crosses another
    labels = {1989: ("Mar 1989\nQuébec power grid\ncollapses", 1989, 241),
              2003: ("Oct 2003\nGPS & radio outages,\nflights rerouted", 2003, 194),
              2006: ("Dec 2006\nGPS receivers\nlose lock", 2006.6, 100),
              2017: ("Sep 2017\nradio blackout during\nhurricane rescue", 2014.5, 128),
              2022: ("Feb 2022\n38 Starlink\nsatellites lost", 2019.6, 200),
              2024: ("May 2024\nGPS-guided\ntractors disrupted", 2026.2, 248)}
    for y, (lab, tx, ty) in labels.items():
        v = ys[y]
        ax.plot(y, v, "o", ms=11, color=RED, mec=TXT, mew=1.5, zorder=5)
        ax.annotate(lab, (y, v), xytext=(tx, ty), ha="center", va="bottom", fontsize=13.5, color=TXT,
                    arrowprops=dict(arrowstyle="-", color=MUT, lw=1))
    ax.set_xlim(1975, 2041.5); ax.set_ylim(0, 300)
    ax.set_ylabel("Sunspot number")
    save(fig, "v02_incidents.png")


# ---------------------------------------------------------------- 3. butterfly
def butterfly():
    g = load_groups(2006, 2026).sort_values(["gid", "time"])
    new = (g.gid != g.gid.shift()) | ((g.time - g.time.shift()).dt.days > 3)
    p = g.assign(passage=new.cumsum()).groupby("passage").agg(time=("time", "mean"), lat=("lat", "mean"), area=("area", "max"))
    p["year"] = p.time.dt.year + (p.time.dt.dayofyear - 0.5) / 365.25
    c24, c25 = bc.loc["cycle 24"], bc.loc["cycle 25"]
    P = c24.period; rise = np.mean([c24.rise, c25.rise])
    nxt_start, nxt_max = c25.start + P, c25.start + P + rise
    full = bc.dropna(subset=["period"])
    all_max = c25.start + full.period.mean() + bc.rise.mean()
    fig = canvas(f"Our butterfly diagram: the Sun's cycle repeats every {P:.0f} years",
                 f"{len(p):,} sunspot groups, 2006–2026 (one dot per group, size = area). A new cycle starts when spots reappear at high latitude",
                 "Sunspot-group positions: D. Hathaway, Greenwich / USAF / NOAA records")
    ax = fig.add_axes(BODY)
    for hemi_, col in [(p.lat > 0, SUN), (p.lat < 0, CYAN)]:
        q = p[hemi_]; ax.scatter(q.year, q.lat, s=np.sqrt(q.area) * 1.3, color=col, alpha=0.45, lw=0)
    for s, lab in [(c24.start, "Cycle 24 starts"), (c25.start, "Cycle 25 starts")]:
        ax.axvline(s, color=TXT, ls="--", lw=1.5)
        note(ax, s + 0.25, 41, f"{lab}\n{s:.1f}", size=15, va="top")
    ax.annotate("", (c24.start, -37), (c25.start, -37), arrowprops=dict(arrowstyle="<->", color=TXT, lw=2))
    note(ax, (c24.start + c25.start) / 2, -35.5, f"{P:.1f} years", size=19, ha="center", fontweight="bold")
    ax.axvline(nxt_start, color=SUN, ls="--", lw=2)
    note(ax, nxt_start - 0.25, 41, f"Cycle 26 starts\n≈ {nxt_start:.0f}", color=SUN, size=15, va="top", ha="right")
    lo, hi = sorted([all_max, nxt_max])
    ax.axvspan(lo, hi, color=SUN, alpha=0.25, lw=0)
    note(ax, (lo + hi) / 2, 44, f"next maximum\n{lo:.0f}–{hi:.0f}", color=SUN, size=16, ha="center", va="top", fontweight="bold")
    ax.plot([2035, 2035], [-45, 33], color=RED, lw=2.5)
    note(ax, 2035.25, -30, "2035\nlaunch", color=RED, size=15, va="top", fontweight="bold")
    ax.set_xlim(2006, 2038.5); ax.set_ylim(-45, 45)
    ax.set_yticks([-40, -20, 0, 20, 40]); ax.set_yticklabels(["40°S", "20°S", "Equator", "20°N", "40°N"])
    save(fig, "v03_butterfly.png")


# ---------------------------------------------------------------- 4. forecast
def forecast():
    fig = canvas("The next solar maximum lands on our 2035 launch window",
                 f"Smoothed sunspot number: observed (white) and our forecast from {fc['n_combinations']} combinations of real past cycles (orange)",
                 f"{SRC_SSN}. Forecast: historical-analogue ensemble, cycles 10–24")
    ax = fig.add_axes(BODY)
    s = sn[sn.t >= 1996]
    ax.plot(s.t, s.smooth, color=TXT, lw=3)
    ax.fill_between(ens.year, ens.p10, ens.p90, color=SUN, alpha=0.2, lw=0, label="10–90% of analogues")
    ax.fill_between(ens.year, ens.p25, ens.p75, color=SUN, alpha=0.4, lw=0, label="25–75%")
    ax.plot(ens.year, ens.p50, color=SUN, lw=3, label="median")
    ax.axvspan(2035, 2036, color=RED, alpha=0.22, lw=0)
    note(ax, 2035.5, 292, "2035\nlaunch", color=RED, size=16, ha="center", va="top", fontweight="bold")
    for c, (t, v) in {23: (2001.9, 181), 24: (2014.3, 117), 25: (2024.8, 161)}.items():
        note(ax, t, v + 8, f"Cycle {c}", size=15, ha="center", color=MUT)
    n_in = round(fc["share_2034_2036"] * fc["n_estimates"])
    box = (f"Maximum: {fc['max_mean']:.1f} ± {fc['max_sd']:.1f}\n"
           f"({n_in} of {fc['n_estimates']} estimates from past cycles land in 2034–2036)\n\n"
           f"2035 sunspot number: {fc['ssn2035_median']:.0f}\n(10–90%: {fc['ssn2035_p10']:.0f}–{fc['ssn2035_p90']:.0f})")
    ax.text(0.015, 0.97, box, transform=ax.transAxes, va="top", fontsize=17, color=TXT,
            bbox=dict(boxstyle="round,pad=0.6", fc=PANEL, ec=GRID))
    ax.set_xlim(1996, 2041.5); ax.set_ylim(0, 300); ax.set_ylabel("Smoothed sunspot number")
    ax.legend(loc="upper left", bbox_to_anchor=(0.5, 1.0))
    save(fig, "v04_forecast.png")


# ---------------------------------------------------------------- 5. step 1: measuring
def measure():
    m = pd.read_csv(WALK)
    lat = mr.analyse(mr.load(WALK))[0].set_index("spot").lat
    img_name = m[m.spot == "A"].image.iloc[0]
    r = m[m.image == img_name]
    g = np.asarray(Image.open(D + "sdo/" + img_name.replace(".jpg", ".png")).convert("L"), float)
    d = r.iloc[0]
    t0, t1 = pd.to_datetime(m.time_utc).min(), pd.to_datetime(m.time_utc).max()
    fig = canvas("Step 1 — Track sunspots: pixel positions and Julian Dates",
                 f"SDO/HMI images, one per day, {t0:%-d}–{t1:%-d %b %Y}. Spot A sits at {hemi(lat['A'])}, spot E at {hemi(lat['E'])}",
                 "Image: NASA SDO/HMI via helioviewer.org. Measurements: data/rotation/manual_walkthrough.csv")
    ax = fig.add_axes([0.03, 0.06, 0.40, 0.40 * 16 / 9 * 0.98])
    ax.imshow(g, cmap="gray", vmin=0, vmax=255)
    ax.axhline(d.disk_cy_px, color=CYAN, lw=1); ax.axvline(d.disk_cx_px, color=CYAN, lw=1)
    for x, y in [(d.disk_left_px, d.disk_cy_px), (d.disk_right_px, d.disk_cy_px), (d.disk_cx_px, d.disk_top_px), (d.disk_cx_px, d.disk_bottom_px)]:
        ax.plot(x, y, "o", color=CYAN, ms=9)
    ax.plot(d.disk_cx_px, d.disk_cy_px, "+", color=CYAN, ms=22, mew=3)
    for _, q in r.iterrows():
        ax.plot(q.x_px, q.y_px, "o", mfc="none", mec=RED, ms=26, mew=3)
        note(ax, q.x_px + 45, q.y_px - 45, q.spot, color=RED, size=24, fontweight="bold")
    ax.set_xlim(0, g.shape[1]); ax.set_ylim(g.shape[0], 0); ax.axis("off")
    for k, (_, q) in enumerate(r.iterrows()):
        a = fig.add_axes([0.50 + k * 0.19, 0.49, 0.15, 0.15 * 16 / 9])
        x, y = int(q.x_px), int(q.y_px)
        a.imshow(g[y - 22:y + 23, x - 22:x + 23], cmap="gray", vmin=0, vmax=255, extent=(x - 22.5, x + 22.5, y + 22.5, y - 22.5))
        a.axhline(y, color=RED, lw=1.5); a.axvline(x, color=RED, lw=1.5); a.set_xticks([]); a.set_yticks([]); a.grid(False)
        a.set_title(f"Spot {q.spot}", fontsize=18, color=TXT, fontweight="bold")
        a.set_xlabel(f"x = {x},  y = {y}", fontsize=16, color=TXT)
    t = pd.Timestamp(d.time_utc)
    lines = [("Time", f"{t:%Y-%m-%d %H:%M:%S} UT"), ("Julian Date", f"{d.jd:.5f}"),
             ("Disk edges (px)", f"left {d.disk_left_px}, right {d.disk_right_px}, top {d.disk_top_px}, bottom {d.disk_bottom_px}"),
             ("Disk centre", f"({d.disk_cx_px}, {d.disk_cy_px})"), ("Disk radius", f"{d.disk_r_px} px")]
    for k, (a_, b_) in enumerate(lines):
        fig.text(0.50, 0.36 - k * 0.052, a_, fontsize=17, color=MUT)
        fig.text(0.64, 0.36 - k * 0.052, b_, fontsize=17, color=TXT)
    fig.text(0.50, 0.075, "Repeat for every image → a table of (x, y, Julian Date) for each spot", fontsize=17, color=SUN)
    save(fig, "v05_step1_measure.png")


# ---------------------------------------------------------------- 6. step 2: trigonometry
def trig():
    m = pd.read_csv(WALK)
    s = m[m.spot == "A"]; s1, s2 = s.iloc[0], s.iloc[-1]

    def conv(q):                                     # the school formulas (B0 ≈ 0 in mid-December)
        X = (q.x_px - q.disk_cx_px) / q.disk_r_px; Y = -(q.y_px - q.disk_cy_px) / q.disk_r_px
        lat = np.degrees(np.arcsin(Y)); return X, Y, lat, np.degrees(np.arcsin(X / np.cos(np.radians(lat))))
    X1, Y1, la1, c1 = conv(s1); X2, Y2, la2, c2 = conv(s2)
    dt = s2.jd - s1.jd; wsyn = (c2 - c1) / dt
    earth = earth_orbital_rate((s1.jd + s2.jd) / 2); wsid = wsyn + earth
    fig = canvas("Step 2 — Trigonometry turns pixels into a rotation rate",
                 f"Worked example: spot A, first and last image ({dt:.0f} days apart)",
                 "Simple formulas, valid because the Sun's axis is barely tilted toward us in mid-December (B0 ≈ 0)")
    ax = fig.add_axes([0.03, 0.07, 0.40, 0.40 * 16 / 9 * 0.98])
    th = np.linspace(0, 2 * np.pi, 400)
    ax.fill(np.cos(th), np.sin(th), color="#3a2a12"); ax.plot(np.cos(th), np.sin(th), color=SUN, lw=2.5)
    ax.plot([-1, 1], [0, 0], color=MUT, lw=1.2, ls=":"); ax.plot([0, 0], [-1, 1], color=MUT, lw=1.2, ls=":")
    phi = np.radians(la1); cphi = np.cos(phi)
    ax.plot([-cphi, cphi], [Y1, Y1], color=CYAN, lw=2)                  # the spot's latitude circle, seen edge-on
    ax.plot([0, cphi], [0, Y1], color=MUT, lw=1.5)                      # radius R to the end of that circle
    ax.add_patch(Arc((0, 0), 0.5, 0.5, theta1=0, theta2=la1, color=TXT, lw=1.5))
    ax.plot([0, X1], [Y1, Y1], color=GREEN, lw=3.5); ax.plot([X1, X1], [0, Y1], color=GREEN, lw=3.5)
    ax.plot(X1, Y1, "o", color=RED, ms=14, mec=TXT, mew=1.5, zorder=5)
    note(ax, X1 + 0.05, Y1 - 0.05, "spot A", color=RED, size=17, va="top", fontweight="bold")
    note(ax, X1 / 2, Y1 + 0.03, "X", color=GREEN, size=20, ha="center", va="bottom", fontweight="bold")
    note(ax, X1 - 0.04, Y1 / 2, "Y", color=GREEN, size=20, ha="right", va="center", fontweight="bold")
    note(ax, 0.29 * np.cos(phi / 2), 0.29 * np.sin(phi / 2), "φ", color=TXT, size=20, va="center")
    note(ax, cphi * 0.62, Y1 + 0.03, "R cos φ", color=CYAN, size=17, ha="center", va="bottom")
    note(ax, 0.52, -0.07, "R = 1", color=MUT, size=15, ha="center", va="top")
    ax.set_xlim(-1.08, 1.08); ax.set_ylim(-1.08, 1.08); ax.set_aspect("equal"); ax.axis("off")
    rows = [
        (r"$X = (x - x_c)\,/\,R$", f"({s1.x_px} − {s1.disk_cx_px}) / {s1.disk_r_px} = {num(X1, '+.3f')}"),
        (r"$Y = -(y - y_c)\,/\,R$", f"−({s1.y_px} − {s1.disk_cy_px}) / {s1.disk_r_px} = {num(Y1, '+.3f')}"),
        (r"latitude  $\varphi = \arcsin(Y)$", f"{num(la1, '+.1f')}°"),
        (r"longitude from centre $= \arcsin(X\,/\,\cos\varphi)$", f"{num(c1, '+.1f')}°   …{dt:.2f} days later: {num(c2, '+.1f')}°"),
        ("rate seen from Earth", f"{c2 - c1:.1f}° ÷ {dt:.2f} d = {wsyn:.2f} °/day"),
        (f"+ Earth's orbital motion ({earth:.3f} °/day in December)", f"= {wsid:.2f} °/day  →  one turn in {360 / wsid:.1f} days"),
    ]
    for k, (f_, v_) in enumerate(rows):
        y = 0.76 - k * 0.11
        fig.text(0.47, y, f_, fontsize=21, color=TXT)
        fig.text(0.49, y - 0.045, v_, fontsize=18, color=SUN if k >= 4 else CYAN)
    save(fig, "v06_step2_trigonometry.png")


# ---------------------------------------------------------------- 7. step 2: sine fit
def sine():
    mm = mr.load(WALK); res, fits = mr.analyse(mm)
    fig = canvas("Each spot traces a sine wave — its period is the rotation period",
                 r"x position of spots A and E over a week, fitted with  $x(t) = x_c + R\cos\varphi\,\sin(2\pi(t - t_0)/P)$",
                 "Dots: measured positions. Solid: the side of the Sun facing us. Dotted: the far side (not visible)")
    ax = fig.add_axes([0.075, 0.14, 0.80, 0.66])
    jd0 = 2457000
    tt = np.linspace(-4, 23, 800)
    for k, ((_, r), col) in enumerate(zip(res.iterrows(), [SUN, CYAN])):
        f = fits[r.spot]; T = f["fit"]["P"]; tc = f["fit"]["t0"] + f["t0"] - jd0
        x = f["fit"]["curve"](tt - (f["t0"] - jd0))
        front = np.cos(2 * np.pi * (tt - tc) / T) > 0
        ax.plot(tt, np.where(front, x, np.nan), color=col, lw=3.5)
        ax.plot(tt, np.where(front, np.nan, x), color=col, lw=1.5, ls=":")
        p = mm[mm.spot == r.spot]; ax.plot(p.jd - jd0, p.x_px, "o", color=col, ms=12, mec=TXT, mew=1.5, zorder=5)
        ax.text(0.015, 0.97 - k * 0.075, f"Spot {r.spot} ({hemi(r.lat)}):  P = {T:.1f} d seen from Earth  →  {r.P_sid:.1f} d true rotation",
                transform=ax.transAxes, color=col, fontsize=17, fontweight="bold", va="top")
    xc, R = mm.disk_cx_px.mean(), mm.disk_r_px.mean()
    for v in [xc - R, xc, xc + R]:
        ax.axhline(v, color=MUT, ls="--", lw=1)
    lim = ax.secondary_yaxis("right"); lim.set_yticks([xc - R, xc, xc + R], ["east limb", "disk centre", "west limb"])
    lim.tick_params(colors=MUT, length=0)
    ax.set_xlim(-4, 23); ax.set_ylim(-40, 2400)
    ax.set_xlabel("Julian Date − 2457000"); ax.set_ylabel("x position (pixels)")
    save(fig, "v07_step2_sine_fit.png")


# ---------------------------------------------------------------- 8. step 2: the equation
def equation():
    r = pd.read_csv(D + "rotation_groups.csv")
    r["band"] = pd.cut(r.lat.abs(), np.arange(0, 42.5, 2.5))
    b = r.groupby("band", observed=True).agg(lat=("lat", lambda x: x.abs().mean()), w=("omega", "median"),
                                             sd=("omega", "std"), n=("omega", "size"))
    b = b[b.n >= 20]; s = np.sin(np.radians(b.lat)) ** 2; se = 1.253 * b.sd / np.sqrt(b.n)
    sdo = pd.read_csv(D + "rotation/sdo_spot_results.csv")
    fig = canvas("The Sun's equator spins faster than its higher latitudes",
                 f"Against sin²(latitude), the rotation rates of {len(r):,} sunspot groups (1874–2026) fall on a straight line",
                 f"Sunspot-group positions: D. Hathaway, Greenwich / USAF / NOAA records. Blue: our {len(sdo)} SDO spots (Dec 2014)")
    ax = fig.add_axes([0.075, 0.14, 0.58, 0.60])
    ss = np.linspace(0, 0.45, 50)
    ax.plot(ss, A + B * ss, color=SUN, lw=3.5)
    ax.errorbar(s, b.w, yerr=se, fmt="o", color=TXT, ms=8, capsize=3, label="150 years: median of each 2.5° band")
    ax.scatter(np.sin(np.radians(sdo.lat)) ** 2, sdo.omega, color=CYAN, s=90, zorder=4, label=f"our {len(sdo)} SDO spots")
    ax.set_xlim(0, 0.45); ax.set_ylim(13.2, 15.4)
    ax.set_xlabel("sin²(latitude)"); ax.set_ylabel("rotation rate ω (° per day)")
    top = ax.secondary_xaxis("top", functions=(lambda x: np.degrees(np.arcsin(np.sqrt(np.clip(x, 0, 1)))),
                                               lambda d: np.sin(np.radians(d)) ** 2))
    top.set_xticks([0, 10, 20, 30, 40], ["0°", "10°", "20°", "30°", "40°"]); top.tick_params(colors=MUT)
    ax.text(1.01, 1.02, "latitude", transform=ax.transAxes, color=MUT, fontsize=16, va="bottom")
    ax.legend(loc="lower left")
    v0 = A * np.pi / 180 / 86400 * 695_700
    cards = [("rotation rate", rf"$\omega = {A:.2f} - {-B:.2f}\,\sin^2\!\varphi$", "° per day"),
             ("true rotation period", r"$P = 360\degree\,/\,\omega$", f"{360 / omega(0):.1f} d at the equator, {360 / omega(30):.1f} d at 30°"),
             ("surface speed", rf"$v = {v0:.2f}\,\cos\varphi\,(1 - {-B / A:.3f}\,\sin^2\!\varphi)$", "km/s")]
    for k, (h, eq, sub) in enumerate(cards):
        y0 = 0.70 - k * 0.205
        fig.patches.append(FancyBboxPatch((0.685, y0 - 0.135), 0.28, 0.17, boxstyle="round,pad=0.008",
                                          transform=fig.transFigure, fc=PANEL, ec=GRID))
        fig.text(0.70, y0 + 0.008, h, fontsize=15, color=MUT)
        fig.text(0.70, y0 - 0.055, eq, fontsize=20 if k != 2 else 17, color=SUN)
        fig.text(0.70, y0 - 0.112, sub, fontsize=14, color=TXT)
    save(fig, "v08_step2_equation.png")


# ---------------------------------------------------------------- 9. what the rotation law means
def rotation_meaning():
    wsyn = lambda lat: omega(lat) - 360 / YEAR_DAYS
    fig = canvas("What our rotation law means for a launch team",
                 "The Sun turns once every ~27 days as seen from Earth, so a storm-making region keeps coming back",
                 f"From ω = {A:.2f} − {-B:.2f} sin²φ °/day (true rotation) and Earth's mean orbital motion of 0.986 °/day")
    ax = fig.add_axes([0.03, 0.08, 0.42, 0.42 * 16 / 9 * 0.96])
    th = np.linspace(0, 2 * np.pi, 400)
    cmap = plt.get_cmap("YlOrRd_r")
    for lo, hi in [(0, 10), (10, 20), (20, 30), (30, 40), (40, 90)]:
        for sgn in (1, -1):
            yl, yh = sorted([sgn * np.sin(np.radians(lo)), sgn * np.sin(np.radians(hi))])
            yy = np.linspace(yl, yh, 50); xx = np.sqrt(np.clip(1 - yy**2, 0, None))
            col = cmap(0.15 + 0.17 * [0, 10, 20, 30, 40].index(lo)) if lo < 40 else "#3B4C6E"
            ax.fill_betweenx(yy, -xx, xx, color=col, lw=0)
    ax.plot(np.cos(th), np.sin(th), color=TXT, lw=2)
    for lat in [0, 15, 30]:
        y = np.sin(np.radians(lat)); x = np.cos(np.radians(lat))
        ax.plot([-x, x], [y, y], color=BG, lw=1, alpha=0.6)
        note(ax, x + 0.05, y, f"{lat}°: {360 / omega(lat):.1f} d", size=16, va="center")
    note(ax, 0.67, -0.83, "above 40°: no sunspots", size=13, color=MUT, va="center")
    note(ax, 0.92, 0.66, "true rotation period", size=13, color=MUT, va="center")
    ax.annotate("", (0.55, -0.20), (-0.55, -0.20), arrowprops=dict(arrowstyle="->", color=BG, lw=3))
    note(ax, 0, -0.32, "rotation", color=BG, size=15, ha="center", fontweight="bold")
    note(ax, -1.02, 1.0, "east limb", color=MUT, size=14); note(ax, 0.72, 1.0, "west limb", color=MUT, size=14)
    ax.set_xlim(-1.05, 1.5); ax.set_ylim(-1.08, 1.08); ax.set_aspect("equal"); ax.axis("off")
    facts = [(f"{360 / wsyn(15):.0f} days", "one full turn as seen from Earth\n(a dangerous region comes back)"),
             (f"~{90 / wsyn(15):.0f} days", "from the east limb (where it appears)\nto facing Earth"),
             (f"~{90 / wsyn(15):.0f} days", "from facing Earth to the west limb\n(when its particles reach Earth most easily)"),
             (f"~{180 / wsyn(15):.0f} days", "on the far side, out of sight —\nits flares point away from Earth")]
    for k, (big, small) in enumerate(facts):
        y = 0.74 - k * 0.165
        fig.text(0.50, y, big, fontsize=34, fontweight="bold", color=SUN, va="top")
        fig.text(0.665, y - 0.005, small, fontsize=17, color=TXT, va="top", linespacing=1.3)
    save(fig, "v09_rotation_meaning.png")


# ---------------------------------------------------------------- 10. flares vs sunspots
def flares_ssn():
    lo35, hi35 = np.percentile(ssn35, [10, 90]); med35 = np.median(ssn35)
    fig = canvas("More sunspots, more radio blackouts",
                 "Each dot is one year, 1976–2026: X-class flares (R3+ radio blackouts) against the yearly sunspot number",
                 "Flares: 96,840 NOAA GOES events, true-flux scale (pre-2017 reports ÷ 0.7). " + SRC_SSN)
    ax = fig.add_axes(BODY)
    ax.axvspan(lo35, hi35, color=SUN, alpha=0.15, lw=0)
    ax.axhspan(R3_RATE * lo35, R3_RATE * hi35, color=SUN, alpha=0.15, lw=0)
    xx = np.linspace(0, 240, 10); ax.plot(xx, R3_RATE * xx, color=SUN, lw=3, ls="--")
    ax.scatter(yr.SSN, yr["R3+ (≥X1)"], color=CYAN, s=110, edgecolor=TXT, lw=1, zorder=4)
    for y in [1989, 1991, 2003, 2014, 2024]:
        note(ax, yr.SSN[y] + 3, yr["R3+ (≥X1)"][y] + 2, str(y), size=14, color=MUT)
    note(ax, med35, 95, f"2035 forecast\nsunspot number {med35:.0f}", color=SUN, size=17, ha="center", va="top", fontweight="bold")
    note(ax, 5, R3_RATE * med35 + 2, f"→ about {R3_RATE * med35:.0f} X-class flares in 2035", color=SUN, size=17, fontweight="bold")
    r = np.corrcoef(yr.SSN, yr["R3+ (≥X1)"])[0, 1]
    note(ax, 238, 4, f"{R3_RATE * 100:.0f} X-class flares per year per 100 sunspots  (r = {r:.2f})", color=MUT, size=15, ha="right")
    ax.set_xlim(0, 240); ax.set_ylim(0, 100)
    ax.set_xlabel("Yearly mean sunspot number"); ax.set_ylabel("X-class flares in that year")
    save(fig, "v10_flares_vs_sunspots.png")


# ---------------------------------------------------------------- 11. danger after maximum
MAXES = {21: 1979.96, 22: 1989.87, 23: 2001.87, 24: 2014.29}           # same as flares.py
BOUNDS = [1976.2, 1986.7, 1996.6, 2008.9, 2019.9]


def phase_windows():
    fl = pd.read_csv(D + "flares_1975_2026.csv", parse_dates=["time"])
    fl = fl[fl.flux >= 1e-4]
    dec = fl.time.dt.year + (fl.time.dt.dayofyear - 1) / 365.25
    cyc = pd.cut(dec, BOUNDS, labels=[21, 22, 23, 24]).astype(float)
    dm = dec - cyc.map(MAXES)
    return {lo: ((dm >= lo) & (dm < lo + 1)).sum() / 4 for lo in range(-3, 6)}


def after_max():
    w = phase_windows()
    fig = canvas("Big flares stay frequent for 3 years after maximum",
                 f"X-class flares per year, average of cycles 21–24. Orange years assume the next maximum at {MAX35:.1f}",
                 "Maximum = peak of the 13-month smoothed sunspot number. Flares: NOAA GOES, true-flux scale")
    ax = fig.add_axes([0.075, 0.14, 0.885, 0.62])
    xs = np.array(list(w)) + 0.5; vals = np.array(list(w.values()))
    ax.bar(xs, vals, width=0.8, color=[BLUE if x < 0 else RED for x in xs])
    for x, v in zip(xs, vals):
        note(ax, x, v + 1, f"{v:.0f}", size=17, ha="center")
    ax.axvline(0, color=TXT, ls="--", lw=1.5); note(ax, 0.08, 52, "maximum", size=16)
    box = ("Same distance from maximum, after vs before:\n"
           f"1–2 years:  {w[1] / w[-2]:.1f}× more\n2–3 years:  {w[2] / w[-3]:.1f}× more")
    ax.text(0.985, 0.97, box, transform=ax.transAxes, ha="right", va="top", fontsize=17, color=SUN, linespacing=1.5,
            bbox=dict(boxstyle="round,pad=0.6", fc=PANEL, ec=GRID))
    ax.set_xticks(range(-3, 7), [num(x, "+d") if x else "0" for x in range(-3, 7)])
    ax.set_xlim(-3.3, 6.3); ax.set_ylim(0, 58)
    ax.set_xlabel("Years from solar maximum"); ax.set_ylabel("X-class flares per year")
    top = ax.secondary_xaxis("top", functions=(lambda x: x + MAX35, lambda y: y - MAX35))
    top.set_xticks(range(2033, 2042)); top.tick_params(colors=SUN)
    save(fig, "v11_after_maximum.png")


# ---------------------------------------------------------------- 12. risk calendar
def risk_calendar():
    e = yearly_forecast()
    med = R3_RATE * e.p50; lo = R3_RATE * e.p10; hi = R3_RATE * e.p90
    worst = med[med >= 20].index
    fig = canvas(f"Risk calendar: {worst.min()}–{worst.max()} are the most dangerous years",
                 "Expected X-class flares (R3+ radio blackouts) per year: bars = median forecast, lines = 10–90% range",
                 f"Median of the analogue sunspot forecast × {R3_RATE * 100:.0f} X-class flares per 100 sunspots (one constant rate per sunspot)")
    ax = fig.add_axes(BODY)
    cols = [RED if v >= 20 else SUN if v >= 10 else BLUE for v in med]
    ax.bar(e.index, med, color=cols, width=0.7)
    ax.errorbar(e.index, med, yerr=[med - lo, hi - med], fmt="none", ecolor=TXT, capsize=6, lw=1.5)
    ax.bar([2035], [med[2035]], width=0.7, fill=False, edgecolor=TXT, lw=3)
    note(ax, 2035, hi[2035] + 2, "launch", size=17, ha="center", fontweight="bold")
    for (y, v), c in zip(med.items(), cols):
        ax.text(y, -0.075, f"{v:.0f}", transform=ax.get_xaxis_transform(), ha="center", va="top", fontsize=17,
                color=c, fontweight="bold")
    ax.text(-0.005, -0.075, "median", transform=ax.transAxes, ha="right", va="top", fontsize=15, color=MUT)
    ax.set_xticks(e.index); ax.set_xlim(2029.4, 2041.6); ax.set_ylim(0, max(hi) + 8)
    ax.set_ylabel("X-class flares per year")
    ax.legend(handles=[Patch(color=RED, label="≥ 20 per year"), Patch(color=SUN, label="10–20"), Patch(color=BLUE, label="< 10")],
              loc="upper right")
    save(fig, "v12_risk_calendar.png")


# ---------------------------------------------------------------- 13. 2035 in numbers
def numbers_2035():
    lo, hi = np.percentile(ssn35, [25, 75])
    look = yr[(yr.SSN >= lo) & (yr.SSN <= hi) & (yr.index < 2026)]
    w = phase_windows()
    cards = [(f"{np.median(ssn35):.0f}", f"average sunspot number in 2035\n(10–90%: {np.percentile(ssn35, 10):.0f}–{np.percentile(ssn35, 90):.0f})"),
             (f"≈{R3_RATE * np.median(ssn35):.0f}", "X-class flares → R3+ radio\nblackouts during the year"),
             (f"≈{round(R1_RATE * np.median(ssn35), -1):.0f}", "M-class or stronger flares →\nR1+ radio blackouts"),
             (f"{(look['R3+ (≥X1)'] > 0).sum()} of {len(look)}", "past years this active had\nat least one R3 blackout"),
             (f"{(look['R4+ (≥X10)'] > 0).sum()} of {len(look)}", "of those years also had an\nextreme R4 flare (≥ X10)"),
             (f"{w[1] / w[-2]:.1f}×", "more X-class flares 1–2 years after\nmaximum than 1–2 years before")]
    fig = canvas("2035 in numbers", "What our forecast says about the launch year (NOAA true-flux scale)",
                 "Forecast: historical-analogue ensemble; flare rates: NOAA GOES 1976–2026; comparable years: sunspot number "
                 f"{lo:.0f}–{hi:.0f}")
    for k, (big, small) in enumerate(cards):
        cx, cy = 0.05 + (k % 3) * 0.31, 0.47 - (k // 3) * 0.36
        fig.patches.append(FancyBboxPatch((cx, cy), 0.28, 0.30, boxstyle="round,pad=0.01", transform=fig.transFigure, fc=PANEL, ec=GRID))
        fig.text(cx + 0.02, cy + 0.265, big, fontsize=52, fontweight="bold", color=[SUN, RED, RED, SUN, RED, SUN][k], va="top")
        fig.text(cx + 0.02, cy + 0.125, small, fontsize=18, color=TXT, va="top", linespacing=1.35)
    save(fig, "v13_2035_in_numbers.png")


# ---------------------------------------------------------------- 14. geomagnetic storms around maximum
def storms_after_max():
    ph = pd.read_csv(D + "geomagnetic_phase.csv", index_col=0)
    gs = json.load(open(D + "geomagnetic_summary.json"))
    fig = canvas("Geomagnetic storms peak 1–3 years after maximum",
                 f"Storm days per year, average of cycles 17–24 (Kp index since 1932). Orange years assume the next maximum at {MAX35:.1f}",
                 "Kp: GFZ Potsdam (Matzka et al. 2021). Storm levels: NOAA G-scale (G1 minor … G5 extreme)")
    panels = [("G1+", SUN, "Minor or stronger (G1+): the level of the\nFeb 2022 storm that downed 38 Starlink satellites",
               f"≈{gs['y2035_G1+'][1]:.0f} storm days in 2035:\nabout 1 day in {365.25 / gs['y2035_G1+'][1]:.0f}"),
              ("G3+", RED, "Strong or stronger (G3+)",
               f"{gs['after_before_G3+']:.1f}× more storm days 1–3 years\nafter maximum than 1–3 years before")]
    for k, (g, col, head, msg) in enumerate(panels):
        ax = fig.add_axes([0.075 + k * 0.475, 0.14, 0.41, 0.58])
        xs = ph.index + 0.5
        ax.bar(xs, ph[g], width=0.8, color=col)
        for x, v in zip(xs, ph[g]):
            note(ax, x, v + ph[g].max() * 0.02, f"{v:.0f}", size=14, ha="center")
        ax.plot([0, 0], [0, ph[g].max() * 1.12], color=TXT, ls="--", lw=1.5)
        ax.set_xticks(range(-3, 7), [num(x, "+d") if x else "0" for x in range(-3, 7)])
        ax.set_xlim(-3.3, 6.3); ax.set_ylim(0, ph[g].max() * 1.75)
        ax.set_xlabel("Years from solar maximum")
        if k == 0:
            ax.set_ylabel("Storm days per year")
        ax.text(0.02, 0.97, head, transform=ax.transAxes, va="top", fontsize=16, color=col, fontweight="bold", linespacing=1.3)
        ax.text(0.02, 0.80, msg, transform=ax.transAxes, va="top", fontsize=15, color=TXT, linespacing=1.3)
        top = ax.secondary_xaxis("top", functions=(lambda x: x + MAX35, lambda y: y - MAX35))
        top.set_xticks(range(2033, 2042, 2)); top.tick_params(colors=SUN)
    save(fig, "v14_storms_after_maximum.png")


# ---------------------------------------------------------------- 15. a LEO constellation in 2035
def leo_2035():
    gs = json.load(open(D + "geomagnetic_summary.json"))
    g1, g3 = gs["y2035_G1+"][1], gs["y2035_G3+"][1]
    cards = [(f"≈{g1:.0f}", SUN, f"G1+ storm days in 2035:\nabout 1 day in {365.25 / g1:.0f}"),
             (f"≈{g3:.0f}", RED, "strong (G3+) storm days\nin 2035"),
             (f"{gs['look_G4_years']} of {gs['look_n']}", RED, "past years this active had a\nsevere (G4+) storm"),
             (f"{gs['look_G5_years']} of {gs['look_n']}", RED, "had an extreme (G5) storm,\nlike May 2024"),
             (f"{gs['free3_G1'] * 100:.0f}%", SUN, "of 3-day stretches had no\nstorm: deploy in those"),
             (f"{gs['after_before_G3+']:.1f}×", SUN, "more strong-storm days 1–3 yr\nafter maximum than before")]
    fig = canvas("A Starlink-like constellation in 2035",
                 "What our forecast says about geomagnetic storms, the main space-weather threat in low Earth orbit",
                 f"Kp index 1932–2026 (GFZ Potsdam); forecast: historical-analogue ensemble; comparable years: "
                 f"sunspot number {gs['look_ssn'][0]:.0f}–{gs['look_ssn'][1]:.0f}")
    for k, (big, col, small) in enumerate(cards):
        cx, cy = 0.05 + (k % 3) * 0.31, 0.47 - (k // 3) * 0.36
        fig.patches.append(FancyBboxPatch((cx, cy), 0.28, 0.30, boxstyle="round,pad=0.01", transform=fig.transFigure, fc=PANEL, ec=GRID))
        fig.text(cx + 0.02, cy + 0.265, big, fontsize=52, fontweight="bold", color=col, va="top")
        fig.text(cx + 0.02, cy + 0.125, small, fontsize=18, color=TXT, va="top", linespacing=1.35)
    save(fig, "v15_leo_2035_in_numbers.png")


if __name__ == "__main__":
    for f in [cover, incidents, butterfly, forecast, measure, trig, sine, equation, rotation_meaning,
              flares_ssn, after_max, risk_calendar, numbers_2035, storms_after_max, leo_2035]:
        f()
