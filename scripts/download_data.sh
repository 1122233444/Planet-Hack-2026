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
fetch https://kp.gfz-potsdam.de/app/files/Kp_ap_Ap_SN_F107_since_1932.txt   # Kp index, for geomagnetic.py
# NOAA solar proton events 1976-2017 (protons.py) are an HTML page, kept in the repository as data/sep_list.html

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

# GOES proton detectors for the big proton events (shielding.py): all of 1989 (GOES-7), Oct-Nov 2003 (GOES-10),
# Jan 2005 (GOES-11), Sep 2017 (GOES-13); 5-minute averages, about 45 MB
mkdir -p "$DATA/goes_protons" && cd "$DATA/goes_protons"
P=https://www.ncei.noaa.gov/data/goes-space-environment-monitor/access/avg
for md in 01:31 02:28 03:31 04:30 05:31 06:30 07:31 08:31 09:30 10:31 11:30 12:31; do
  m=${md%:*}; d=${md#*:}; fetch "$P/1989/$m/goes07/csv/g07_eps_5m_1989${m}01_1989${m}${d}.csv"
done
fetch "$P/2003/10/goes10/csv/g10_eps_5m_20031001_20031031.csv"
fetch "$P/2003/11/goes10/csv/g10_eps_5m_20031101_20031130.csv"
fetch "$P/2005/01/goes11/csv/g11_eps_5m_20050101_20050131.csv"
fetch "$P/2017/09/goes13/csv/g13_epead_cpflux_5m_20170901_20170930.csv"

# Final check over everything
bad=$(grep -li "<!doctype html\|<html" "$DATA"/groups/*.txt "$DATA"/flares/*.txt "$DATA"/*.txt "$DATA"/*.csv 2>/dev/null || true)
if [ -n "$bad" ]; then echo "These files are HTML pages, not data: $bad" >&2; exit 1; fi
echo "All data downloaded and checked."
# The SDO/HMI images for track_sdo.py: JPG copies are in data/sdo/; the script can fetch the PNG originals.
