"""Folders of the repository, found from this file's location (works wherever the repo is cloned)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
D = str(ROOT / "data") + "/"        # data/
F = str(ROOT / "figures") + "/"     # figures/


def assert_data(path):
    """Stop if a downloaded file is an HTML error page instead of data (busy servers sometimes send one)."""
    with open(path, "rb") as f:
        head = f.read(300).lower()
    if b"<html" in head or b"<!doctype" in head:
        raise RuntimeError(f"{path} is an HTML page, not data: run scripts/download_data.sh again")
