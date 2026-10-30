"""NOAA GOES X-ray flares 1975-2026 vs sunspot number; radio-blackout (R-scale) check and 2035 outlook.

Calibration: GOES 1-15 (to 2016) fluxes were officially scaled by 0.7 by NOAA SWPC.
GOES-16/19 science data are true fluxes. We divide the old fluxes by 0.7 so the whole
record is on today's NOAA scale (the one used for current R-scale alerts).
"""
import glob, re, numpy as np, pandas as pd, xarray as xr, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

D = "/home/user/planethack/data/"; F = "/home/user/planethack/figures/"
BASE = dict(A=1e-8, B=1e-7, C=1e-6, M=1e-5, X=1e-4)

# ---------- legacy text reports 1975 - 2017-02-08 ----------
rec = []
for f in sorted(glob.glob(D+"flares/goes-xrs-report_*.txt")):
    if "modified" in f: continue
    for line in open(f, errors="ignore"):
        m = re.match(r"31777(\d{6})", line)
        if not m or not line[23:27].strip().isdigit(): continue
        yy, mo, dd = int(m[1][:2]), int(m[1][2:4]), int(m[1][4:])
        if 75 <= yy < 80:   # 1970s reports give whole-number magnitudes ("M 1" = M1)
            c = re.search(r"([ABCMX]) +(\d{1,2})\s", line[58:66]); mag = int(c[2]) if c else 0
        else:               # later reports: "X 15" = X1.5, "X172" = X17.2
            c = re.search(r"([ABCMX])([ \d]\d\d)", line[58:64]); mag = int(c[2]) / 10 if c else 0
        if not c: continue
        t = pd.Timestamp(year=(1900 if yy >= 75 else 2000)+yy, month=mo, day=dd,
                         hour=int(line[23:25]) % 24, minute=int(line[25:27]) % 60)
        rec.append((t, BASE[c[1]] * mag, "legacy"))
old = pd.DataFrame(rec, columns=["time", "flux_old", "src"]).drop_duplicates("time")
old["time"] = old.time.astype("datetime64[ns]")

# ---------- GOES-16 (2017-02-09 .. 2025-04-07) and GOES-19 (2025-04-08 ..) science data ----------
def peaks(files):
    d = pd.concat([xr.open_dataset(f).to_dataframe().reset_index() for f in files])
    d = d[d.status == "EVENT_PEAK"]
    d = d[["time", "xrsb_flux"]].rename(columns={"xrsb_flux": "flux"})
    return d.assign(time=d.time.astype("datetime64[ns]"), flux=d.flux.astype(float))
g16 = peaks([D+"flares/sci_xrsf-l2-flsum_g16_s20170209_e20250407_v2-2-2.nc"]); g16["src"] = "GOES-16"
g19 = peaks(sorted(glob.glob(D+"flares/g19/*.nc"))); g19["src"] = "GOES-19"
g16 = g16[g16.time < "2025-04-08"]; g19 = g19[g19.time >= "2025-04-08"]

# ---------- check the 0.7 calibration with flares seen by both (Feb-Jun 2017) ----------
ov = pd.merge_asof(g16[g16.flux >= 1e-6].sort_values("time"), old.sort_values("time"),
                   on="time", tolerance=pd.Timedelta("4min"), direction="nearest").dropna()
ratio = (ov.flux_old / ov.flux).median()
print(f"Calibration check: {len(ov)} C-class+ flares seen in both datasets, "
      f"median old/new flux ratio = {ratio:.2f} (NOAA official: 0.70)")

old = old[old.time < "2017-02-09"].assign(flux=lambda x: x.flux_old / 0.7)
fl = pd.concat([old[["time", "flux", "src"]], g16, g19]).sort_values("time").reset_index(drop=True)
fl["year"] = fl.time.dt.year
def cls(f):
    for L in "XMCBA":
        if f >= BASE[L]: return f"{L}{f/BASE[L]:.1f}"
    return "A0"
fl["class"] = fl.flux.map(cls)
fl.to_csv(D+"flares_1975_2026.csv", index=False)
print(f"Total flares: {len(fl)}  ({fl.time.min():%Y-%m} to {fl.time.max():%Y-%m})")

# ---------- yearly counts per NOAA radio-blackout level ----------
R = {"R1+ (≥M1)": 1e-5, "R2+ (≥M5)": 5e-5, "R3+ (≥X1)": 1e-4, "R4+ (≥X10)": 1e-3}
yr = pd.DataFrame({k: fl[fl.flux >= v].groupby("year").size() for k, v in R.items()}).fillna(0).astype(int)
sn = pd.read_csv(D+"SN_m_tot_V2.0.csv", sep=";", header=None, names=["y","m","t","ssn","sd","n","p"])
yr["SSN"] = sn.groupby("y").ssn.mean().reindex(yr.index).round(1)
yr = yr.loc[1976:2026]          # 1975: GOES record starts part-way through the year
yr.loc[2026, yr.columns[:4]] = (yr.loc[2026, yr.columns[:4]] * 12 / 10).round()   # Jan-Oct -> full-year estimate
yr.to_csv(D+"flares_per_year.csv")
print("\nFlares per year by radio-blackout level (2026 scaled to a full year):")
print(yr.to_string())

# ---------- relation to sunspot number ----------
print("\nCorrelation with yearly sunspot number:")
fits = {}
for k in R:
    rr = np.corrcoef(yr.SSN, yr[k])[0, 1]
    rate = yr[k].sum() / yr.SSN.sum()          # flares per year per unit SSN (line through 0)
    fits[k] = rate
    print(f"   {k:11s}: r = {rr:.2f}, about {rate*100:.2f} flares/yr per 100 SSN")

# ---------- 2035 outlook using the v2 ensemble ----------
ssn35 = pd.read_csv(D+"forecast_v2_ssn2035_samples.csv").ssn_2035.values
print(f"\n2035 outlook (SSN 10/50/90 percentile = {np.percentile(ssn35,[10,50,90]).round(0)}):")
for k, rate in fits.items():
    lam = rate * ssn35
    print(f"   {k:11s}: expected {np.percentile(lam,10):5.0f} / {np.median(lam):5.0f} / {np.percentile(lam,90):5.0f} per year")
# Big flares come in bursts from a few monster regions (e.g. June 1991, Oct-Nov 2003), so a
# Poisson estimate is too optimistic about "at least one". Use the real years instead.
act = yr[yr.SSN >= 100]
print(f"   Real years with SSN >= 100 ({len(act)} years): at least one R3+ event in "
      f"{(act['R3+ (≥X1)'] > 0).mean()*100:.0f}%, at least one R4+ event in {(act['R4+ (≥X10)'] > 0).mean()*100:.0f}%")
print(f"   R4+ years: {', '.join(map(str, act.index[act['R4+ (≥X10)'] > 0]))}")

# ---------- when do the biggest flares happen? (position in the cycle) ----------
MAX = {21: 1979.96, 22: 1989.87, 23: 2001.87, 24: 2014.29, 25: 2024.79}
dec = fl.time.dt.year + (fl.time.dt.dayofyear - 1) / 365.25
fl["cycle"] = pd.cut(dec, [1976.2, 1986.7, 1996.6, 2008.9, 2019.9, 2031], labels=[21, 22, 23, 24, 25]).astype(float)
fl["from_max"] = dec - fl.cycle.map(MAX)
big = fl[fl.flux >= 1e-4].dropna(subset=["cycle"])
print("\nX-class flares (R3+) by position relative to cycle maximum:")
for lo, hi, lab in [(-99, -1, "rising phase (>1 yr before max)"), (-1, 1, "within ±1 yr of max"),
                    (1, 3, "1-3 yr after max"), (3, 99, ">3 yr after max")]:
    n = ((big.from_max >= lo) & (big.from_max < hi)).sum()
    print(f"   {lab:32s}: {n:4d} ({n/len(big)*100:.0f}%)")
print(f"   within ±2 yr of max: {(big.from_max.abs() < 2).mean()*100:.0f}%")
top = fl[fl.flux >= 1e-3].sort_values("time")
print("\nAll R4+ events (≥X10 on today's scale):")
for _, e in top.iterrows():
    print(f"   {e.time:%Y-%m-%d}  {e['class']:6s} cycle {e.cycle:.0f}, {e.from_max:+.1f} yr from max  [{e.src}]")

# ---------- figures ----------
fig, ax = plt.subplots(figsize=(13, 5.5))
ax.bar(yr.index - 0.2, yr["R1+ (≥M1)"] - yr["R3+ (≥X1)"], width=0.4, color="tab:orange", label="M-class flares (R1–R2 blackouts)")
ax.bar(yr.index + 0.2, yr["R3+ (≥X1)"] * 10, width=0.4, color="tab:red", label="X-class flares × 10 (R3+ blackouts)")
ax.set_ylabel("Flares per year"); ax.set_xlabel("Year")
ax2 = ax.twinx(); ax2.plot(yr.index, yr.SSN, c="k", lw=2, marker="o", ms=3, label="Yearly mean sunspot number")
ax2.set_ylabel("Sunspot number"); ax2.set_ylim(0, None)
for y, n in yr["R4+ (≥X10)"].items():
    if n: ax.text(y, max(yr.loc[y, "R1+ (≥M1)"] - yr.loc[y, "R3+ (≥X1)"], yr.loc[y, "R3+ (≥X1)"] * 10) + 15,
                  f"{n}×R4", ha="center", fontsize=8, color="darkred", fontweight="bold")
ax.set_ylim(0, 1150)
ax2.set_ylim(0, 280)
h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
ax.legend(h1+h2, l1+l2, loc="upper center", ncol=3, fontsize=9)
ax.set_title("NOAA GOES flares vs sunspot number, 1976–2026  (n×R4 = number of ≥X10 flares that year)")
plt.tight_layout(); plt.savefig(F+"flares_vs_sunspots.png", dpi=150)

fig, (a, a2, b) = plt.subplots(1, 3, figsize=(16, 5))
xx = np.linspace(0, 240, 10)
for axx, k, col in [(a, "R1+ (≥M1)", "tab:orange"), (a2, "R3+ (≥X1)", "tab:red")]:
    rr = np.corrcoef(yr.SSN, yr[k])[0, 1]
    axx.scatter(yr.SSN, yr[k], c=col, s=22)
    axx.plot(xx, fits[k] * xx, c=col, ls="--", label=f"{fits[k]*100:.0f} per year per 100 SSN")
    for y in [1989, 2003, 2024]:
        axx.annotate(str(y), (yr.SSN[y], yr[k][y]), xytext=(4, 4), textcoords="offset points", fontsize=8)
    axx.set_xlabel("Yearly mean sunspot number"); axx.set_ylabel("Flares in that year")
    axx.set_title(f"{k} flares per year (r = {rr:.2f})"); axx.legend(fontsize=8)
b.hist(big.from_max, bins=np.arange(-6, 9, 0.5), color="tab:red")
b.axvspan(-1, 1, color="tab:orange", alpha=.2); b.axvline(0, c="k", ls=":")
b.set_xlabel("Years from cycle maximum (cycles 21–25)"); b.set_ylabel("Number of X-class flares")
b.set_title("When do X-class flares happen?")
plt.tight_layout(); plt.savefig(F+"flares_relation.png", dpi=150)
