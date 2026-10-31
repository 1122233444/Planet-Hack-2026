"""Shielding against solar particles: how much proton dose reaches a satellite's electronics, behind how much
aluminium, in which orbit — for the largest proton events on record, measured by GOES.

1. Fluence. GOES integral proton channels (> 5, 10, 30, 50, 60, 100 MeV, corrected), 5-minute averages, summed
   over each event and multiplied by 4π (isotropic flux). The quiet background (5th percentile) is removed first.
2. Spectrum. log F(>E) is interpolated between the channels; above 100 MeV the 60-100 MeV power law is
   continued to 1 GeV (real spectra fall faster there, so this errs on the safe side).
3. Shielding. A proton of energy E loses energy in aluminium (Bethe formula, as in drag.py's check of ranges);
   behind t g/cm² it keeps the energy E' with R(E') = R(E) - t and deposits S_Si(E') in silicon. Electronics in
   the middle of a closed box of wall t (straight-ahead approximation, no secondary particles).
4. Orbit. In low Earth orbit the Earth's magnetic field turns away protons below the local cutoff rigidity
   (Størmer, tilted dipole: Rc = 14.9 cos⁴(magnetic latitude) / r² GV) and the Earth blocks 30% of the sky at
   550 km. Real cutoffs sit at lower latitudes than Størmer's: SAMPEX saw the ISS (51.6°) graze the polar cap for
   30-60 MeV protons, and cutoffs move a further 5-12° toward the equator in storms (Leske et al. 2001). So we use
   the Størmer cutoff of a latitude 6° higher (quiet) or 16° higher (severe storm). Orbit-averaged over 3 days.
"""
import glob, json, numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from paths import D, F, assert_data

E_CH = [5, 10, 30, 50, 60, 100]                       # MeV, integral channels used
EVENTS = {"October 1989 (S4)": ("1989-10-19", "1989-11-01"), "Halloween 2003 (S4)": ("2003-10-26", "2003-11-08"),
          "January 2005 (S3)": ("2005-01-16", "2005-01-27"), "September 2017 (S3)": ("2017-09-04", "2017-09-18"),
          "the whole of 1989": ("1989-01-01", "1990-01-01")}
ORBITS = {"outside the magnetosphere": None, "LEO 97.6° (polar)": 97.6, "LEO 70°": 70.0, "LEO 53° (Starlink)": 53.0}
SHIFT = {"quiet": 6.0, "storm": 16.0}                 # degrees the real cutoff lies equatorward of Størmer's
H_ORBIT, MEV_G_PER_RAD = 550.0, 6.2415e7
MP, ME, K = 938.272, 0.51099895, 0.307075
DEPTHS = [0.1, 0.5, 1, 2, 5, 10, 20]                  # g/cm² of aluminium (1 g/cm² = 3.7 mm)


# ---------- GOES data ----------
def read_goes(f):
    assert_data(f)
    lines = open(f).read().split("\ndata:", 1)[1].strip().splitlines()
    d = pd.read_csv(pd.io.common.StringIO("\n".join(lines)), na_values=[-99999, -99999.0])
    t = pd.to_datetime(d.time_tag)
    if "p3_flux_ic" in d:                                                    # GOES 7-12 EPS
        cols = {5: "p2_flux_ic", 10: "p3_flux_ic", 30: "p4_flux_ic", 50: "p5_flux_ic", 60: "p6_flux_ic", 100: "p7_flux_ic"}
        out = {e: d[c] for e, c in cols.items()}
    else:                                                                    # GOES 13-15 EPEAD: mean of the two telescopes
        out = {e: d[[f"ZPGT{e}E", f"ZPGT{e}W"]].mean(axis=1) for e in E_CH}
    return pd.DataFrame({e: np.asarray(v, float) for e, v in out.items()}, index=t.values).where(lambda x: x >= 0)


goes = pd.concat([read_goes(f) for f in sorted(glob.glob(D + "goes_protons/*.csv"))]).sort_index()
goes = goes[~goes.index.duplicated()]


def fluence(t0, t1):
    """Omnidirectional event fluence F(>E), protons/cm², background removed."""
    w = goes[(goes.index >= t0) & (goes.index < t1)].interpolate(limit_direction="both")
    w = (w - w.quantile(0.05)).clip(lower=0)
    return np.minimum.accumulate((w.sum() * 300 * 4 * np.pi).values)


# ---------- spectrum, stopping and range ----------
E = np.logspace(0, 3, 600)                            # 1 MeV - 1 GeV


def spectrum(Fch):
    """Differential fluence f(E) (per MeV per cm²) from the channel values."""
    le, lf = np.log(E_CH), np.log(np.maximum(Fch, 1e-3))
    s_lo, s_hi = (lf[1] - lf[0]) / (le[1] - le[0]), (lf[5] - lf[4]) / (le[5] - le[4])
    x = np.log(E)
    lF = np.where(x < le[0], lf[0] + s_lo * (x - le[0]), np.where(x > le[-1], lf[-1] + s_hi * (x - le[-1]), np.interp(x, le, lf)))
    return -np.gradient(np.exp(lF), E)


def stopping(e, za, I):
    """Mass stopping power (MeV cm²/g) of protons, Bethe formula."""
    g = 1 + e / MP; b2 = 1 - 1 / g ** 2
    return K * za / b2 * (np.log(2 * ME * b2 * g ** 2 / (I * 1e-6)) - b2)


S_AL, S_SI = stopping(E, 0.4818, 166.0), stopping(E, 0.4985, 173.0)
R_AL = np.concatenate([[0.0], np.cumsum(np.diff(E) / (0.5 * (S_AL[1:] + S_AL[:-1])))]) + 1.0 / S_AL[0] / 2


def behind(t):
    """Energy each proton keeps behind t g/cm² of aluminium (NaN if it stops)."""
    r = R_AL - t
    return np.where(r > R_AL[0], np.interp(r, R_AL, E), np.nan)


def rigidity(e):
    return np.sqrt(e ** 2 + 2 * e * MP) / 1000         # GV


# ---------- geomagnetic shielding in low Earth orbit ----------
def transmission(incl, shift):
    """Fraction of the time a proton of energy E can reach a circular 550 km orbit, times the visible sky."""
    if incl is None:
        return np.ones_like(E)
    t = np.arange(0, 3 * 86400, 30.0)
    r = 1 + H_ORBIT / 6371.0
    n = np.sqrt(3.986e14 / ((6371e3 + H_ORBIT * 1e3) ** 3))
    u, i = n * t, np.radians(incl)
    lat = np.arcsin(np.sin(i) * np.sin(u))
    lon = np.arctan2(np.cos(i) * np.sin(u), np.cos(u)) - 7.2921e-5 * t
    plat, plon = np.radians(80.7), np.radians(-72.7)                       # north geomagnetic pole (dipole)
    mlat = np.arcsin(np.sin(lat) * np.sin(plat) + np.cos(lat) * np.cos(plat) * np.cos(lon - plon))
    rc = 14.9 * np.cos(np.minimum(np.abs(mlat) + np.radians(shift), np.pi / 2)) ** 4 / r ** 2
    sky = 1 - (1 - np.cos(np.arcsin(1 / r))) / 2                           # part of the sky not blocked by the Earth
    return np.array([(rc < R).mean() for R in rigidity(E)]) * sky


TQ = {name: transmission(i, SHIFT['quiet']) for name, i in ORBITS.items()}
T = {name: transmission(i, SHIFT['storm']) for name, i in ORBITS.items()}      # design case: severe-storm cutoffs


def dose(f, trans, t):
    """Dose in silicon (rad) behind t g/cm² of aluminium."""
    e1 = behind(t)
    ok = np.isfinite(e1)
    return np.sum((f * trans * np.gradient(E))[ok] * np.interp(e1[ok], E, S_SI)) / MEV_G_PER_RAD


def through(f, trans, t, e_min=30.0):
    """Protons per cm² still above e_min MeV behind t g/cm² (the ones that cause single-event upsets)."""
    e1 = behind(t)
    return np.sum((f * trans * np.gradient(E))[np.nan_to_num(e1) > e_min])


# ---------- results ----------
print("Range check (CSDA in aluminium): 100 MeV ->", f"{np.interp(100, E, R_AL):.2f} g/cm² (NIST PSTAR: 9.98)")
print("\nEvent fluences from GOES, protons/cm² (omnidirectional):")
fl = {name: fluence(*w) for name, w in EVENTS.items()}
tab = pd.DataFrame(fl, index=[f">{e} MeV" for e in E_CH]).T
print(tab.map(lambda x: f"{x:.2e}").to_string())
tab.to_csv(D + "sep_fluence.csv", float_format="%.4e")

peak = goes[10].resample("1D").max()
noaa = {"October 1989 (S4)": 40000, "Halloween 2003 (S4)": 29500, "January 2005 (S3)": 5040, "September 2017 (S3)": 1490}
print("Check: highest >10 MeV flux in each event, GOES 5-minute data vs NOAA's event list (pfu):")
for ev, n in noaa.items():
    w = EVENTS[ev]
    print(f"   {ev:22s}: {goes.loc[w[0]:w[1], 10].max():8.0f} vs {n}")
print("\nOrbit-averaged share of protons that reach a 550 km orbit (geomagnetic cutoff × visible sky), quiet / severe storm:")
for name in ORBITS:
    print(f"   {name:26s}: " + ", ".join(f"{e} MeV {np.interp(e, E, TQ[name]):.2f} / {np.interp(e, E, T[name]):.2f}"
                                       for e in (10, 30, 100, 300)))

res = []
for ev, Fch in fl.items():
    f = spectrum(Fch)
    for orb in ORBITS:
        for t in DEPTHS:
            res.append(dict(event=ev, orbit=orb, depth=t, krad=dose(f, T[orb], t) / 1e3, krad_quiet=dose(f, TQ[orb], t) / 1e3,
                            see=through(f, T[orb], t)))
res = pd.DataFrame(res)
res.to_csv(D + "shielding_dose.csv", index=False, float_format="%.4g")
print("\nDose in silicon (krad) behind aluminium (g/cm²; 1 g/cm² = 3.7 mm), severe-storm cutoffs (quiet cutoffs: shielding_dose.csv):")
for ev in ["October 1989 (S4)", "the whole of 1989"]:
    p = res[res.event == ev].pivot(index="orbit", columns="depth", values="krad").loc[list(ORBITS)]
    print(f"   {ev}:\n" + p.to_string(float_format=lambda x: f"{x:9.3f}"))

# ---------- what thickness? ----------
ps = json.load(open(D + "protons_summary.json"))
yr = pd.read_csv(D + "protons_per_year.csv", index_col=0)
scale = max(ps["S3+"]["life"] / yr.loc[1989, "S3+"], ps["S4+"]["life"] / yr.loc[1989, "S4+"])
TOL, MARGIN = 10.0, 2.0                               # krad(Si) a commercial chip survives (assumption), safety factor
print(f"\nA 10-year mission (2035-2044) expects {ps['S3+']['life']:.1f} S3+ and {ps['S4+']['life']:.1f} S4 events; 1989 had "
      f"{yr.loc[1989, 'S3+']} and {yr.loc[1989, 'S4+']}: mission ≈ {scale:.1f} × the whole of 1989 (solar protons only)")
year = res[res.event == "the whole of 1989"]
need = {}
for orb in ORBITS:
    q = year[year.orbit == orb].set_index("depth").krad * scale
    ok = q[q * MARGIN <= TOL]
    need[orb] = float(ok.index.min()) if len(ok) else np.nan
    print(f"   {orb:26s}: mission dose {q[0.1]:6.2f} krad behind a thin 0.1 g/cm² skin, {q[1]:6.2f} behind 1 g/cm², {q[2]:6.2f} behind 2, {q[5]:6.2f} behind 5"
          f"  -> thinnest wall from the list keeping it below {TOL / MARGIN:.0f} krad: "
          + (f"{need[orb]:g} g/cm²" if np.isfinite(need[orb]) else "none"))
oct89 = res[res.event == "October 1989 (S4)"]
for orb in ["LEO 53° (Starlink)", "LEO 97.6° (polar)"]:
    s = oct89[oct89.orbit == orb].set_index("depth").see
    print(f"   Protons above 30 MeV still getting through in October 1989, {orb}: behind 2 g/cm² {s[2] / s[0.1]:.0%}, "
          f"behind 10 g/cm² {s[10] / s[0.1]:.0%} of the unshielded number -> shielding cannot stop bit flips; redundancy must")

json.dump(dict(fluence={k: list(v) for k, v in fl.items()}, need=need, scale=scale, tol=TOL, margin=MARGIN,
               transmission={k: {e: float(np.interp(e, E, v)) for e in (10, 30, 100, 300)} for k, v in T.items()},
               transmission_quiet={k: {e: float(np.interp(e, E, v)) for e in (10, 30, 100, 300)} for k, v in TQ.items()},
               mission={o: year[year.orbit == o].set_index("depth").krad.mul(scale).to_dict() for o in ORBITS}),
          open(D + "shielding_summary.json", "w"), indent=1, default=float)

# ---------- figure ----------
fig, (a, b, c) = plt.subplots(1, 3, figsize=(17, 5.2))
for ev, col in [("October 1989 (S4)", "tab:red"), ("Halloween 2003 (S4)", "tab:orange"), ("January 2005 (S3)", "tab:purple"),
                ("September 2017 (S3)", "tab:green")]:
    a.loglog(E_CH, fl[ev], "o-", c=col, label=ev)
a.set_xlabel("Proton energy E (MeV)"); a.set_ylabel("Protons per cm² with more than E (event total)")
a.set_title("The biggest proton events, measured by GOES", fontsize=11); a.legend(fontsize=8)
for orb, col in zip(ORBITS, ["k", "tab:red", "tab:orange", "tab:blue"]):
    b.semilogx(E, T[orb], c=col, label=orb if orb == "outside the magnetosphere" else f"{orb}, severe storm")
    if orb != "outside the magnetosphere":
        b.semilogx(E, TQ[orb], c=col, ls=":", lw=1.2)
b.set_xlabel("Proton energy (MeV)"); b.set_ylabel("Share that reaches the orbit (time-averaged)")
b.set_title("Earth's magnetic field is the first shield (550 km; dotted: quiet)", fontsize=11); b.legend(fontsize=8); b.set_ylim(0, 1.05)
dd = np.array(DEPTHS)
for orb, col in zip(ORBITS, ["k", "tab:red", "tab:orange", "tab:blue"]):
    q = year[year.orbit == orb].set_index("depth").krad * scale
    c.loglog(dd, q, "o-", c=col, label=orb)
c.axhline(TOL, c="gray", ls="--"); c.text(2.5, TOL * 1.15, f"commercial chip ≈ {TOL:.0f} krad (assumed)", fontsize=8, color="gray")
c.axvline(2, color="tab:green", lw=2, alpha=0.6); c.text(2.15, 0.011, "our vault\n2 g/cm²", fontsize=8, color="tab:green")
c.set_xlabel("Aluminium around the electronics (g/cm²; 1 g/cm² = 3.7 mm)"); c.set_ylabel("10-year solar-proton dose in silicon (krad)")
c.set_title(f"Dose behind shielding, 2035–2044 (≈ {scale:.1f} × the year 1989)", fontsize=11); c.legend(fontsize=8)
plt.tight_layout(); plt.savefig(F + "shielding.png", dpi=150)
