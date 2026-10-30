"""Folders of the repository, found from this file's location (works wherever the repo is cloned)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
D = str(ROOT / "data") + "/"        # data/
F = str(ROOT / "figures") + "/"     # figures/
