"""Cross-section of our vault for the video: an aluminium box with a polyethylene liner around the flight computer,
power control and memory. Wall thicknesses, dose and mass come from shielding.py and cost.py; walls drawn thicker
than scale so the two layers can be seen."""
import json, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from paths import D, F

sh = json.load(open(D + "shielding_summary.json"))
v, tol = sh["vault"], sh["tol"]
dose53 = v["mission"]["LEO 53° (Starlink)"]
area = 2 * (0.30 * 0.30 + 0.30 * 0.15 + 0.30 * 0.15)                # m², box of cost.py (VAULT)
saved = area * (2.0 - v["areal"]) * 10                               # kg of wall saved against 2 g/cm² of aluminium
AL, PE = "#9AA3AD", "#F3EBD3"
W, H, ta, tp = 30.0, 15.0, 0.7, 1.4                                  # cm; wall thicknesses exaggerated, ratio kept

fig = plt.figure(figsize=(16, 9))
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(-7, 53); ax.set_ylim(-9.5, 24.25); ax.set_aspect("equal"); ax.axis("off")
ax.add_patch(Rectangle((0, 0), W, H, fc=AL, ec="#4A5560", lw=2))
ax.add_patch(Rectangle((ta, ta), W - 2 * ta, H - 2 * ta, fc=PE, ec="#B8A77A", lw=1.2))
ax.add_patch(Rectangle((ta + tp, ta + tp), W - 2 * (ta + tp), H - 2 * (ta + tp), fc="white", ec="#B8A77A", lw=1.2))

# electronics on aluminium feet that go through the liner to the outer wall (heat out, grounded)
inner = ta + tp
for x0, w, name, col in [(3.6, 9.4, "Flight computer\n+ hot spare", "#CFE2F3"), (14.0, 6.6, "Power\ncontrol", "#D9EAD3"),
                         (21.6, 5.0, "Memory\n(ECC)", "#FCE5CD")]:
    ax.add_patch(Rectangle((x0, inner + 0.9), w, 6.2, fc=col, ec="#555", lw=1.2))
    ax.text(x0 + w / 2, inner + 4.0, name, ha="center", va="center", fontsize=15)
    for xf in (x0 + 0.8, x0 + w - 1.4):
        ax.add_patch(Rectangle((xf, ta), 0.6, tp + 0.9, fc=AL, ec="#4A5560", lw=1))

def label(xy, xytext, text):
    ax.annotate(text, xy=xy, xytext=xytext, fontsize=15, va="center",
                arrowprops=dict(arrowstyle="-", color="#333", lw=1.1, shrinkA=4, shrinkB=0))

label((W - ta / 2, H * 0.78), (34, 15.2), f"Aluminium, {v['al_mm']:.1f} mm\nstructure, heat path, grounded")
label((W - ta - tp / 2, H * 0.55), (34, 10.3), f"Polyethylene liner, {v['pe_mm']:.1f} mm\nhydrogen-rich: slows protons well")
label((25.5, ta + tp / 2 + 0.2), (34, 5.4), "Aluminium feet through the liner:\nelectronics sit on the metal")

# outer size
ax.annotate("", xy=(0, -1.3), xytext=(W, -1.3), arrowprops=dict(arrowstyle="<->", color="#333", lw=1.1))
ax.text(W / 2, -2.1, "30 cm (box 30 × 30 × 15 cm, sealed lid)", ha="center", va="top", fontsize=14)
ax.annotate("", xy=(-1.3, 0), xytext=(-1.3, H), arrowprops=dict(arrowstyle="<->", color="#333", lw=1.1))
ax.text(-2.0, H / 2, "15 cm", ha="right", va="center", fontsize=14, rotation=90)

ax.text(-5.5, 21.6, "Our vault: one sealed box around the electronics that must survive", fontsize=24, fontweight="bold", va="center")
ax.text(-5.5, 19.6, "Cross-section. Walls drawn thicker than scale.", fontsize=15, color="gray", va="center")
ax.text(-5.5, -5.4, f"Same solar-particle dose as {2 / 2.70 * 10:.1f} mm of solid aluminium, {saved:.0f} kg lighter.", fontsize=17, va="center")
ax.text(-5.5, -7.3, f"10-year solar-particle dose at 53°: {dose53:.2f} krad, {tol / dose53:.0f}× below a commercial chip's ~{tol:.0f} krad.",
        fontsize=17, va="center")
plt.savefig(F + "vault_diagram.png", dpi=120, facecolor="white")
print(f"saved figures/vault_diagram.png  (dose {dose53:.3f} krad, {tol / dose53:.0f}x below {tol:.0f} krad, {saved:.2f} kg lighter)")
