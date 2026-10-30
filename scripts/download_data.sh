#!/usr/bin/env bash
# Download all raw data used by the analysis into data/
set -e
cd "$(dirname "$0")/../data"
curl -sSO https://www.sidc.be/SILSO/DATA/SN_m_tot_V2.0.csv
curl -sSO http://solarcyclescience.com/AR_Database/bflydata.txt
mkdir -p flares/g19 && cd flares
B=https://www.ngdc.noaa.gov/stp/space-weather/solar-data/solar-features/solar-flares/x-rays/goes/xrs
for y in $(seq 1975 2016) 2017-ytd; do curl -sSO "$B/goes-xrs-report_$y.txt"; done
curl -sSO https://data.ngdc.noaa.gov/platforms/solar-space-observing-satellites/goes/goes16/l2/data/xrsf-l2-flsum_science/sci_xrsf-l2-flsum_g16_s20170209_e20250407_v2-2-2.nc
G=https://data.ngdc.noaa.gov/platforms/solar-space-observing-satellites/goes/goes19/l2/data/xrsf-l2-flsum_science
cd g19
for y in 2025 2026; do for m in 01 02 03 04 05 06 07 08 09 10 11 12; do
  curl -sS "$G/$y/$m/" 2>/dev/null | grep -o 'sci_xrsf[^"]*\.nc' | sort -u | sed "s|^|$G/$y/$m/|"
done; done | xargs -P 8 -n 1 curl -sSO
