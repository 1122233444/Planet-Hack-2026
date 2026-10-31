"""Air drag on a Starlink-like satellite in low Earth orbit: how solar activity and geomagnetic storms change the
air density (NRLMSIS 2.1 atmosphere model), how fast a satellite sinks, and what that means for 2035.

Inputs from our own analyses: the 2035 sunspot forecast (forecast_v2.py), converted to the F10.7 radio flux that
heats the upper atmosphere, and the storm days per G level expected in 2035 (geomagnetic.py).
Satellite (assumed, Starlink-like): mass 300 kg; ballistic coefficient B = Cd·A/m of 0.01 m²/kg when flying
edge-on (the low-drag safe mode) and 0.1 m²/kg with the solar array facing the flow. Circular orbits; the
satellite is lost when it sinks to 150 km. Orbit-averaged density = mean over latitudes ±50° and all local times.
"""
import json, numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pymsis
from scipy.integrate import solve_ivp

from paths import D, F
from kp_index import load_kp, AP3

MU, RE, G0 = 3.986004e14, 6371e3, 9.80665
B_LOW, B_HIGH, MASS, ISP = 0.01, 0.1, 300.0, 1500.0          # m²/kg, m²/kg, kg, s (electric propulsion)
H_LOST = 150.0                                                # km
ALTS = np.arange(140, 705, 5.0)
LATS, LONS = np.arange(-50, 51, 10), np.arange(0, 360, 15)

# ---------- daily Kp/Ap, sunspot number and F10.7 (GFZ file, see geomagnetic.py) ----------
k = load_kp()

# sunspot number -> F10.7 (yearly means 1947-2025)
y = k[(k.F107obs > 0) & k.Y.between(1947, 2025)].groupby("Y").agg(F=("F107obs", "mean"), SN=("SN", "mean"))
fb, fa = np.polyfit(y.SN, y.F, 1)
ssn35 = pd.read_csv(D + "forecast_v2_ssn2035_samples.csv").ssn_2035.values
F35 = fa + fb * np.percentile(ssn35, [10, 50, 90])
FMIN = y.F.min()
print(f"Yearly F10.7 = {fa:.1f} + {fb:.3f} × sunspot number (1947-2025, r = {np.corrcoef(y.SN, y.F)[0, 1]:.3f})")
print(f"   2035 (sunspot number 10/50/90%: {np.percentile(ssn35, [10, 50, 90]).round(0)}): F10.7 = {F35.round(0)}")
print(f"   solar minimum: lowest yearly F10.7 = {FMIN:.0f} ({y.F.idxmin()})")

# typical daily Ap on days whose highest Kp reaches each G level (1932-2026)
BANDS = {"quiet": (0, 4.66), "G1": (4.66, 5.66), "G2": (5.66, 6.66), "G3": (6.66, 7.66), "G4": (7.66, 8.9), "G5": (8.9, 10)}
AP = {lev: k[(k.kp >= lo) & (k.kp < hi)].Ap.median() for lev, (lo, hi) in BANDS.items()}
print("Median daily Ap on days at each level:", {lev: int(v) for lev, v in AP.items()})


def day(d):
    """F10.7 of the previous day, 81-day mean F10.7 and daily Ap for a real date."""
    t = pd.Timestamp(d)
    w = k[(k.date >= t - pd.Timedelta(days=40)) & (k.date <= t + pd.Timedelta(days=40)) & (k.F107obs > 0)]
    return k.loc[k.date == t - pd.Timedelta(days=1), "F107obs"].iloc[0], w.F107obs.mean(), k.loc[k.date == t, "Ap"].iloc[0]


def density(f107, f107a, ap):
    """Orbit-averaged mass density (kg/m³) at ALTS."""
    out = pymsis.calculate(np.datetime64("2035-03-20T12:00"), LONS, LATS, ALTS, [f107], [f107a], [[ap] * 7], version=2.1)
    return out[0, :, :, :, pymsis.Variable.MASS_DENSITY].mean(axis=(0, 1))


f22q, f22s, f24 = day("2022-02-01"), day("2022-02-04"), day("2024-05-11")
SC = {"solar minimum, quiet": (FMIN, FMIN, AP["quiet"]),
      "2035, quiet": (F35[1], F35[1], AP["quiet"])}
SC |= {f"2035, {lev} day": (F35[1], F35[1], AP[lev]) for lev in ["G1", "G2", "G3", "G4", "G5"]}
SC |= {"May 2024 peak (G5)": f24, "Feb 2022, before the storm": f22q, "Feb 2022, storm (G1)": f22s,
       "2021, quiet (earlier launches)": (y.F[2021], y.F[2021], AP["quiet"])}
rho = pd.DataFrame({name: density(*v) for name, v in SC.items()}, index=ALTS)
rho.index.name = "alt_km"
rho.to_csv(D + "drag_density.csv", float_format="%.4e")
print("\nScenario inputs (F10.7 previous day, F10.7 81-day mean, daily Ap):")
for name, v in SC.items():
    print(f"   {name:28s} {v[0]:6.0f} {v[1]:6.0f} {v[2]:5.0f}")
print("\nOrbit-averaged air density (kg/m³):")
print(rho.loc[[200, 210, 300, 350, 400, 480, 550, 600]].to_string(float_format=lambda x: f"{x:.2e}"))
print("\nDensity relative to '2035, quiet':")
print((rho.loc[[210, 350, 480, 550]] / rho[["2035, quiet"]].loc[[210, 350, 480, 550]].values).round(2).T.to_string())


# ---------- how fast a satellite sinks ----------
def sink_rate(h_km, r, B):
    """km per day for a circular orbit: dh/dt = −ρ·B·√(μ·r)."""
    return np.exp(np.interp(h_km, ALTS, np.log(r))) * B * np.sqrt(MU * (RE + h_km * 1e3)) * 86400 / 1e3


def days_left(h0, B, r_first, r_after=None, switch_days=np.inf, t_max=3650.0):
    """Days until the orbit sinks to 150 km; density r_first until switch_days, then r_after."""
    rhs = lambda t, h: [-sink_rate(h[0], r_first if t < switch_days or r_after is None else r_after, B)]
    hit = lambda t, h: h[0] - H_LOST
    hit.terminal = True
    s = solve_ivp(rhs, (0, t_max), [h0], events=hit, max_step=0.25 if h0 < 400 else 5.0, rtol=1e-6)
    return s.t_events[0][0] if len(s.t_events[0]) else np.inf


print("\nCheck with February 2022 (Starlink deployed with perigee ~210 km; 38 of 49 lost within days):")
q, s, r21 = rho["Feb 2022, before the storm"], rho["Feb 2022, storm (G1)"], rho["2021, quiet (earlier launches)"]
print(f"   density at 210 km, storm day vs typical 2021 conditions (earlier launches): ×{s[210] / r21[210]:.2f}"
      "  (SpaceX: drag up to 50% higher than during previous launches)")
print(f"   of which the storm itself (vs the days just before): ×{s[210] / q[210]:.2f}; the rest is the rising solar cycle")
r35 = rho["2035, quiet"]
print(f"   a QUIET day in 2035 vs that storm day: ×{r35[210] / s[210]:.2f} at 210 km, ×{r35[350] / s[350]:.2f} at 350 km")
for B in (B_LOW, 0.02):
    print(f"   B = {B} m²/kg, circular 210 km: {days_left(210, B, q):.1f} days before the storm conditions, "
          f"{days_left(210, B, s):.1f} days in them  (sinking {sink_rate(210, q.values, B):.0f} -> {sink_rate(210, s.values, B):.0f} km/day)")
print("   (all survival times scale as 1/B: a satellite stuck with its array facing the flow, B = 0.1, lasts 10× shorter)")

# ---------- check: daily Ap vs the 3-hourly ap history that MSIS can also use ----------
ap3 = pd.Series(k[AP3].values.ravel(),
                index=np.repeat(k.date.values, 8) + np.tile(np.arange(8) * np.timedelta64(3, "h"), len(k)))


def density_3h(t, alts):
    """Orbit-averaged density at time t, MSIS storm-time mode fed with the real 3-hourly ap history."""
    t = pd.Timestamp(t); f107, f107a, Ap = day(t.normalize())
    a = lambda h: ap3[t.floor("3h") - pd.Timedelta(hours=h)]
    aps = [Ap, a(0), a(3), a(6), a(9), np.mean([a(h) for h in range(12, 34, 3)]), np.mean([a(h) for h in range(36, 58, 3)])]
    out = pymsis.calculate(np.datetime64(t.strftime("%Y-%m-%dT%H:%M")), LONS, LATS, alts, [f107], [f107a], [aps],
                           version=2.1, geomagnetic_activity=-1)
    return out[0, :, :, :, pymsis.Variable.MASS_DENSITY].mean(axis=(0, 1))


print("Daily Ap (used here) vs real 3-hourly ap, highest density during the storm relative to its first day:")
for name, t0, t1 in [("May 2024", "2024-05-09", "2024-05-13"), ("Feb 2022", "2022-02-01", "2022-02-06")]:
    ts = pd.date_range(t0, t1, freq="3h")
    st = np.array([density_3h(t, [210.0, 480.0]) for t in ts])
    dd = np.array([density(*day(t)) for t in pd.date_range(t0, t1, freq="D")])[:, [np.searchsorted(ALTS, 210), np.searchsorted(ALTS, 480)]]
    print(f"   {name}: 3-hourly ×{st[:, 0].max() / st[0, 0]:.2f} at 210 km, ×{st[:, 1].max() / st[0, 1]:.2f} at 480 km; "
          f"daily ×{dd[:, 0].max() / dd[0, 0]:.2f} and ×{dd[:, 1].max() / dd[0, 1]:.2f}")

# ---------- how high must a new satellite be deployed? ----------
H0 = np.arange(200, 405, 5.0)
SURV = {name: [days_left(h, B_LOW, rho[name]) for h in H0] for name in
        ["solar minimum, quiet", "2035, quiet", "2035, G4 day", "2035, G5 day", "May 2024 peak (G5)"]}
SURV["2035, 3-day G5 storm, then quiet"] = [days_left(h, B_LOW, rho["2035, G5 day"], rho["2035, quiet"], 3) for h in H0]
surv = pd.DataFrame(SURV, index=H0)
print(f"\nDays a satellite in low-drag safe mode (B = {B_LOW}) survives without raising its orbit, by starting altitude:")
print(surv.loc[[200, 210, 250, 300, 350, 400]].round(1).to_string())
need = {}
for name in surv:
    need[name] = {n: float(surv.index[np.argmax(surv[name].values >= n)]) for n in (7, 14)}
    print(f"   {name:34s}: lowest altitude that survives 7 days: {need[name][7]:.0f} km, 14 days: {need[name][14]:.0f} km")

# ---------- yearly drag budget: storm days weighted by how often they happen ----------
gs = json.load(open(D + "geomagnetic_summary.json"))
gy = pd.read_csv(D + "geomagnetic_per_year.csv", index_col=0)
lowyears = gy[(gy.SSN < 20) & (gy.index < 2026)]
plus = {"2035": {g: gs[f"y2035_{g}"][1] for g in ["G1+", "G2+", "G3+", "G4+", "G5"]},
        "solar minimum": {g: lowyears[g].mean() for g in ["G1+", "G2+", "G3+", "G4+", "G5"]}}


def level_days(p):
    """Days per year at each single level, from 'level or stronger' counts."""
    lv = {"G1": p["G1+"] - p["G2+"], "G2": p["G2+"] - p["G3+"], "G3": p["G3+"] - p["G4+"], "G4": p["G4+"] - p["G5"], "G5": p["G5"]}
    return {"quiet": 365.25 - p["G1+"]} | lv


mix = {}
for case, p in plus.items():
    days_ = level_days(p)
    fx = F35[1] if case == "2035" else FMIN
    r = {lev: density(fx, fx, AP[lev]) for lev in days_}
    mix[case] = (sum(days_[lev] * r[lev] for lev in days_) / 365.25, days_, r)
print(f"\nStorm days per year used: 2035 = median forecast (geomagnetic.py); solar minimum = mean of the "
      f"{len(lowyears)} years with sunspot number < 20")
for case, (avg, days_, r) in mix.items():
    share = {lev: days_[lev] * r[lev][np.searchsorted(ALTS, 480)] / (avg[np.searchsorted(ALTS, 480)] * 365.25) for lev in days_}
    print(f"   {case:13s}: " + ", ".join(f"{lev} {d:.0f} d" for lev, d in days_.items())
          + f"  -> storm days give {(1 - share['quiet']) * 100:.0f}% of the year's drag at 480 km")
print(f"\nDrag to make up each year to stay at one altitude (ΔV), and electric-propulsion fuel for a {MASS:.0f} kg "
      f"satellite (Isp {ISP:.0f} s):")
budget = {}
for h in (350, 480, 550):
    v = np.sqrt(MU / (RE + h * 1e3))
    for B in (B_LOW, B_HIGH):
        dv = {case: 0.5 * np.interp(h, ALTS, m[0]) * v ** 2 * B * 365.25 * 86400 for case, m in mix.items()}
        fuel = {case: MASS * (1 - np.exp(-x / (ISP * G0))) for case, x in dv.items()}
        budget[f"{h} km, B={B}"] = dv | {f"fuel {c}": x for c, x in fuel.items()}
        print(f"   {h} km, B = {B:4.2f}: 2035 {dv['2035']:7.1f} m/s ({fuel['2035']:5.1f} kg fuel), "
              f"solar minimum {dv['solar minimum']:6.1f} m/s ({fuel['solar minimum']:5.2f} kg)  -> ×{dv['2035'] / dv['solar minimum']:.0f}")

# a dead satellite left at 550 km (tumbling, B ~ 0.05): years until it burns up, if conditions stayed as in each case
dead = {case: days_left(550, 0.05, m[0], t_max=365.25 * 200) / 365.25 for case, m in mix.items()}
print(f"\nA dead satellite at 550 km (tumbling, B = 0.05) falls back in {dead['2035']:.1f} years in 2035-like conditions, "
      f"{dead['solar minimum']:.0f} years in solar-minimum conditions")

json.dump(dict(F35=list(F35), FMIN=FMIN, AP=AP, need=need, budget=budget, dead_years=dead,
               feb2022_storm_vs_before_210=s[210] / q[210], feb2022_storm_vs_2021_210=s[210] / r21[210],
               quiet2035_vs_feb2022_storm={"210": r35[210] / s[210], "350": r35[350] / s[350]}),
          open(D + "drag_summary.json", "w"), indent=1, default=float)

# ---------- figure ----------
fig, (a, b, c) = plt.subplots(1, 3, figsize=(17, 5.2))
style = {"solar minimum, quiet": ("tab:blue", "-"), "2035, quiet": ("tab:orange", "-"), "2035, G3 day": ("tab:red", "--"),
         "2035, G5 day": ("darkred", "--"), "May 2024 peak (G5)": ("k", ":"), "Feb 2022, storm (G1)": ("tab:purple", "-.")}
for name, (col, ls) in style.items():
    a.semilogx(rho[name], ALTS, c=col, ls=ls, label=name)
for h, lab in [(210, "Starlink deployment (2022)"), (550, "Starlink operating shell")]:
    a.axhline(h, c="gray", lw=0.8); a.text(1.2e-14, h + 6, lab, fontsize=8, color="gray")
a.set_xlim(1e-14, 1e-8); a.set_ylim(150, 650)
a.set_xlabel("Air density (kg/m³), orbit average"); a.set_ylabel("Altitude (km)")
a.set_title("Air density: solar maximum and storms (NRLMSIS 2.1)", fontsize=11); a.legend(fontsize=8, loc="upper right")
for name, col in [("solar minimum, quiet", "tab:blue"), ("2035, quiet", "tab:orange"), ("2035, G4 day", "tab:red"),
                  ("2035, G5 day", "darkred"), ("May 2024 peak (G5)", "k"), ("2035, 3-day G5 storm, then quiet", "tab:green")]:
    b.semilogy(H0, np.clip(surv[name], 0.1, 3650), c=col, label=name)
for n in (7, 14):
    b.axhline(n, c="gray", ls=":", lw=0.8); b.text(204, n, f"{n} days", fontsize=8, va="bottom", color="gray")
b.axvline(210, c="tab:purple", lw=0.8, ls="-."); b.text(212, 300, "Feb 2022\ndeployment", fontsize=8, color="tab:purple")
b.set_xlabel("Starting altitude (km)"); b.set_ylabel(f"Days until re-entry (safe mode, B = {B_LOW} m²/kg)")
b.set_title("How long a satellite survives without raising its orbit", fontsize=11); b.legend(fontsize=7.5, loc="lower right")
hh = np.arange(300, 655, 10.0)
for case, col in [("2035", "tab:orange"), ("solar minimum", "tab:blue")]:
    for B, ls in [(B_HIGH, "-"), (B_LOW, "--")]:
        v = np.sqrt(MU / (RE + hh * 1e3))
        c.semilogy(hh, 0.5 * np.interp(hh, ALTS, mix[case][0]) * v ** 2 * B * 365.25 * 86400, c=col, ls=ls,
                   label=f"{case}, B = {B} m²/kg")
c.set_xlabel("Altitude (km)"); c.set_ylabel("Velocity lost to drag per year, ΔV (m/s)")
c.set_title("Fuel to stay up: 2035 vs solar minimum (storm days included)", fontsize=11); c.legend(fontsize=8)
plt.tight_layout(); plt.savefig(F + "drag_leo.png", dpi=150)
