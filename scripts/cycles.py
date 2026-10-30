"""Butterfly diagram + solar cycle analysis + 2035 forecast."""
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

from paths import D, F, assert_data
assert_data(D + "SN_m_tot_V2.0.csv"); assert_data(D + "bflydata.txt")

# ---------- monthly sunspot number, our own 13-month smoothing ----------
sn = pd.read_csv(D+"SN_m_tot_V2.0.csv", sep=";", header=None,
                 names=["y","m","t","ssn","sd","nobs","prov"])
w = np.r_[0.5, np.ones(11), 0.5] / 12          # standard SILSO 13-month window
sn["smooth"] = np.convolve(sn.ssn, w, mode="same")
sn.loc[:5, "smooth"] = np.nan; sn.loc[len(sn)-6:, "smooth"] = np.nan

# cycle minima (SILSO official dates, decimal years), cycles 1..25
minima = [1755.2,1766.5,1775.5,1784.7,1798.3,1810.6,1823.3,1833.9,1843.5,1855.9,
          1867.2,1878.9,1890.2,1902.0,1913.6,1923.6,1933.7,1944.1,1954.3,1964.8,
          1976.2,1986.7,1996.6,2008.9,2019.9]
rows=[]
for i,t0 in enumerate(minima):
    t1 = minima[i+1] if i+1<len(minima) else sn.t.max()
    seg = sn[(sn.t>=t0)&(sn.t<t1)].dropna(subset=["smooth"])
    k = seg.smooth.idxmax()
    rows.append(dict(cycle=i+1, start=t0, max_time=seg.t[k], max_ssn=seg.smooth[k],
                     rise=seg.t[k]-t0, length=(t1-t0) if i+1<len(minima) else np.nan))
cyc = pd.DataFrame(rows); cyc.to_csv(D+"cycles_table.csv", index=False)
print(cyc.round(2).to_string(index=False))

L = cyc.length.dropna()
print(f"\nCycle length: mean {L.mean():.2f} yr, std {L.std():.2f}, range {L.min():.1f}-{L.max():.1f}")
c25 = cyc.iloc[-1]
# Cycle 26 start & max estimates
start26 = c25.start + L.mean(); s_sd = L.std()
rise = cyc.rise.mean(); r_sd = cyc.rise.std()
max26 = start26 + rise
print(f"Cycle 25: min {c25.start}, max {c25.max_time:.2f} at smoothed SSN {c25.max_ssn:.1f}")
print(f"Cycle 26 min est {start26:.1f} ± {s_sd:.1f};  rise {rise:.1f} ± {r_sd:.1f} yr")
print(f"Cycle 26 MAX est {max26:.1f} ± {np.hypot(s_sd,r_sd):.1f}")

# ---------- butterfly data (Hathaway, NASA MSFC): per Carrington rotation, 50 sin-lat bins ----------
txt = open(D+"bflydata.txt").read().replace(",", " ").split()
vals = list(map(int, txt)); recs=[]; i=0
while i < len(vals):
    cr = vals[i]; recs.append((cr, vals[i+1:i+51])); i += 51
crs = np.array([r[0] for r in recs]); grid = np.array([r[1] for r in recs], float)
cr_date = lambda c: datetime(1853,11,9) + timedelta(days=(c-1)*27.2753)
tyear = np.array([ (lambda d: d.year + (d.timetuple().tm_yday-1)/365.25)(cr_date(c)) for c in crs])
sinlat_edges = np.linspace(-1,1,51); lat_edges = np.degrees(np.arcsin(sinlat_edges))
print(f"Butterfly data: CR {crs[0]}–{crs[-1]}, {tyear[0]:.1f}–{tyear[-1]:.1f}")

def lat_stats(t0,t1):
    m=(tyear>=t0)&(tyear<t1); g=grid[m].sum(0); c=np.degrees(np.arcsin((sinlat_edges[:-1]+sinlat_edges[1:])/2))
    return (np.abs(c)*g).sum()/g.sum() if g.sum() else np.nan

fig,(a1,a2)=plt.subplots(2,1,figsize=(13,8),sharex=True,gridspec_kw=dict(height_ratios=[3,2]))
m = tyear>=2006
a1.pcolormesh(np.r_[tyear[m], tyear[m][-1]+0.0747], lat_edges, np.ma.masked_equal(np.log10(grid[m].T+1),0),
              cmap="inferno_r", shading="flat")
a1.set_ylim(-50,50); a1.axhline(0,c="gray",lw=.5); a1.set_ylabel("Latitude (°)")
a1.set_title("Butterfly diagram – Solar Cycles 24 & 25 (sunspot area by latitude, NASA/MSFC Hathaway data)")
for t,lab in [(2008.9,"Cycle 24 starts"),(2019.9,"Cycle 25 starts")]:
    a1.axvline(t,c="tab:blue",ls="--"); a1.text(t+.2,44,lab,color="tab:blue")
s = sn[sn.t>=2006]
a2.bar(s.t, s.ssn, width=0.08, color="0.75", label="Monthly sunspot number")
a2.plot(s.t, s.smooth, c="tab:red", lw=2, label="13-month smoothed")
a2.axvspan(max26-np.hypot(s_sd,r_sd), max26+np.hypot(s_sd,r_sd), color="tab:orange", alpha=.2)
a2.axvline(max26, c="tab:orange", lw=2, label=f"Cycle 26 max estimate ≈ {max26:.1f}")
a2.axvline(2035.5, c="k", ls=":", label="2035 launch window")
a2.set_xlim(2006, 2041); a2.set_ylabel("Sunspot number"); a2.set_xlabel("Year"); a2.legend(loc="upper left", fontsize=8)
plt.tight_layout(); plt.savefig(F+"butterfly_c24_c25.png", dpi=150)

# ---------- latitude drift per year (Spörer's law) ----------
print("\nMean |latitude| of sunspot area by year:")
for y in range(2009, int(tyear[-1])+1): print(y, f"{lat_stats(y,y+1):.1f}°")

# ---------- forecast curve: average cycle shape scaled to plausible amplitudes ----------
def hathaway(t, A, t0, b=27.12, c=0.71):     # Hathaway et al. 1994 cycle-shape function (t in months)
    x = np.clip((t-t0),0,None)
    return A*(x/b)**3/(np.exp((x/b)**2)-c)
months = np.arange(0, 12*12)
_x=np.linspace(0.01,5,5000); _y=_x**3/(np.exp(_x**2)-0.71); B = rise*12/_x[_y.argmax()]   # scale so peak = mean rise time
fig,ax=plt.subplots(figsize=(12,5))
ax.plot(sn.t, sn.smooth, c="tab:red", lw=2, label="Observed (smoothed)")
for A,lab,col in [(cyc.max_ssn.mean(),"Average cycle","tab:orange"),(c25.max_ssn,"Same strength as Cycle 25","tab:purple"),
                  (cyc.iloc[23].max_ssn,"Weak like Cycle 24","tab:green")]:
    shape = hathaway(months,1,0,b=B); shape/=shape.max()
    ax.plot(start26+months/12, A*shape, ls="--", c=col, label=f"Cycle 26 scenario: {lab} (peak {A:.0f})")
ax.axvline(2035.5,c="k",ls=":"); ax.text(2035.6,10,"2035",fontsize=10)
ax.set_xlim(1995,2044); ax.set_ylim(0,300); ax.set_xlabel("Year"); ax.set_ylabel("Smoothed sunspot number")
ax.set_title("Forecast of Solar Cycle 26 and the 2035 launch window"); ax.legend(fontsize=8)
plt.tight_layout(); plt.savefig(F+"forecast_2035.png", dpi=150)
shape=hathaway(months,1,0,b=B); shape/=shape.max()
idx=int(round((2035.5-start26)*12)); print(f"\n2035.5 is {2035.5-start26:.1f} yr into cycle 26 -> {shape[idx]*100:.0f}% of peak")
for A in [cyc.iloc[23].max_ssn, cyc.max_ssn.mean(), c25.max_ssn]: print(f"  peak {A:.0f} -> SSN in mid-2035 ≈ {A*shape[idx]:.0f}")
