"""Our own butterfly diagram, built from the latitude of every sunspot group, and what it tells us:
the cycle period and when the next maximum is likely.

Cycle start, read off the diagram: an old cycle ends with its spots near the equator, the new one
begins with spots at high latitude. We call the start of a cycle the moment when more than half
of the sunspot area (1-year running total) sits at |latitude| >= 15°, after a stretch in which
almost all of it was below 15°. Maximum: when the total sunspot area (1-year running mean) peaks.
"""
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sunspot_groups import load_groups

from paths import D, F
SPLIT = 15            # latitude separating "high" (new cycle) from "low" (old cycle) spots
CR_DAYS = 27.2753     # one Carrington rotation
T0 = pd.Timestamp("1853-11-09")
SILSO_MIN = [1878.9, 1889.6, 1902.0, 1913.6, 1923.6, 1933.7, 1944.1, 1954.3, 1964.8, 1976.2, 1986.7, 1996.6, 2008.9, 2019.9]

g = load_groups()
g["cr"] = ((g.time - T0).dt.total_seconds() / 86400 // CR_DAYS).astype(int) + 1
g["hi"] = np.where(g.lat.abs() >= SPLIT, g.area, 0.0)
cr = g.groupby("cr").agg(tot=("area", "sum"), hi=("hi", "sum"), n=("area", "size"))
cr = cr.reindex(range(cr.index.min(), cr.index.max() + 1), fill_value=0)
mid = T0 + pd.to_timedelta((cr.index - 0.5) * CR_DAYS, unit="D")
cr["year"] = mid.year + (mid.dayofyear - 0.5) / 365.25
year_sum = cr[["tot", "hi"]].rolling(13, center=True, min_periods=7).sum()   # 13 rotations ≈ 1 year
cr["f_high"] = year_sum.hi / year_sum.tot
cr["area"] = (cr.tot / CR_DAYS).rolling(13, center=True, min_periods=7).mean()     # mean daily area

# ---------- cycle starts: upward crossing of 50%, after the fraction had dropped below 0.3 ----------
# (and at least 7 years after the previous start: no cycle has ever been shorter than 9 years)
starts = []
for i in cr.index[1:]:
    if cr.f_high[i - 1] < 0.5 <= cr.f_high[i] and cr.f_high.loc[i - 30:i].min() < 0.3:
        if not starts or cr.year[i] - starts[-1] > 7:
            starts.append(cr.year[i])
starts = np.array(starts)
# ---------- maxima: peak of the 1-year mean sunspot area between two starts ----------
maxima = []
for a, b in zip(starts, list(starts[1:]) + [cr.year.max()]):
    seg = cr[(cr.year > a) & (cr.year < b)].dropna(subset=["area"])
    k = seg.area.idxmax(); maxima.append((seg.year[k], seg.area[k]))
res = pd.DataFrame(dict(start=starts, max_year=[m[0] for m in maxima], max_area=[m[1] for m in maxima]))
res["period"] = res.start.shift(-1) - res.start
res["rise"] = res.max_year - res.start
res["silso_min"] = [min(SILSO_MIN, key=lambda s: abs(s - x)) for x in res.start]
res.index = [f"cycle {c}" for c in range(25 - len(res) + 1, 26)]
print("Cycles read off our butterfly diagram (1874-2026):")
print(res.round(2).to_string())
print(f"\nStart vs official (SILSO) minimum: mean difference {np.mean(res.start - res.silso_min):+.2f} yr, "
      f"largest {np.max(np.abs(res.start - res.silso_min)):.2f} yr")

# ---------- the two most recent cycles ----------
c24, c25 = res.loc["cycle 24"], res.loc["cycle 25"]
P = c24.period; rise = np.mean([c24.rise, c25.rise])
print(f"\nTwo most recent cycles:")
print(f"   cycle 24 starts {c24.start:.2f}, maximum {c24.max_year:.2f} (rise {c24.rise:.2f} yr), length {P:.2f} yr")
print(f"   cycle 25 starts {c25.start:.2f}, maximum {c25.max_year:.2f} (rise {c25.rise:.2f} yr)")
print(f"   -> cycle 26 starts ≈ {c25.start:.2f} + {P:.2f} = {c25.start + P:.1f}; "
      f"maximum ≈ {c25.start + P:.1f} + {rise:.2f} = {c25.start + P + rise:.1f}")
full = res.dropna(subset=["period"])
Pm, Ps, Rm, Rs = full.period.mean(), full.period.std(), res.rise.mean(), res.rise.std()
print(f"   with all {len(full)} complete cycles: period {Pm:.2f} ± {Ps:.2f} yr, rise {Rm:.2f} ± {Rs:.2f} yr "
      f"-> cycle 26 maximum ≈ {c25.start + Pm + Rm:.1f} ± {np.hypot(Ps, Rs):.1f}")
lat_at_max = []
for _, r in res.iterrows():
    s = g[(g.time.dt.year + g.time.dt.dayofyear / 365.25 - r.max_year).abs() < 0.5]
    lat_at_max.append(np.average(s.lat.abs(), weights=s.area + 1e-9))
print(f"   mean latitude of spots at maximum: {np.mean(lat_at_max):.1f}° ± {np.std(lat_at_max):.1f}° "
      f"(cycle 24: {lat_at_max[-2]:.1f}°, cycle 25: {lat_at_max[-1]:.1f}°)")
res.to_csv(D + "butterfly_cycles.csv")
pred_start, pred_max = c25.start + P, c25.start + P + rise                 # from cycles 24-25 only
all_max, all_err = c25.start + Pm + Rm, np.hypot(Ps, Rs)                   # from all complete cycles

# ---------- figure ----------
sel = g[g.time >= "2006-01-01"].sort_values(["gid", "time"])
new = (sel.gid != sel.gid.shift()) | ((sel.time - sel.time.shift()).dt.days > 3)
sel = sel.assign(passage=new.cumsum())
pas = sel.groupby("passage").agg(time=("time", "mean"), lat=("lat", "mean"), area=("area", "max"))
pas["year"] = pas.time.dt.year + (pas.time.dt.dayofyear - 0.5) / 365.25
fig, (a1, a2, a3) = plt.subplots(3, 1, figsize=(13, 10), sharex=True, gridspec_kw=dict(height_ratios=[3, 1.2, 1.4]))
a1.scatter(pas.year, pas.lat, s=np.sqrt(pas.area) * 0.8, c=np.where(pas.lat > 0, "tab:red", "tab:blue"),
           alpha=0.35, lw=0)
for y in (SPLIT, -SPLIT): a1.axhline(y, c="0.4", ls=":", lw=1)
a1.text(2006.2, SPLIT + 1, f"{SPLIT}°", fontsize=8, color="0.3")
a1.set_ylim(-45, 45); a1.set_ylabel("Latitude (°)")
a1.set_title(f"Our butterfly diagram: {len(pas):,} sunspot groups 2006–2026 (one dot per disk passage, size = area)")
for ax in (a1, a2, a3):
    for s, lab in [(c24.start, "cycle 24 starts"), (c25.start, "cycle 25 starts")]:
        ax.axvline(s, c="k", ls="--", lw=1)
    ax.axvline(pred_start, c="tab:orange", ls="--", lw=1.5)
    ax.axvspan(all_max - all_err, all_max + all_err, color="0.5", alpha=0.15)
    ax.axvline(pred_max, c="tab:orange", lw=2)
a1.text(c24.start + 0.2, 40, f"cycle 24 starts\n{c24.start:.1f}", fontsize=9)
a1.text(c25.start + 0.2, 40, f"cycle 25 starts\n{c25.start:.1f}", fontsize=9)
a1.text(pred_start - 3.3, 40, f"cycle 26 starts\n≈ {pred_start:.1f}", fontsize=9, color="tab:orange")
a1.text(pred_max + 0.2, -36, f"cycle 26 maximum\n≈ {pred_max:.1f}\n(from cycles 24–25)", fontsize=9, color="tab:orange")
a1.text(all_max - all_err + 0.1, -44, f"grey: {all_max:.1f} ± {all_err:.1f}\n(all {len(full)} cycles)", fontsize=8, color="0.3")
sub = cr[cr.year >= 2006]
a2.plot(sub.year, sub.f_high, c="k")
a2.axhline(0.5, c="0.5", ls=":"); a2.set_ylim(0, 1)
a2.set_ylabel(f"share of area\nat |lat| ≥ {SPLIT}°")
a2.set_title("New cycle = high-latitude spots take over (share crosses 0.5 upward)", fontsize=10)
a3.plot(sub.year, sub.area, c="tab:red")
for _, r in res[res.start > 2000].iterrows():
    a3.plot(r.max_year, r.max_area, "v", c="tab:red", ms=9)
    a3.text(r.max_year + 0.2, r.max_area, f"maximum {r.max_year:.1f}", fontsize=9)
a3.set_ylabel("sunspot area\n(millionths of a\nhemisphere, 1-yr mean)"); a3.set_xlabel("Year")
a3.set_title(f"Period {c24.start:.1f} → {c25.start:.1f} = {P:.1f} yr; rise to maximum ≈ {rise:.1f} yr "
             f"→ next maximum ≈ {pred_max:.1f}  (all {len(full)} cycles since {int(res.start.iloc[0])}: {all_max:.1f} ± {all_err:.1f})",
             fontsize=10)
a3.set_xlim(2006, 2041)
plt.tight_layout(); plt.savefig(F + "butterfly_own.png", dpi=140)
