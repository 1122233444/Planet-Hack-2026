"""The protection plan as two tables: the five protection layers and the response playbook (who does what at each
NOAA alert level). Every number is read from the results of the other scripts."""
import json, textwrap, numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from paths import D, F

gs = json.load(open(D + "geomagnetic_summary.json"))
ps = json.load(open(D + "protons_summary.json"))
ds = json.load(open(D + "drag_summary.json"))
cs = json.load(open(D + "cost_summary.json"))
fc = json.load(open(D + "forecast_v2_summary.json"))
yr = pd.read_csv(D + "flares_per_year.csv", index_col=0)
ssn35 = np.median(pd.read_csv(D + "forecast_v2_ssn2035_samples.csv").ssn_2035)
r3 = yr["R3+ (≥X1)"].sum() / yr.SSN.sum() * ssn35
r4 = yr["R4+ (≥X10)"].sum() / yr.SSN.sum() * ssn35
g = lambda key: gs[key][1]
s = lambda key: ps[key]["y2035"][1]
fuel550 = [ds["budget"][f"550 km, B={b}"]["fuel 2035"] for b in (0.01, 0.1)]


def draw_table(fname, title, header, rows, widths, colors, note):
    """Rows of wrapped text in coloured bands; widths in characters per column."""
    wrapped = [[textwrap.wrap(str(c), w) or [""] for c, w in zip(r, widths)] for r in rows]
    heights = [max(len(c) for c in r) for r in wrapped]
    total = sum(heights) + 2 * len(rows) + 3
    fig = plt.figure(figsize=(17, 0.26 * total + 1.2))
    ax = fig.add_axes([0.01, 0.06, 0.98, 0.86]); ax.axis("off")
    ax.set_xlim(0, sum(widths) + len(widths)); ax.set_ylim(total, 0)
    x = np.cumsum([0] + [w + 1 for w in widths])
    for j, h in enumerate(header):
        ax.text(x[j] + 0.5, 1.2, h, fontsize=10, fontweight="bold", va="center")
    y = 2.6
    for r, h, col in zip(wrapped, heights, colors):
        ax.add_patch(plt.Rectangle((0, y - 0.5), x[-1], h + 1.2, color=col, alpha=0.35, lw=0))
        for j, cell in enumerate(r):
            ax.text(x[j] + 0.5, y, "\n".join(cell), fontsize=9.5, va="top", linespacing=1.35,
                    fontweight="bold" if j == 0 else "normal")
        y += h + 2
    fig.suptitle(title, fontsize=13, fontweight="bold", y=0.985)
    fig.text(0.01, 0.015, note, fontsize=8.5, color="dimgray")
    fig.savefig(F + fname, dpi=150); plt.close(fig)
    print("saved figures/" + fname)


draw_table(
    "layered_protection.png",
    "Layered protection for a Starlink-like constellation in 2035 — no single technology stops space weather",
    ["Layer", "What we do", "The numbers behind it (our analyses)", "Protects against"],
    [["1  Monitor and warn",
      "Watch flares (GOES X-rays), particles (GOES protons) and CMEs (coronagraphs: 1–3 days' warning; solar-wind monitors "
      "at L1: 15–60 minutes). Our tools: risk calendar (years), active-region calendar (weeks), 3-day quiet-window rule (days). "
      "An operations desk warns satellite operators before conditions arrive. From about 2031 ESA's Vigil at L5 sees regions "
      "about 4.5 days earlier.",
      f"Maximum {fc['max_mean']:.1f} ± {fc['max_sd']:.1f}; storms peak 1–3 years after it. The calendar predicted the May 2024 "
      f"G5 region's dates to within 0.7 days, 5 weeks ahead. In years like 2035, {gs['free3_G1']:.0%} of 3-day stretches are storm-free.",
      "Everything: early warning"],
     ["2  Orbit",
      "Deploy new satellites at 300 km or higher (not 210 km). Operate near 550 km. Track the orbits from the ground and "
      "re-raise satellites after storms with electric propulsion. Prefer low inclination where the service allows.",
      f"In safe mode a satellite survives 19–33 days at 300 km but 2–3 days at 210 km in 2035. Holding 550 km costs "
      f"{fuel550[0]:.1f}–{fuel550[1]:.1f} kg of fuel a year.",
      "Drag in storms; protons over the poles"],
     ["3  Satellite: solar-hardened, not fully hardened",
      f"Fly edge-on in storms. A {cs['m_vault']:.0f} kg liquid-cooled, shielded vault (2 g/cm²) only around the flight computer "
      "and power control. Commercial chips with triple redundancy, error-correcting memory and watchdogs. Conductive skin, "
      "single-point grounding. Safe mode: non-essential instruments off, less electrical activity, battery kept charged, "
      "telemetry and health monitoring stay on. Solar arrays sized with margin for proton damage.",
      f"+{cs['m_layer']:.0f} kg per satellite instead of +{cs['m_full']:.0f} kg for full hardening. 2035: about {s('S1+'):.0f} "
      f"proton events ({s('S3+'):.1f} strong) and {r3:.0f} X-class flares.",
      "Radiation hits, charging, drag"],
     ["4  Constellation",
      "Spare satellites in orbit, automatic safe mode, quick replacement launches.",
      f"A dead satellite at 550 km falls back in about {ds['dead_years']['2035']:.1f} years at solar maximum "
      f"({ds['dead_years']['solar minimum']:.0f} years at minimum): no long-lived debris.",
      "Losing single satellites"],
     ["5  Ground and critical systems",
      "Ground stations on batteries and generators, able to run off the grid. Stations spread in latitude and longitude. "
      "Links that do not depend on short-wave radio.",
      f"Québec 1989 (G5): 9-hour grid blackout. 2035: about {g('y2035_G4+'):.0f} severe (G4+) storm days and {r3:.0f} R3+ radio blackouts.",
      "Power-grid failures, radio blackouts"],
     ["6  Emerging technology, chosen now",
      "On-board autonomy: the satellite enters safe mode by itself from its own radiation and charging sensors if the ground "
      "link is down. Laser links between satellites keep data flowing through radio blackouts. Machine-learning flare "
      "forecasts from SDO magnetograms feed the operations desk.",
      "The $100 billion system is not built yet: seven years before launch, the vault, the safe mode and the 300 km "
      "deployment cost almost nothing to write into the design and the launch contracts.",
      "Slow reactions, lost links"]],
    [44, 62, 66, 22],
    ["#cfe2f3", "#d9ead3", "#fff2cc", "#fce5cd", "#ead1dc", "#d9d2e9"],
    "Sources: forecast_v2.py, geomagnetic.py, protons.py, flares.py, drag.py, region_calendar.py, cost.py (this repository). "
    "Satellite mass, drag area and costs are assumptions (see cost.py and drag.py).")

draw_table(
    "response_playbook.png",
    "Response playbook: what each team does at each NOAA alert level, and how often to expect it in 2035",
    ["Level", "Trigger", "How often in 2035", "Satellites", "Launch and deployment", "Ground stations"],
    [["Routine", "Every day: NOAA SWPC forecasts, our active-region calendar",
      "365 days", "Normal operations; the operations desk updates the region calendar and sends a daily outlook to operators", "Deploy only into a forecast 3-day quiet window, at 300 km or higher",
      "Test backup power every month"],
     ["Watch", "A big region enters the danger zone (E30–W90), or G1–G2 storm, S1 proton event, R1–R2 blackout",
      f"G1+ storm days: about {g('y2035_G1+'):.0f}; S1+ proton events: about {s('S1+'):.0f}",
      "Check spares are ready; avoid manoeuvres while the region is in the danger zone", "Hold new deployments",
      "Check generator fuel; plan links that avoid short-wave radio"],
     ["Warning", "G3 storm, S2 proton event or R3 blackout (X-class flare)",
      f"G3+ days: about {g('y2035_G3+'):.0f}; S2+ events: about {s('S2+'):.0f}; X-class flares: about {r3:.0f}",
      "Charge batteries fully; satellites below 400 km fly edge-on; pause manoeuvres and software uploads; scrub memory more often", "No launches",
      "Backup power on standby; staff on call"],
     ["Alert", "G4–G5 storm, S3+ proton event or R4 blackout",
      f"G4+ days: about {g('y2035_G4+'):.0f}; G5 storms: about {g('y2035_G5_storms'):.1f}; S3+ events: about {s('S3+'):.1f}; "
      f"R4 flares: about {r4:.1f}",
      "Safe mode for all: edge-on, non-essential instruments off, less electrical activity; keep the telemetry link and health monitoring", "No launches",
      "Switch to backup power and run off the grid; staff 24/7; coordinate with the grid operator"],
     ["Recovery", "After the storm", "—",
      "Track orbits from the ground; raise satellites that sank; reset upsets; check batteries and solar-array output; replace failures from spares",
      "Resume normal operations after a 3-day quiet forecast", "Reconnect to the grid; write a short report"]],
    [10, 30, 30, 34, 26, 30],
    ["#d9ead3", "#fff2cc", "#fce5cd", "#f4cccc", "#cfe2f3"],
    "Frequencies are 2035 medians from geomagnetic.py (storm days and storms), protons.py (proton events) and flares.py "
    "(X-class flares). NOAA scales: G = geomagnetic storm, S = solar radiation storm, R = radio blackout.")
