"""Step-by-step measurement of two sunspots, following exactly the steps you would take by hand.

For every image (data/sdo/hmi_*.jpg):
  1. disk: along the horizontal and vertical lines through the middle, find the first and last
     bright pixel (left/right/top/bottom edge) -> centre = middle of the edges, radius = half the width;
  2. spot: the pixel at the centre of the spot's dark core (umbra);
  3. time: the observation time, turned into a Julian Date with the classic formula.
All readings are whole pixels, like reading the position under the mouse. manual_rotation.py then
does the trigonometry (arcsin method and sine-curve fit).
"""
import json, numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image
from scipy import ndimage
from solar_geometry import jd_from_date
import manual_rotation as mr

D = "/home/user/planethack/data/"; F = "/home/user/planethack/figures/"
SPOTS = ["A", "E"]       # NOAA 12236 at +30° and NOAA 12235 at -8°: two very different latitudes
auto = pd.read_csv(D + "rotation/sdo_spot_positions.csv", dtype={"spot": str})   # which dark dot is which


def measure_disk(g):
    # the edge is where the disk turns black: brightness falls from ~85 to ~0 within about three pixels,
    # and a quarter of the normal disk brightness (~47) sits in the middle of that drop
    edge = 0.25 * np.median(g[g > 50])
    yc, xc = (np.array(g.shape) - 1) / 2
    for _ in range(2):                                # 2nd pass: lines through the measured centre
        row, col = g[int(round(yc)), :], g[:, int(round(xc))]
        left, right = np.nonzero(row > edge)[0][[0, -1]]
        top, bottom = np.nonzero(col > edge)[0][[0, -1]]
        xc, yc = (left + right) / 2, (top + bottom) / 2
    return dict(disk_left_px=int(left), disk_right_px=int(right), disk_top_px=int(top), disk_bottom_px=int(bottom),
                disk_cx_px=xc, disk_cy_px=yc, disk_r_px=((right - left) + (bottom - top)) / 4)


def measure_spot(g, x0, y0, half=20):
    win = g[y0 - half:y0 + half + 1, x0 - half:x0 + half + 1].astype(float)
    quiet, dark = np.percentile(win, 90), win.min()
    lab, _ = ndimage.label(win < dark + 0.35 * (quiet - dark))        # the darkest core (umbra)
    core = lab == lab[np.unravel_index(win.argmin(), win.shape)]
    yy, xx = np.nonzero(core); w = quiet - win[yy, xx]
    return int(round(x0 - half + (w * xx).sum() / w.sum())), int(round(y0 - half + (w * yy).sum() / w.sum()))


rows = []
for img in sorted(auto.image.unique()):
    g = np.asarray(Image.open(D + "sdo/" + img).convert("L"), float)
    meta = json.load(open(D + "sdo/" + img.replace(".jpg", ".json")))
    t = pd.Timestamp(meta["date"])
    disk = measure_disk(g)
    jd = jd_from_date(t.year, t.month, t.day, t.hour + t.minute / 60 + t.second / 3600)
    for spot in SPOTS:
        a = auto[(auto.spot == spot) & (auto.image == img)]
        if not len(a): continue
        x, y = measure_spot(g, int(round(a.x_px.iloc[0])), int(round(a.y_px.iloc[0])))
        rows.append(dict(spot=spot, noaa=a.noaa.iloc[0], image=img, time_utc=f"{t:%Y-%m-%d %H:%M:%S}",
                         jd=round(jd, 5), x_px=x, y_px=y, **disk))
m = pd.DataFrame(rows).sort_values(["spot", "jd"]).reset_index(drop=True)
m.to_csv(D + "rotation/manual_walkthrough.csv", index=False)

# ---------- show the maths for one image ----------
t = pd.Timestamp(m.time_utc.iloc[0]); h = t.hour + t.minute / 60 + t.second / 3600
Y, M, Dd = t.year, t.month, t.day
print(f"Step 3 example, Julian Date of {t} UT:")
print(f"   JD = 367×{Y} − INT(7×({Y} + INT(({M}+9)/12))/4) + INT(275×{M}/9) + {Dd} + 1721013.5 + {h:.4f}/24")
print(f"      = {367 * Y} − {(7 * (Y + (M + 9) // 12)) // 4} + {(275 * M) // 9} + {Dd} + 1721013.5 + {h / 24:.5f}"
      f" = {jd_from_date(Y, M, Dd, h):.5f}")
r = m.iloc[0]
print(f"\nStep 1 example ({r.image}): left edge x = {r.disk_left_px}, right edge x = {r.disk_right_px}, "
      f"top edge y = {r.disk_top_px}, bottom edge y = {r.disk_bottom_px}")
print(f"   centre = (({r.disk_left_px}+{r.disk_right_px})/2, ({r.disk_top_px}+{r.disk_bottom_px})/2) = "
      f"({r.disk_cx_px}, {r.disk_cy_px});  radius = (({r.disk_right_px}−{r.disk_left_px}) + "
      f"({r.disk_bottom_px}−{r.disk_top_px}))/4 = {r.disk_r_px}")
a = auto[auto.image == r.image].iloc[0]
print(f"   (automatic circle fit on the same image: centre ({a.disk_cx_px}, {a.disk_cy_px}), radius {a.disk_r_px})")
cmd_ok = np.abs(mr.load(D + "rotation/manual_walkthrough.csv").cmd.values) <= mr.MAX_CMD
for spot in SPOTS:
    p = m[(m.spot == spot) & cmd_ok]                                  # first and last usable reading
    for _, q in p.iloc[[0, -1]].iterrows():
        X = (q.x_px - q.disk_cx_px) / q.disk_r_px; Yn = -(q.y_px - q.disk_cy_px) / q.disk_r_px
        lat = np.degrees(np.arcsin(Yn)); cmd = np.degrees(np.arcsin(X / np.cos(np.radians(lat))))
        print(f"Step 2+4, spot {spot} on {q.time_utc}: pixel ({q.x_px}, {q.y_px}) -> X = ({q.x_px}−{q.disk_cx_px})/{q.disk_r_px}"
              f" = {X:+.4f}, Y = −({q.y_px}−{q.disk_cy_px})/{q.disk_r_px} = {Yn:+.4f} -> latitude {lat:+.2f}°, CMD {cmd:+.2f}°")
print()

# ---------- the trigonometry: both methods ----------
mm = mr.load(D + "rotation/manual_walkthrough.csv")
res, fits = mr.analyse(mm)
mr.report(mm, res)
mr.plot(mm, res, fits, F + "xy_sine_fit.png")
auto_res = pd.read_csv(D + "rotation/sdo_spot_results.csv", dtype={"label": str}).set_index("label")
print("\nCompared with the automatic tracking (sub-pixel positions, circle fit for the disk):")
for _, r in res.iterrows():
    print(f"   spot {r.spot}: whole-pixel readings give {r.omega_sid:.2f} °/day, automatic {auto_res.omega[r.spot]:.2f} °/day")

# ---------- figure: what each reading looks like ----------
img = m[m.spot == "A"].image.iloc[0]                                  # first image with both spots
g = np.asarray(Image.open(D + "sdo/" + img).convert("L"), float)
r = m[m.image == img].iloc[0]
fig = plt.figure(figsize=(15, 8.6))
gs = fig.add_gridspec(3, 4)
ax = fig.add_subplot(gs[:, :2])
ax.imshow(g, cmap="gray", vmin=0, vmax=255)
ax.axhline(r.disk_cy_px, c="tab:cyan", lw=0.8); ax.axvline(r.disk_cx_px, c="tab:cyan", lw=0.8)
pts = [("left", r.disk_left_px, r.disk_cy_px), ("right", r.disk_right_px, r.disk_cy_px),
       ("top", r.disk_cx_px, r.disk_top_px), ("bottom", r.disk_cx_px, r.disk_bottom_px)]
for lab, x, y in pts: ax.plot(x, y, "o", c="tab:cyan", ms=6)
ax.plot(r.disk_cx_px, r.disk_cy_px, "+", c="tab:cyan", ms=14, mew=2)
for _, q in m[m.image == img].iterrows():
    ax.plot(q.x_px, q.y_px, "o", mfc="none", mec="tab:red", ms=16, mew=2)
    ax.text(q.x_px + 30, q.y_px - 30, f"{q.spot} ({q.x_px}, {q.y_px})", color="tab:red", fontsize=11, fontweight="bold")
ax.set_title(f"{r.time_utc} UT (JD {r.jd:.5f}): centre ({r.disk_cx_px}, {r.disk_cy_px}), radius {r.disk_r_px} px",
             fontsize=10); ax.axis("off")
for k, (lab, x, y) in enumerate(pts):
    a = fig.add_subplot(gs[k // 2, 2 + k % 2]); x, y = int(round(x)), int(round(y))
    a.imshow(g[y - 12:y + 13, x - 12:x + 13], cmap="gray", vmin=0, vmax=255, extent=(x - 12.5, x + 12.5, y + 12.5, y - 12.5))
    a.plot(x, y, "s", mfc="none", mec="tab:cyan", ms=10, mew=2)
    a.set_title(f"{lab} edge: " + (f"x = {x}" if lab in ("left", "right") else f"y = {y}"), fontsize=10)
for k, (_, q) in enumerate(m[m.image == img].iterrows()):
    a = fig.add_subplot(gs[2, 2 + k]); x, y = int(q.x_px), int(q.y_px)
    a.imshow(g[y - 20:y + 21, x - 20:x + 21], cmap="gray", vmin=0, vmax=255, extent=(x - 20.5, x + 20.5, y + 20.5, y - 20.5))
    a.axhline(y, c="tab:red", lw=0.8); a.axvline(x, c="tab:red", lw=0.8)
    a.set_title(f"spot {q.spot} dark core: ({x}, {y})", fontsize=10)
fig.suptitle("Reading positions off the image, step by step (zoomed squares: each pixel is visible)", fontsize=12)
plt.tight_layout(); plt.savefig(F + "manual_steps.png", dpi=120)
