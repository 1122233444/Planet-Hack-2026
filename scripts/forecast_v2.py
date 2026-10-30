"""Improved Cycle 26 forecast: addresses the limitations of cycles.py (v1).

1. Checks the hand-typed cycle minima against minima found directly in the data.
2. Uses only the reliable cycles (10-25, since 1855) and compares with all cycles.
3. Two independent ways to time the Cycle 26 maximum (from the Cycle 25 minimum,
   and from the Cycle 25 maximum, which is already observed).
4. Historical-analogue ensemble: real cycle curves (double peaks, Waldmeier effect
   included) instead of one smooth formula -> probability ranges for 2035.
"""
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

D = "/home/user/planethack/data/"; F = "/home/user/planethack/figures/"

sn = pd.read_csv(D+"SN_m_tot_V2.0.csv", sep=";", header=None,
                 names=["y","m","t","ssn","sd","nobs","prov"])
w = np.r_[0.5, np.ones(11), 0.5] / 12
sn["smooth"] = np.convolve(sn.ssn, w, mode="same")
sn.loc[:5, "smooth"] = np.nan; sn.loc[len(sn)-6:, "smooth"] = np.nan
s = sn.dropna(subset=["smooth"]).reset_index(drop=True)

MINIMA = [1755.2,1766.5,1775.5,1784.7,1798.3,1810.6,1823.3,1833.9,1843.5,1855.9,
          1867.2,1878.9,1890.2,1902.0,1913.6,1923.6,1933.7,1944.1,1954.3,1964.8,
          1976.2,1986.7,1996.6,2008.9,2019.9]

# ---------- 1. verify minima: local minima of the smoothed curve, at least 7 yr apart ----------
idx, _ = find_peaks(-s.smooth.values, distance=84, prominence=20)
found = s.t.values[idx]
print("1) Hand-typed minimum vs minimum found in data:")
diffs = []
for c, m in enumerate(MINIMA, 1):
    f = found[np.argmin(abs(found - m))]; diffs.append(f - m)
    flag = "" if abs(f - m) < 0.3 else "   <-- differs"
    print(f"   Cycle {c:2d}: typed {m:.1f}  data {f:.2f}{flag}")
print(f"   max |difference| = {max(map(abs, diffs)):.2f} yr")

# ---------- cycle table ----------
rows = []
for i, t0 in enumerate(MINIMA):
    t1 = MINIMA[i+1] if i+1 < len(MINIMA) else s.t.max()
    seg = s[(s.t >= t0) & (s.t < t1)]; k = seg.smooth.idxmax()
    rows.append(dict(cycle=i+1, start=t0, tmax=seg.t[k], amp=seg.smooth[k], rise=seg.t[k]-t0,
                     length=(t1-t0) if i+1 < len(MINIMA) else np.nan))
cyc = pd.DataFrame(rows).set_index("cycle")

# ---------- 2. reliable cycles only ----------
print("\n2) Cycle statistics, all cycles vs reliable cycles (10-25):")
for lab, sub in [("Cycles 1-25 ", cyc), ("Cycles 10-25", cyc.loc[10:])]:
    print(f"   {lab}: length {sub.length.mean():.2f} ± {sub.length.std():.2f} yr, "
          f"rise {sub.rise.mean():.2f} ± {sub.rise.std():.2f} yr, peak {sub.amp.mean():.0f} ± {sub.amp.std():.0f}")
r = np.corrcoef(cyc.loc[10:].amp, cyc.loc[10:].rise)[0, 1]
print(f"   Waldmeier effect (cycles 10-25): correlation(peak, rise time) = {r:.2f}  (negative = strong cycles rise faster)")

# ---------- 3. two independent timings of the Cycle 26 maximum ----------
c = cyc.loc[10:]
A = 2019.9 + np.array([c.length[n] + c.rise[n+1] for n in range(10, 25)])   # min(n) -> max(n+1)
B = cyc.tmax[25] + np.array([c.tmax[n+1] - c.tmax[n] for n in range(10, 25)])  # max(n) -> max(n+1)
print("\n3) Cycle 26 maximum timing (each value = one historical cycle pair):")
for lab, x in [("A: from Cycle 25 minimum (2019.9)", A), (f"B: from Cycle 25 maximum ({cyc.tmax[25]:.1f})", B)]:
    print(f"   {lab}: mean {x.mean():.1f} ± {x.std(ddof=1):.1f}, median {np.median(x):.1f}, "
          f"range {x.min():.1f}-{x.max():.1f}")
both = np.r_[A, B]
print(f"   Combined: {both.mean():.1f} ± {both.std(ddof=1):.1f};  "
      f"share of the 30 estimates landing within 2034.0-2036.99: {np.mean((both>=2034)&(both<2037))*100:.0f}%")

# ---------- 4. analogue ensemble ----------
# start of Cycle 26 = 2019.9 + (length of a past cycle i); then follow the REAL smoothed curve
# of a past cycle j from its minimum. All 15 x 14 combinations of i (10-24) and j (11-24).
ts = s.t.values; ys = s.smooth.values
years = np.arange(2028, 2045.01, 1/12)
ens, own = [], []          # own = the part of each curve that belongs to Cycle 26 itself
for i in range(10, 25):
    start26 = 2019.9 + cyc.length[i]
    for j in range(11, 25):
        tau = years - start26
        ens.append(np.where(tau >= 0, np.interp(cyc.start[j] + tau, ts, ys), np.nan))
        own.append(np.where((tau >= 0) & (tau < cyc.length[j]), ens[-1], -1))
ens = np.array(ens); own = np.array(own)
pct = np.nanpercentile(ens, [10, 25, 50, 75, 90], axis=0)

y35 = (years >= 2035) & (years < 2036)
mean35 = np.nanmean(ens[:, y35], axis=1)
q = np.percentile(mean35, [10, 50, 90])
print(f"\n4) Analogue ensemble ({len(ens)} combinations): mean smoothed SSN during 2035")
print(f"   10th pct {q[0]:.0f} | median {q[1]:.0f} | 90th pct {q[2]:.0f}")
for thr in [50, 100, 150]:
    print(f"   P(2035 average SSN > {thr}) = {np.mean(mean35 > thr)*100:.0f}%")
pk = years[np.argmax(own, axis=1)]
print(f"   Peak year of the ensemble members: median {np.median(pk):.1f}, 10-90%: {np.percentile(pk,10):.1f}-{np.percentile(pk,90):.1f}")

out = pd.DataFrame({"year": years, "p10": pct[0], "p25": pct[1], "p50": pct[2], "p75": pct[3], "p90": pct[4]})
out.to_csv(D+"forecast_v2_ensemble.csv", index=False)
pd.Series(mean35, name="ssn_2035").to_csv(D+"forecast_v2_ssn2035_samples.csv", index=False)

# ---------- figure ----------
fig, ax = plt.subplots(figsize=(12, 5.5))
ax.plot(s.t, s.smooth, c="tab:red", lw=2, label="Observed (13-month smoothed)")
ax.fill_between(years, pct[0], pct[4], color="tab:orange", alpha=.18, label="Forecast 10–90% range")
ax.fill_between(years, pct[1], pct[3], color="tab:orange", alpha=.35, label="Forecast 25–75% range")
ax.plot(years, pct[2], c="tab:orange", lw=2, label="Forecast median")
ax.axvspan(2035, 2036, color="k", alpha=.08); ax.text(2035.1, 285, "2035", fontsize=11)
ax.set_xlim(1995, 2045); ax.set_ylim(0, 300)
ax.set_xlabel("Year"); ax.set_ylabel("Smoothed sunspot number")
ax.set_title(f"Solar Cycle 26 forecast – analogue ensemble of {len(ens)} historical cycle combinations (cycles 10–24)")
ax.legend(loc="upper left", fontsize=9)
plt.tight_layout(); plt.savefig(F+"forecast_v2_ensemble.png", dpi=150)
