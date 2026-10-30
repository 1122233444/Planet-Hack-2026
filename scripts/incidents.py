"""Cross-check the 2035 forecast against reported space-weather incidents and "look-alike" years.

For each well-documented incident we look up, in our own data: the biggest flare (today's NOAA
scale) and radio-blackout level, the sunspot number of that year and where it sat in the cycle.
Then: how many radio blackouts happened in past years as active as the forecast for 2035?
"""
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from paths import D, F
CYCLE_MAX = [1979.9, 1989.9, 2001.9, 2014.3, 2024.8]          # smoothed sunspot maxima (cycles.py)

# well-documented incidents: (first day, last day, short name, biggest flare as reported at the time, what happened, source)
INCIDENTS = [
    ("1989-03-06", "1989-03-14", "March 1989", "X15",
     "Geomagnetic storm collapses the Hydro-Québec power grid: 6 million people without power for ~9 h",
     "Boteler 2019, Space Weather"),
    ("2003-10-28", "2003-11-04", "Halloween 2003", "X28+",
     "HF radio blackouts, polar flights rerouted, FAA's GPS augmentation (WAAS) unusable ~30 h, "
     "power cut in Malmö (Sweden), Japanese satellite ADEOS-II lost",
     "NOAA Service Assessment 2004"),
    ("2006-12-05", "2006-12-06", "December 2006", "X9.0",
     "Intense solar radio burst makes GPS receivers on the sunlit side of Earth lose track",
     "Cerruti et al. 2008, Space Weather"),
    ("2017-09-06", "2017-09-10", "September 2017", "X9.3",
     "Hours-long HF radio blackout hits emergency communications during the Caribbean hurricane response (Irma)",
     "Redmon et al. 2018, Space Weather"),
    ("2022-01-29", "2022-02-04", "February 2022", "M1.1",
     "Minor geomagnetic storm raises atmospheric drag: 38 of 49 new Starlink satellites re-enter",
     "SpaceX 2022; Dang et al. 2022, Space Weather"),
    ("2024-05-08", "2024-05-14", "May 2024", "X8.7",
     "Strongest geomagnetic storm since 2003 (G5): GPS-guided farm machinery disrupted, HF radio blackouts",
     "NOAA SWPC reports, May 2024"),
]


def r_level(flux):
    for lvl, lim in [(5, 2e-3), (4, 1e-3), (3, 1e-4), (2, 5e-5), (1, 1e-5)]:
        if flux >= lim: return f"R{lvl}"
    return "below R1"


def class_flux(c):
    return dict(M=1e-5, X=1e-4)[c[0]] * float(c[1:].rstrip("+"))


fl = pd.read_csv(D + "flares_1975_2026.csv", parse_dates=["time"])
yr = pd.read_csv(D + "flares_per_year.csv", index_col=0)
rows = []
for a, b, name, reported, what, src in INCIDENTS:
    w = fl[(fl.time >= a) & (fl.time < pd.Timestamp(b) + pd.Timedelta(days=1))]
    big = w.loc[w.flux.idxmax()]
    y = pd.Timestamp(a); dec = y.year + y.dayofyear / 365.25
    cmax = min(CYCLE_MAX, key=lambda m: abs(m - dec))
    rows.append(dict(incident=name, reported_then=reported, level_then=r_level(class_flux(reported)),
                     biggest_flare=big["class"], blackout=r_level(big.flux),
                     n_X=(w.flux >= 1e-4).sum(), year_SSN=yr.SSN[y.year], years_from_max=round(dec - cmax, 1),
                     what=what, source=src))
inc = pd.DataFrame(rows)
pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 200)
print("Reported incidents vs our data. reported_then / level_then = class and R level announced at the time "
      "(up to 2017 on the old scale, about 0.7x the true flux); biggest_flare / blackout = our true-flux scale:")
print(inc.drop(columns=["what", "source"]).to_string(index=False))
inc.to_csv(D + "incidents.csv", index=False)

# ---------- look-alike years: as active as the 2035 forecast ----------
ssn35 = pd.read_csv(D + "forecast_v2_ssn2035_samples.csv").ssn_2035
lo, hi = np.percentile(ssn35, [25, 75])
look = yr[(yr.SSN >= lo) & (yr.SSN <= hi) & (yr.index < 2026)]
print(f"\nPast years with a sunspot number like the 2035 forecast (middle half: {lo:.0f}-{hi:.0f}):")
print(look[["SSN", "R1+ (≥M1)", "R3+ (≥X1)", "R4+ (≥X10)"]].to_string())
print(f"   per year: {look['R1+ (≥M1)'].median():.0f} R1+ events and {look['R3+ (≥X1)'].median():.0f} R3+ events (median); "
      f"at least one R3 in {np.mean(look['R3+ (≥X1)'] > 0) * 100:.0f}% of these years, "
      f"an R4 in {np.mean(look['R4+ (≥X10)'] > 0) * 100:.0f}%")
print(f"   compare the forecast for 2035 from flares.py: ~438 R1+ and ~30 R3+ events")

# ---------- figure: sunspot number, forecast and the incidents on one time line ----------
ens = pd.read_csv(D + "forecast_v2_ensemble.csv")
ens["y"] = ens.year.astype(int)
ey = ens.groupby("y")[["p10", "p50", "p90"]].mean()
fig, ax = plt.subplots(figsize=(14, 5.5))
ax.bar(yr.index, yr.SSN, color="0.75", width=0.8, label="Yearly sunspot number (observed)")
ey = ey[ey.index >= 2030]
ax.fill_between(ey.index, ey.p10, ey.p90, color="tab:orange", alpha=0.25, step="mid", label="Forecast 10–90%")
ax.step(ey.index, ey.p50, where="mid", c="tab:orange", lw=2, label="Forecast median")
ax.axvspan(2034.5, 2035.5, color="tab:red", alpha=0.12)
ax.text(2035, 285, "2035\nlaunch", ha="center", fontsize=9, color="tab:red")
for k, r in inc.iterrows():
    y0 = int(r.incident[-4:])
    ax.annotate(f"{r.incident}\n{r.reported_then} flare", (y0, yr.SSN[y0]), xytext=(0, 40 + 28 * (k % 2)),
                textcoords="offset points", ha="center", fontsize=8, arrowprops=dict(arrowstyle="->", lw=0.8))
ax.set_xlim(1975, 2041); ax.set_ylim(0, 310)
ax.set_xlabel("Year"); ax.set_ylabel("Sunspot number")
ax.set_title("Reported space-weather incidents happen in active years — and 2035 is forecast to be one")
ax.legend(loc="upper center", ncol=3, fontsize=9)
plt.tight_layout(); plt.savefig(F + "incidents_timeline.png", dpi=150)
