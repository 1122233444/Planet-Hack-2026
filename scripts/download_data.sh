#!/usr/bin/env bash
# Download all raw data used by the analysis into data/ (about 60 MB, a few minutes).
# A busy server sometimes answers with an HTML error page instead of the file, so every file is
# checked and fetched again until it is real data; the script stops with an error if one never is.
set -euo pipefail
DATA="$(cd "$(dirname "$0")/../data" && pwd)"

is_html() { head -c 300 "$1" | grep -qi "<!doctype html\|<html"; }
fetch() {   # fetch URL [output file]
  local out="${2:-$(basename "$1")}"
  for i in 1 2 3 4 5 6; do
    if curl -fsSL --retry 5 --retry-delay 3 --retry-all-errors -o "$out" "$1" && ! is_html "$out"; then
      return 0
    fi
    sleep $((i * 5))
  done
  echo "FAILED to download $1" >&2; return 1
}
export -f is_html fetch

cd "$DATA"
fetch https://www.sidc.be/SILSO/DATA/SN_m_tot_V2.0.csv
fetch http://solarcyclescience.com/AR_Database/bflydata.txt

# GOES X-ray flare lists: NCEI reports 1975-2017, GOES-16 summary 2017-2025, GOES-19 daily files 2025-
mkdir -p flares/g19 && cd flares
B=https://www.ngdc.noaa.gov/stp/space-weather/solar-data/solar-features/solar-flares/x-rays/goes/xrs
for y in $(seq 1975 2016) 2017-ytd; do fetch "$B/goes-xrs-report_$y.txt"; done
fetch https://data.ngdc.noaa.gov/platforms/solar-space-observing-satellites/goes/goes16/l2/data/xrsf-l2-flsum_science/sci_xrsf-l2-flsum_g16_s20170209_e20250407_v2-2-2.nc
G=https://data.ngdc.noaa.gov/platforms/solar-space-observing-satellites/goes/goes19/l2/data/xrsf-l2-flsum_science
cd g19
for y in 2025 2026; do for m in 01 02 03 04 05 06 07 08 09 10 11 12; do
  { curl -fsS --retry 3 "$G/$y/$m/" 2>/dev/null || true; } | { grep -o 'sci_xrsf[^"]*\.nc' || true; } | sort -u | sed "s|^|$G/$y/$m/|"
done; done | xargs -P 4 -I{} bash -c 'fetch "$1"' _ {}

# Daily sunspot-group positions 1874-2026 (D. Hathaway: Greenwich + USAF/NOAA), for rotation.py
mkdir -p "$DATA/groups" && cd "$DATA/groups"
seq 1874 2026 | xargs -P 3 -I{} bash -c 'fetch "http://solarcyclescience.com/AR_Database/g$1.txt"' _ {}

# Final check over everything
bad=$(grep -li "<!doctype html\|<html" "$DATA"/groups/*.txt "$DATA"/flares/*.txt "$DATA"/*.txt "$DATA"/*.csv 2>/dev/null || true)
if [ -n "$bad" ]; then echo "These files are HTML pages, not data: $bad" >&2; exit 1; fi
echo "All data downloaded and checked."
# The SDO/HMI images for track_sdo.py: JPG copies are in data/sdo/; the script can fetch the PNG originals.
