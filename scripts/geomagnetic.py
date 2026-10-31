"""Geomagnetic storms (NOAA G-scale) 1932-2026 from the Kp index: link to sunspots, timing in the cycle, 2035 outlook.

Why: for a Starlink-like constellation in low Earth orbit the main space-weather threat is a geomagnetic storm,
which heats and expands the upper atmosphere and raises the drag on the satellites (February 2022: 38 of 49
new Starlink satellites lost in a minor storm).

Kp: GFZ Potsdam (Matzka et al. 2021), one value per 3 hours, in thirds (5- = 4.667, 5o = 5.000, 5+ = 5.333).
NOAA G-scale: G1 Kp 5, G2 Kp 6, G3 Kp 7, G4 Kp 8 including 9-, G5 Kp 9. An integer Kp level N covers N-, No
and N+, so G1 starts at 5- (4.667) and G5 is 9o only; with this convention the storm days per cycle match
NOAA's published averages (checked below). A storm day is a UT day whose highest Kp reaches the level; a
storm is a run of consecutive storm days.
"""
import json, numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from paths import D, F
from kp_index import load_kp

LEVELS = {"G1+": 4.667, "G2+": 5.667, "G3+": 6.667, "G4+": 7.667, "G5": 9.0}
NOAA_DAYS = {"G1+": 900, "G2+": 360, "G3+": 130, "G4+": 60, "G5": 4}   # NOAA scale table, storm days per cycle

# ---------- daily maximum Kp ----------
k = load_kp()
k = k[k.kp >= 0].reset_index(drop=True)
for g, thr in LEVELS.items():
    k[g] = k.kp >= thr - 0.01
last = k.date.max()
print(f"Kp: {len(k)} days, {k.date.min():%Y-%m-%d} to {last:%Y-%m-%d} "
      f"({(k.flag == 2).mean() * 100:.1f}% definitive, the rest preliminary)")

# ---------- check the convention against NOAA's table (complete cycles 17-24) ----------
cyc = pd.read_csv(D + "cycles_table.csv").set_index("cycle")
dec = k.Y + (k.date.dt.dayofyear - 0.5) / 365.25
k["cycle"] = pd.cut(dec, list(cyc.start.loc[17:25]) + [2100], labels=range(17, 26), right=False).astype(float)
k["from_max"] = dec - k.cycle.map(cyc.max_time)
full = k.cycle.between(17, 24)
print(f"\nStorm days per cycle, cycles 17-24 ({cyc.start.loc[17]}-{cyc.start.loc[25]}), vs NOAA's published averages:")
for g in LEVELS:
    print(f"   {g:4s}: {k.loc[full, g].sum() / 8:5.0f}   (NOAA: {NOAA_DAYS[g]})")

# ---------- storms (runs of consecutive storm days) ----------
def storms(level):
    run = (k[level] != k[level].shift()).cumsum()
    s = k[k[level]].groupby(run[k[level]]).agg(start=("date", "first"), days=("date", "size"), kp_max=("kp", "max"))
    s["level"] = [next(g for g, t in reversed(LEVELS.items()) if kp >= t - 0.01) for kp in s.kp_max]
    return s.reset_index(drop=True)

st = {g: storms(g) for g in ["G3+", "G4+", "G5"]}
st["G3+"].to_csv(D + "geomagnetic_storms_g3.csv", index=False)      # every G3+ storm, with its strongest level

# ---------- yearly counts (the current year scaled to a full year) ----------
sn = pd.read_csv(D + "SN_m_tot_V2.0.csv", sep=";", header=None, names=["y", "m", "t", "ssn", "sd", "n", "p"])
yr = k.groupby("Y")[list(LEVELS)].sum().astype(float)
for g, s_ in st.items():
    yr[f"{g} storms"] = s_.groupby(s_.start.dt.year).size().reindex(yr.index, fill_value=0)
frac = last.dayofyear / (366 if last.is_leap_year else 365)
yr.loc[last.year] = (yr.loc[last.year] / frac).round()
yr = yr.astype(int)
yr["SSN"] = sn.groupby("y").ssn.mean().reindex(yr.index).round(1)
yr.index.name = "year"
yr.to_csv(D + "geomagnetic_per_year.csv")
print(f"\nStorm days per year by G level ({last.year} scaled to a full year from {last:%d %b}):")
print(yr.to_string())

# ---------- relation to sunspot number (complete years) ----------
fy = yr.loc[:last.year - 1]
print(f"\nStorm days per year against the yearly sunspot number ({fy.index[0]}-{fy.index[-1]}),"
      " straight line a + b·SSN (storms also happen near minimum, so the line is not forced through 0):")
fits = {}
for g in list(LEVELS) + [f"{g} storms" for g in st]:
    b, a = np.polyfit(fy.SSN, fy[g], 1)
    fits[g] = (a, b)
    print(f"   {g:10s}: r = {np.corrcoef(fy.SSN, fy[g])[0, 1]:.2f},  {a:5.1f} + {b * 100:5.2f} per 100 SSN")

# ---------- 2035 outlook ----------
ssn35 = pd.read_csv(D + "forecast_v2_ssn2035_samples.csv").ssn_2035.values
print(f"\n2035 outlook (SSN 10/50/90 percentile = {np.percentile(ssn35, [10, 50, 90]).round(0)}), per year:")
for g, (a, b) in fits.items():
    lam = a + b * ssn35
    print(f"   {g:10s}: {np.percentile(lam, 10):5.1f} / {np.median(lam):5.1f} / {np.percentile(lam, 90):5.1f}")
lo, hi = np.percentile(ssn35, [25, 75])
look = fy[(fy.SSN >= lo) & (fy.SSN <= hi)]
print(f"   Real years as active as 2035 (SSN {lo:.0f}-{hi:.0f}, {len(look)} years: {', '.join(map(str, look.index))}):")
print(f"      mean {look['G1+'].mean():.0f} G1+ days and {look['G3+'].mean():.0f} G3+ days per year; at least one G4+ day in "
      f"{(look['G4+'] > 0).sum()} of {len(look)} years, at least one G5 day in {(look['G5'] > 0).sum()} of {len(look)}")
g1_share = np.median(fits["G1+"][0] + fits["G1+"][1] * ssn35) / 365.25
print(f"   A G1 storm or stronger (Kp 5+ on 3-4 Feb 2022, when the Starlink satellites were lost, was G1) is expected"
      f" on about {g1_share * 100:.0f}% of days in 2035, i.e. about once every {1 / g1_share:.0f} days")
# Storms cluster, so count storm-free stretches directly in the real look-alike years
print("   Share of n-day stretches with no storm at all, in those real years:")
summary = {}
for n in (3, 5, 7):
    pooled = {g: np.concatenate([(k.loc[k.Y == y, g].astype(int).rolling(n).max().dropna() == 0).values for y in look.index]).mean()
              for g in ["G1+", "G3+"]}
    print(f"      {n} days: no G1+ storm {pooled['G1+'] * 100:.0f}%, no G3+ storm {pooled['G3+'] * 100:.0f}%")
    summary |= {f"free{n}_G1": pooled["G1+"], f"free{n}_G3": pooled["G3+"]}

# ---------- timing within the cycle ----------
print("\nStorm days per year in 1-year windows around cycle maximum (average of cycles 17-24;"
      " windows that leave a cycle are not counted for it):")
win = {}
for lo_ in range(-3, 6):
    ok = [c for c in range(17, 25) if cyc.start.loc[c] <= cyc.max_time.loc[c] + lo_ and cyc.max_time.loc[c] + lo_ + 1 <= cyc.start.loc[c + 1]]
    sel = full & k.cycle.isin(ok) & (k.from_max >= lo_) & (k.from_max < lo_ + 1)
    win[lo_] = {g: k.loc[sel, g].sum() / len(ok) for g in ["G1+", "G3+", "G4+"]} | {"cycles": len(ok)}
w = pd.DataFrame(win).T
w.rename_axis("years_from_max").to_csv(D + "geomagnetic_phase.csv")
w.index = [f"{i:+d} to {i + 1:+d}" for i in w.index]
print(w.round(1).to_string())
for g in ["G1+", "G3+"]:
    v = pd.DataFrame(win).T[g]
    summary[f"after_before_{g}"] = (v[1] + v[2]) / (v[-3] + v[-2])
    print(f"   {g}: 1-3 yr after max {v[1] + v[2]:.0f} days vs 1-3 yr before {v[-3] + v[-2]:.0f} days "
          f"({(v[1] + v[2]) / (v[-3] + v[-2]):.1f}x); peak window {v.idxmax():+d} to {v.idxmax() + 1:+d} yr")

# ---------- satellite lifetime 2035-2044 ----------
ens = pd.read_csv(D + "forecast_v2_ensemble.csv").dropna()
ssn_y = ens.assign(yy=ens.year.astype(int)).groupby("yy").p50.mean().loc[2035:2044]
print("\nA satellite working 2035-2044 (median forecast sunspot number each year):")
for g in ["G1+", "G3+", "G4+", "G5", "G3+ storms", "G4+ storms", "G5 storms"]:
    a, b = fits[g]
    tot = np.clip(a + b * ssn_y, 0, None).sum()
    summary[f"life_{g.replace(' ', '_')}"] = tot
    extra = f"  (at least one: {1 - np.exp(-tot):.0%})" if "storms" in g and tot < 10 else ""
    print(f"   {g:10s}: about {tot:5.1f} in 10 years{extra}")

for g, (a, b) in fits.items():
    lam = a + b * ssn35
    summary[f"y2035_{g.replace(' ', '_')}"] = [np.percentile(lam, 10), np.median(lam), np.percentile(lam, 90)]
summary |= dict(look_n=len(look), look_ssn=[lo, hi], look_G1_mean=look["G1+"].mean(), look_G3_mean=look["G3+"].mean(),
                look_G4_years=int((look["G4+"] > 0).sum()), look_G5_years=int((look["G5"] > 0).sum()),
                noaa_check={g: [k.loc[full, g].sum() / 8, NOAA_DAYS[g]] for g in LEVELS})
json.dump(summary, open(D + "geomagnetic_summary.json", "w"), indent=1, default=float)

# ---------- known events ----------
print("\nKnown events (daily maximum Kp, G level):")
for day, what in [("1989-03-13", "Quebec blackout"), ("2003-10-29", "Halloween storms"), ("2022-02-03", "Starlink launch"),
                  ("2022-02-04", "Starlink losses"), ("2024-05-11", "Gannon storm")]:
    kp = k.loc[k.date == day, "kp"].iloc[0]
    lev = next((g for g, t in reversed(LEVELS.items()) if kp >= t - 0.01), "below G1")
    print(f"   {day} {what:17s}: Kp {kp:.3f}  -> {lev.rstrip('+')}")

# ---------- figure ----------
fig, (a1, a2, a3) = plt.subplots(1, 3, figsize=(17, 5), gridspec_kw=dict(width_ratios=[1.5, 1, 1]))
a1.bar(yr.index, yr["G1+"], color="tab:orange", alpha=0.45, label="G1+ storm days")
a1.bar(yr.index, yr["G3+"], color="tab:red", label="G3+ storm days")
a1.set_ylabel("Storm days per year"); a1.set_xlabel("Year")
t = a1.twinx(); t.plot(yr.index, yr.SSN, c="k", lw=1.5, label="Yearly mean sunspot number"); t.set_ylabel("Sunspot number")
t.set_ylim(0, 300); a1.set_ylim(0, 230)
h1, l1 = a1.get_legend_handles_labels(); h2, l2 = t.get_legend_handles_labels()
a1.legend(h1 + h2, l1 + l2, loc="upper left", fontsize=9, ncol=3)
a1.set_title(f"Geomagnetic storm days from the Kp index, 1932–{last.year} ({last.year} scaled)", fontsize=11)
xx = np.linspace(0, 260, 10); a_, b_ = fits["G3+"]
a2.scatter(fy.SSN, fy["G3+"], c="tab:red", s=20)
a2.plot(xx, a_ + b_ * xx, c="tab:red", ls="--", label=f"{a_:.1f} + {b_ * 100:.1f} per 100 SSN")
a2.axvspan(*np.percentile(ssn35, [10, 90]), color="tab:orange", alpha=0.2, label="2035 forecast (10–90%)")
for y in [1989, 1991, 2003, 2024]:
    if y in fy.index:
        a2.annotate(str(y), (fy.SSN[y], fy["G3+"][y]), xytext=(4, 4), textcoords="offset points", fontsize=8)
a2.set_xlabel("Yearly mean sunspot number"); a2.set_ylabel("G3+ storm days in that year")
a2.set_title(f"G3+ storm days vs sunspots (r = {np.corrcoef(fy.SSN, fy['G3+'])[0, 1]:.2f})", fontsize=11); a2.legend(fontsize=8)
wd = pd.DataFrame(win).T
a3.bar(wd.index + 0.5, wd["G1+"], width=0.8, color="tab:orange", alpha=0.45, label="G1+ storm days")
a3.bar(wd.index + 0.5, wd["G3+"], width=0.8, color="tab:red", label="G3+ storm days")
a3.axvline(0, c="k", ls=":"); a3.set_xlabel("Years from cycle maximum"); a3.set_ylabel("Storm days per year (cycles 17–24)")
a3.set_title("Storms stay frequent for years after maximum", fontsize=11); a3.legend(fontsize=8)
plt.tight_layout(); plt.savefig(F + "geomagnetic_storms.png", dpi=150)
