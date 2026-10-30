"""Shared look of the video / slide figures: 16:9 at 1920x1080, dark 'space' theme, large text."""
import os, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.text import Text
from paths import F

OUT = F + "video/"
os.makedirs(OUT, exist_ok=True)

BG, PANEL = "#0B1221", "#141E33"
TXT, MUT, GRID = "#F1F3F5", "#9AA5B8", "#243049"
SUN, RED, CYAN, GREEN, PURPLE, BLUE = "#F5A524", "#FF5A5F", "#3BC9DB", "#51CF66", "#B197FC", "#4DABF7"

plt.rcParams.update({
    "font.family": "Inter", "font.size": 18, "mathtext.fontset": "dejavusans",
    "figure.facecolor": BG, "axes.facecolor": BG, "savefig.facecolor": BG,
    "axes.edgecolor": GRID, "axes.labelcolor": TXT, "text.color": TXT,
    "xtick.color": MUT, "ytick.color": MUT, "xtick.labelsize": 16, "ytick.labelsize": 16,
    "axes.labelsize": 18, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8,
    "axes.spines.top": False, "axes.spines.right": False, "legend.frameon": False,
    "legend.fontsize": 15, "lines.linewidth": 2.5, "axes.axisbelow": True,
    "axes.unicode_minus": True,
})

BODY = [0.075, 0.14, 0.885, 0.66]       # default plot area under the title, room for an x label


def canvas(title, subtitle=None, source=None):
    """1920x1080 figure with a conclusion-style title, a subtitle and a source line."""
    fig = plt.figure(figsize=(16, 9), dpi=120)
    fig.text(0.045, 0.94, title, fontsize=32, fontweight="bold", color=TXT, va="top")
    if subtitle:
        fig.text(0.045, 0.862, subtitle, fontsize=18, color=MUT, va="top")
    if source:
        fig.text(0.045, 0.028, source, fontsize=12, color=MUT)
    fig.text(0.955, 0.028, "Planet Hack 2026 · Seniors Challenge", fontsize=12, color=MUT, ha="right")
    return fig


def num(x, fmt):
    """Format a number with a typographic minus sign."""
    return format(x, fmt).replace("-", "−")


def _texts(fig):
    """Visible text of the figure: figure text, annotations, labels, legends and the tick labels inside the view."""
    out = list(fig.texts)
    axes = [a for a in fig.axes if a.axison]
    axes += [c for a in axes for c in a.child_axes]
    for ax in axes:
        out += list(ax.texts) + [ax.xaxis.label, ax.yaxis.label, ax.title]
        lo, hi = sorted(ax.get_xlim())
        out += [t for t in ax.get_xticklabels() if lo - 1e-9 <= t.get_position()[0] <= hi + 1e-9]
        lo, hi = sorted(ax.get_ylim())
        out += [t for t in ax.get_yticklabels() if lo - 1e-9 <= t.get_position()[1] <= hi + 1e-9]
        if ax.get_legend():
            out += list(ax.get_legend().get_texts())
    return [t for t in out if t.get_visible() and t.get_text().strip()]


def check_layout(fig, name):
    """Warn about text that overlaps other text or runs off the 1920x1080 frame (leader lines are not checked)."""
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    W, H = fig.canvas.get_width_height()
    boxes = []
    for t in _texts(fig):
        b = Text.get_window_extent(t, r)                  # text only, without an annotation's arrow
        if b.width == 0:
            continue
        if b.x0 < -1 or b.y0 < -1 or b.x1 > W + 1 or b.y1 > H + 1:
            print(f"  LAYOUT {name}: off frame: {t.get_text()[:40]!r}")
        boxes.append((t, b))
    for i, (t1, b1) in enumerate(boxes):
        for t2, b2 in boxes[i + 1:]:
            if b1.overlaps(b2):
                print(f"  LAYOUT {name}: {t1.get_text()[:35]!r} overlaps {t2.get_text()[:35]!r}")


def save(fig, name):
    check_layout(fig, name)
    fig.savefig(OUT + name, dpi=120, facecolor=BG)
    plt.close(fig)
    print("saved figures/video/" + name)
