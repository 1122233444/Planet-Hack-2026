#!/usr/bin/env bash
# Re-run the whole analysis in order and rewrite the results_*.txt files.
# First time: pip install -r requirements.txt && bash scripts/download_data.sh   (needs internet)
set -e
cd "$(dirname "$0")"
run() { echo "== $1"; python3 "$1" > "../$2"; }
run cycles.py             results_cycles.txt
run forecast_v2.py        results_forecast_v2.txt
run flares.py             results_flares.txt          # needs forecast_v2.py output
run rotation.py           results_rotation.txt
run track_sdo.py          results_sdo_tracking.txt    # needs rotation.py output; uses data/sdo images
run manual_rotation.py    results_sine_fit_all.txt
run manual_walkthrough.py results_manual_walkthrough.txt
run rotation_equation.py  results_rotation_equation.txt
run butterfly_own.py      results_butterfly_own.txt
run incidents.py          results_incidents.txt       # needs flares.py output
run video_figures.py      results_video_figures.txt   # 16:9 figures for the video and slides (figures/video/)
echo "== self-test (needs sunpy)"; python3 solar_geometry.py
