"""Cost-effectiveness of protecting a Starlink-like constellation in 2035 (curveball): full-scale radiation hardening
vs our layered protection, and how the layered cost compares with losing satellites.

Every input below is an assumption: a round number in the range of public figures, with a low and a high value.
The results are order-of-magnitude estimates, not quotes. Storm and drag numbers come from geomagnetic.py and drag.py.
"""
import json, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from paths import D, F

MU, RE, G0 = 3.986004e14, 6371e3, 9.80665
# assumption: (central, low-cost end, high-cost end)
A = dict(
    in_service=(4000, 4000, 4000),          # satellites in the constellation
    life_years=(5, 5, 5),                    # design life -> replacements per year
    per_launch=(50, 50, 50),                 # satellites per launch
    sat_mass=(300, 300, 300),                # kg
    sat_cost=(0.8e6, 0.5e6, 1.5e6),          # US$ per satellite
    launch_per_kg=(2500, 1500, 5000),        # US$ per kg to low Earth orbit
    radhard_premium=(1.0e6, 0.5e6, 3.0e6),   # US$ per satellite for radiation-hardened electronics throughout
    layered_parts=(50e3, 20e3, 100e3),       # US$ per satellite: spare computer, memory protection, grounding, vault pump
    ops_per_year=(2e6, 1e6, 5e6),            # US$ per year: space-weather desk (staff, data, software)
)
SHIELD = 2.0                                  # g/cm² for the shielded parts (≈ 7 mm aluminium or 2.2 cm of ester), chosen in shielding.py
BUS = (3.0, 1.5, 0.3)                         # m, flat satellite body (assumed)
VAULT = (0.30, 0.30, 0.15)                    # m, box around flight computer and power control
VAULT_EXTRA, LAYER_EXTRA = 3.0, 3.0           # kg: vault housing, pump and bellows; spare computer, grounding, coatings
STAGE_DRY, ISP_STAGE = 4000.0, 348.0          # upper stage: dry mass (kg), Isp (s)
SYSTEM = 100e9                                # the "$100 billion system" in the curveball

gs = json.load(open(D + "geomagnetic_summary.json"))
area = lambda d: 2 * (d[0] * d[1] + d[0] * d[2] + d[1] * d[2])
m_full = area(BUS) * SHIELD * 10                         # g/cm² -> kg/m² is ×10
m_vault = area(VAULT) * SHIELD * 10 + VAULT_EXTRA
m_layer = m_vault + LAYER_EXTRA


def hohmann(h1, h2):
    r1, r2 = RE + h1 * 1e3, RE + h2 * 1e3
    a = (r1 + r2) / 2
    return (np.sqrt(MU * (2 / r1 - 1 / a)) - np.sqrt(MU / r1)) + (np.sqrt(MU / r2) - np.sqrt(MU * (2 / r2 - 1 / a)))


dv_deploy = hohmann(210, 300)


def costs(i):
    """Yearly costs (US$) with every assumption at column i (0 central, 1 low, 2 high)."""
    v = {k: x[i] for k, x in A.items()}
    new = v["in_service"] / v["life_years"]; launches = new / v["per_launch"]
    payload = v["per_launch"] * v["sat_mass"]
    lost_payload = (payload + STAGE_DRY) * (1 - np.exp(-dv_deploy / (ISP_STAGE * G0))) / payload
    full = new * (m_full * v["launch_per_kg"] + v["radhard_premium"])
    layered = new * (m_layer * v["launch_per_kg"] + v["layered_parts"]) + lost_payload * launches * payload * v["launch_per_kg"] + v["ops_per_year"]
    batch = v["per_launch"] * (v["sat_cost"] + v["sat_mass"] * v["launch_per_kg"])
    return dict(new=new, launches=launches, lost_payload=lost_payload, full=full, layered=layered, batch=batch,
                full_per_sat=m_full * v["launch_per_kg"] + v["radhard_premium"],
                layered_per_sat=m_layer * v["launch_per_kg"] + v["layered_parts"])


c = [costs(i) for i in range(3)]
print("Assumptions (central / low-cost end / high-cost end):")
for k, x in A.items():
    print(f"   {k:16s}: {x[0]:>12,.0f} {x[1]:>12,.0f} {x[2]:>12,.0f}")
print(f"   shielding {SHIELD} g/cm² on the protected parts; body {BUS} m; vault {VAULT} m")

print(f"\nAdded mass per satellite: full-scale hardening (whole body, {area(BUS):.1f} m²) {m_full:.0f} kg "
      f"(+{m_full / A['sat_mass'][0]:.0%}); layered: vault {m_vault:.1f} kg ({area(VAULT):.2f} m² + {VAULT_EXTRA:.0f} kg housing/pump)"
      f" + {LAYER_EXTRA:.0f} kg other = {m_layer:.1f} kg (+{m_layer / A['sat_mass'][0]:.0%})")
print(f"Deploying at 300 km instead of 210 km: {dv_deploy:.0f} m/s more from the upper stage -> {c[0]['lost_payload']:.1%} "
      "less payload per launch (each satellite then needs about 1 kg less of its own fuel to climb)")
print(f"\nPer satellite: full-scale hardening ${c[0]['full_per_sat'] / 1e6:.2f}M (range {c[1]['full_per_sat'] / 1e6:.2f}-"
      f"{c[2]['full_per_sat'] / 1e6:.2f}M), layered ${c[0]['layered_per_sat'] / 1e3:.0f}k ({c[1]['layered_per_sat'] / 1e3:.0f}-"
      f"{c[2]['layered_per_sat'] / 1e3:.0f}k)")
print(f"Per year ({c[0]['new']:.0f} new satellites on {c[0]['launches']:.0f} launches):")
for key, lab in [("full", "full-scale radiation hardening"), ("layered", "our layered protection")]:
    print(f"   {lab:32s}: ${c[0][key] / 1e6:6.0f}M  (range {c[1][key] / 1e6:.0f}-{c[2][key] / 1e6:.0f}M), "
          f"{c[0][key] / SYSTEM:.2%} of the $100 billion system per year")
rat = [x["layered"] / x["full"] for x in c]
print(f"   layered / full: {rat[0]:.0%}  ({min(rat):.0%}-{max(rat):.0%} across the range)")

p5 = 1 - gs["free5_G1"]
storm_batches = c[0]["launches"] * p5
print(f"\nWhat one lost batch costs (50 satellites + their launch): ${c[0]['batch'] / 1e6:.0f}M (range {c[1]['batch'] / 1e6:.0f}-{c[2]['batch'] / 1e6:.0f}M)")
print(f"   The layered protection for a whole year costs as much as losing {c[0]['layered'] / c[0]['batch']:.1f} batches "
      f"(range {c[1]['layered'] / c[1]['batch']:.1f}-{c[2]['layered'] / c[2]['batch']:.1f}).")
print(f"   With 2022 practice (deploy at 210 km whatever the forecast), in a year like 2035 {p5:.0%} of 5-day windows after a"
      f" launch contain a G1+ storm: about {storm_batches:.0f} of the {c[0]['launches']:.0f} batches a year would meet one in their"
      f" first days, and on every 2035 day the air at 210 km is denser than on the day of the February 2022 losses (drag.py).")
print(f"   So the layers pay for themselves if they save about one batch a year. Full-scale hardening costs as much as losing"
      f" {c[0]['full'] / c[0]['batch']:.0f} batches a year and would not have saved the February 2022 satellites: they were lost to drag, not radiation.")
json.dump(dict(m_full=m_full, m_vault=m_vault, m_layer=m_layer, dv_deploy=dv_deploy, costs=c, storm_batches=storm_batches,
               p5=p5, assumptions=A), open(D + "cost_summary.json", "w"), indent=1, default=float)

# ---------- figure ----------
fig, (a, b) = plt.subplots(1, 2, figsize=(13, 5), gridspec_kw=dict(width_ratios=[1, 1.5]))
a.bar(["Full-scale\nhardening", "Our layered\nprotection"], [m_full, m_layer], color=["tab:gray", "tab:green"])
for x, v in enumerate([m_full, m_layer]):
    a.text(x, v + 5, f"+{v:.0f} kg\n(+{v / A['sat_mass'][0]:.0%})", ha="center", fontsize=10)
a.set_ylabel(f"Mass added per satellite (kg), {A['sat_mass'][0]} kg satellite"); a.set_ylim(0, m_full * 1.3)
a.set_title("Shield only what matters", fontsize=11)
labels = ["Full-scale hardening\n(per year)", "Our layered protection\n(per year)", "Losing one batch\nof 50 satellites"]
keys = ["full", "layered", "batch"]
mid = np.array([c[0][k] for k in keys]) / 1e6
err = np.array([[mid[j] - c[1][k] / 1e6, c[2][k] / 1e6 - mid[j]] for j, k in enumerate(keys)]).T
b.bar(labels, mid, yerr=err, capsize=8, color=["tab:gray", "tab:green", "tab:red"])
for x, v in enumerate(mid):
    b.text(x + 0.08, v * 1.15, f"${v:,.0f}M", fontsize=10)
b.set_yscale("log"); b.set_ylabel("US$ million (bars: central values, lines: low–high assumptions)")
b.set_title(f"Yearly cost for {c[0]['new']:.0f} new satellites a year, vs one lost batch", fontsize=11)
plt.tight_layout(); plt.savefig(F + "cost.png", dpi=150)
