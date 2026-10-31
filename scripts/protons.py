"""Solar proton events (NOAA S-scale, radiation storms) 1976-2017 vs sunspot number, where on the Sun they start,
and the 2035 outlook.

Source: NOAA SWPC list of solar proton events affecting the Earth environment (>= 10 pfu at > 10 MeV), the
preliminary listing at https://umbra.nascom.nasa.gov/SEP/ (saved as data/sep_list.html; it stops in 2017, and the
solar-minimum years 2018-2019 had no events). S-scale: S1 >= 10 pfu, S2 >= 100, S3 >= 1000, S4 >= 10^4, S5 >= 10^5.
NOAA notes that several proton increases can be merged into one event and that the GOES detectors were not
cross-calibrated, so counts are approximate.
"""
import re, json, numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from paths import D, F

NOAA_PER_CYCLE = {"S1": 50, "S2": 25, "S3": 10, "S4": 3}      # NOAA scale table, events per cycle at each level

# ---------- parse the event table ----------
txt = open(D + "sep_list.html", encoding="latin-1").read()
assert "Solar Proton Events" in txt, "data/sep_list.html is not the NOAA proton event list"
rows, year = [], None
for tr in re.split(r"<tr>", txt):
    m = re.search(r"<strong>(\d{4})</strong>", tr)
    if m:
        year = int(m.group(1)); continue
    c = [re.sub(r"<[^>]+>", "", x).strip() for x in re.split(r"<td[^>]*>", tr)[1:]]
    if len(c) >= 8 and re.match(r"[A-Z][a-z]{2} \d", c[0]):
        rows.append(dict(year=year, start=c[0], peak=c[1], pfu=float(c[2].replace(",", "")), flare=c[6], location=c[7]))
ev = pd.DataFrame(rows)
ev["S"] = np.floor(np.log10(ev.pfu)).clip(1, 5).astype(int)


def longitude(loc):
    """Central-meridian distance of the source, degrees, west positive; limb sources count as 90."""
    m = re.search(r"([EW])(\d+)", loc)
    if m:
        return (1 if m.group(1) == "W" else -1) * float(m.group(2))
    if "limb" in loc:
        return 90.0 if "W" in loc else -90.0
    return 0.0 if loc.lower() == "disk center" else np.nan


ev["lon"] = ev.location.map(longitude)
print(f"Proton events: {len(ev)} ({ev.year.min()}-{ev.year.max()}); by peak level: "
      + ", ".join(f"S{s}: {(ev.S == s).sum()}" for s in range(1, 6)))
print("Events per cycle (cycles 21-24, 1976-2019 = 4 cycles) at each level vs NOAA's published averages:")
for s in range(1, 5):
    print(f"   S{s}: {(ev.S == s).sum() / 4:5.1f}   (NOAA: {NOAA_PER_CYCLE[f'S{s}']})")

# ---------- per year and the link to sunspots ----------
sn = pd.read_csv(D + "SN_m_tot_V2.0.csv", sep=";", header=None, names=["y", "m", "t", "ssn", "sd", "n", "p"])
yr = pd.DataFrame({"SSN": sn.groupby("y").ssn.mean().loc[1976:2017].round(1)})
for s in range(1, 5):
    yr[f"S{s}+"] = ev[ev.S >= s].groupby("year").size().reindex(yr.index, fill_value=0)
yr.index.name = "year"
yr.to_csv(D + "protons_per_year.csv")
print("\nProton events per year (S1+ = all events, S3+ = strong or stronger):")
print(yr.to_string())

ssn35 = pd.read_csv(D + "forecast_v2_ssn2035_samples.csv").ssn_2035.values
lo, hi = np.percentile(ssn35, [25, 75])
look = yr[(yr.SSN >= lo) & (yr.SSN <= hi)]
print(f"\nLink to the yearly sunspot number (events per year per 100 sunspots, line through 0 as for flares) and 2035 outlook"
      f" (sunspot number 10/50/90%: {np.percentile(ssn35, [10, 50, 90]).round(0)}):")
summary = {}
for s in range(1, 5):
    g = f"S{s}+"
    rate = yr[g].sum() / yr.SSN.sum()
    lam = rate * ssn35
    p30 = 1 - np.exp(-np.median(lam) * 30 / 365.25)
    summary[g] = dict(rate=rate, r=np.corrcoef(yr.SSN, yr[g])[0, 1], y2035=list(np.percentile(lam, [10, 50, 90])),
                      look_years=int((look[g] > 0).sum()), p30=p30)
    print(f"   {g}: {rate * 100:4.2f} per 100 SSN (r = {summary[g]['r']:.2f}) -> 2035: {np.percentile(lam, 10):4.1f} / "
          f"{np.median(lam):4.1f} / {np.percentile(lam, 90):4.1f} events; real years as active as 2035 with at least one: "
          f"{summary[g]['look_years']} of {len(look)}; at least one in a 30-day period: {p30:.0%}")
print(f"   (look-alike years: sunspot number {lo:.0f}-{hi:.0f}: {', '.join(map(str, look.index))})")
quiet = yr[yr.SSN < 50]
print(f"   Big events also come in quiet years: {', '.join(f'{y} (SSN {quiet.SSN[y]:.0f}, {quiet['S3+'][y]} S3+)' for y in quiet.index[quiet['S3+'] > 0])}")

ens = pd.read_csv(D + "forecast_v2_ensemble.csv").dropna()
ssn_y = ens.assign(yy=ens.year.astype(int)).groupby("yy").p50.mean().loc[2035:2044]
print("A satellite working 2035-2044 (median forecast sunspot number each year):")
for g in ["S1+", "S3+", "S4+"]:
    tot = summary[g]["rate"] * ssn_y.sum()
    summary[g]["life"] = tot
    print(f"   {g}: about {tot:4.1f} events" + (f" (at least one: {1 - np.exp(-tot):.0%})" if tot < 10 else ""))

# ---------- where on the Sun do proton events start? ----------
known = ev.dropna(subset=["lon"])
zone = known.lon.between(-30, 90)
print(f"\nSource position known for {len(known)} of {len(ev)} events (the rest: unknown or far side):")
print(f"   western half of the disk: {(known.lon > 0).mean():.0%};  between E30 and W90 (the 'danger zone'): {zone.mean():.0%}")
big = known[known.S >= 3]
print(f"   S3+ events: {big.lon.between(-30, 90).mean():.0%} from E30-W90; the five largest events:")
for _, e in ev.nlargest(5, "pfu").iterrows():
    print(f"      {e.year} {e.start:11s} {e.pfu:8.0f} pfu  flare {e.flare:7s} at {e.location}")
summary |= dict(n_events=len(ev), zone_share=zone.mean(), west_share=(known.lon > 0).mean(), n_known=len(known),
                look_n=len(look), look_ssn=[lo, hi])
json.dump(summary, open(D + "protons_summary.json", "w"), indent=1, default=float)

# ---------- figure ----------
fig, (a1, a2, a3) = plt.subplots(1, 3, figsize=(17, 5), gridspec_kw=dict(width_ratios=[1.4, 1, 1]))
a1.bar(yr.index, yr["S1+"], color="tab:orange", alpha=0.5, label="all proton events (S1+)")
a1.bar(yr.index, yr["S3+"], color="tab:red", label="strong or stronger (S3+)")
t = a1.twinx(); t.plot(yr.index, yr.SSN, c="k", lw=1.5, label="Yearly mean sunspot number"); t.set_ylim(0, 300)
t.set_ylabel("Sunspot number"); a1.set_ylabel("Proton events per year"); a1.set_xlabel("Year"); a1.set_ylim(0, 30)
h1, l1 = a1.get_legend_handles_labels(); h2, l2 = t.get_legend_handles_labels()
a1.legend(h1 + h2, l1 + l2, loc="upper right", fontsize=8)
a1.set_title("Solar proton events (NOAA list), 1976–2017", fontsize=11)
xx = np.linspace(0, 230, 10)
for g, col in [("S1+", "tab:orange"), ("S3+", "tab:red")]:
    a2.scatter(yr.SSN, yr[g], c=col, s=18)
    a2.plot(xx, summary[g]["rate"] * xx, c=col, ls="--", label=f"{g}: {summary[g]['rate'] * 100:.1f} per 100 SSN (r = {summary[g]['r']:.2f})")
a2.axvspan(*np.percentile(ssn35, [10, 90]), color="tab:orange", alpha=0.15, label="2035 forecast (10–90%)")
a2.set_xlabel("Yearly mean sunspot number"); a2.set_ylabel("Proton events in that year"); a2.legend(fontsize=8)
a2.set_title("More sunspots, more radiation storms", fontsize=11)
a3.axvspan(-30, 90, color="tab:orange", alpha=0.15, zorder=0, label=f"danger zone E30–W90 ({zone.mean():.0%} of events)")
a3.hist(known.lon, bins=np.arange(-90, 100, 15), color="tab:gray", label="all events")
a3.hist(big.lon, bins=np.arange(-90, 100, 15), color="tab:red", label="S3+ events")
a3.set_xlabel("Source: degrees from the central meridian (E −, W +)"); a3.set_ylabel("Events")
a3.set_title("Where on the Sun proton events start", fontsize=11); a3.legend(fontsize=8, loc="upper left")
plt.tight_layout(); plt.savefig(F + "protons.png", dpi=150)
