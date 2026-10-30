# Planet Hack 2026 – Seniors Challenge (G9–Y12)

**Challenge:** Develop a data-driven forecast of solar activity for the 2035 launch window and recommend strategies to protect future space missions from solar storms.

📖 **中文说明（方法、局限、蝴蝶图解读、概念）：[docs/README_zh.md](docs/README_zh.md)**

**Headline:** Cycle 26 maximum ≈ **2035.4 ± 1.2** → mid-2035 smoothed sunspot number median **156** (80% range 99–210) → expect ~**30 X-class flares (R3+ radio blackouts)** and ~440 M-class-or-stronger flares in 2035; elevated risk continues to ~2038 because big flares cluster *after* maximum.

## Part 1 – Butterfly diagram & Cycle 26 forecast

![Butterfly diagram](figures/butterfly_c24_c25.png)
![Forecast 2035](figures/forecast_2035.png)

### Key results
| | Value |
|---|---|
| Mean cycle length (Cycles 1–24) | 11.0 ± 1.2 yr |
| Mean rise time (minimum → maximum) | 4.4 ± 1.1 yr |
| Cycle 24 maximum | 2014.3, smoothed SSN 116 |
| Cycle 25 maximum | 2024.8, smoothed SSN 161 |
| **Cycle 26 minimum (estimate)** | **2030.9 ± 1.2** |
| **Cycle 26 maximum (estimate)** | **2035.3 ± 1.6** |

**Conclusion:** the 2035 launch window very likely falls close to the maximum of Solar Cycle 26.
Scenario peak strengths (smoothed SSN): weak like Cycle 24 ≈ 116, like Cycle 25 ≈ 161, historical average ≈ 178.

**Spörer's law** is visible in the data: mean sunspot latitude fell from 24° (2009) to 7° (2019) during Cycle 24, and Cycle 25 restarted at 19° (2020), drifting to 12° by 2026.

Full numbers: [`results_cycles.txt`](results_cycles.txt), [`data/cycles_table.csv`](data/cycles_table.csv).

### Limitations
Timing of the maximum is fairly predictable from statistics; the *strength* is not, so we show scenarios. Better amplitude predictions use the Sun's polar magnetic field near solar minimum (~2030).

## Part 2 – Improved forecast (v2): verified data, reliable cycles, analogue ensemble

![Ensemble forecast](figures/forecast_v2_ensemble.png)

- Hand-typed cycle minima agree with minima found in the data to within 0.23 yr.
- Using only reliable cycles 10–25: length 10.93 ± 0.75 yr, rise 4.17 ± 0.70 yr. Waldmeier effect: corr(peak, rise) = −0.61.
- Two independent timings of the Cycle 26 maximum: from the Cycle 25 minimum 2035.0 ± 1.2, from the Cycle 25 maximum 2035.8 ± 1.1; 77% of the 30 estimates fall in 2034–2036.
- 210-member historical-analogue ensemble (real cycle shapes): 2035 mean SSN median 156, 10–90% 99–210; P(>100) = 88%, P(>150) = 55%; peak year median 2035.0 (10–90% 2033.7–2036.3).

Details: [`results_forecast_v2.txt`](results_forecast_v2.txt)

## Part 3 – NOAA GOES flares and radio blackouts, 1975–2026

![Flares vs sunspots](figures/flares_vs_sunspots.png)
![Flare relations](figures/flares_relation.png)

96,840 GOES flares (NCEI legacy reports 1975–2016, GOES-16 2017–2025, GOES-19 2025–2026), all put on today's NOAA flux scale (legacy fluxes ÷ 0.7; checked empirically: median ratio 0.64 on 120 overlapping flares).

| Radio-blackout level | r with yearly SSN | flares/yr per 100 SSN | 2035 expected (10% / median / 90%) |
|---|---|---|---|
| R1+ (≥M1) | 0.88 | 280 | 277 / 438 / 587 |
| R2+ (≥M5) | 0.82 | 44 | 43 / 68 / 91 |
| R3+ (≥X1) | 0.80 | 19 | 19 / 30 / 40 |
| R4+ (≥X10) | 0.38 | 0.8 | ~1–2 |

- In all 18 past years with SSN ≥ 100 there was at least one R3 event; 39% had an R4 event.
- X-class flares (cycles 21–25): 17% in the rising phase, 41% within ±1 yr of maximum, 34% 1–3 yr after, 9% later → risk stays high for several years after the 2035 maximum (e.g. Halloween 2003, Sept 2005, Sept 2017).

Details: [`results_flares.txt`](results_flares.txt), [`data/flares_per_year.csv`](data/flares_per_year.csv)

## Data sources
- Monthly sunspot number: WDC-SILSO, Royal Observatory of Belgium, Brussels (`SN_m_tot_V2.0.csv`)
- Sunspot area by latitude (butterfly data): D. Hathaway, NASA/MSFC (`bflydata.txt`)
- Solar flares: NOAA NCEI GOES XRS flare reports (1975–2017) and GOES-16 / GOES-19 XRS L2 flare summaries (2017–2026)

## Reproduce
```bash
pip install numpy pandas scipy matplotlib xarray netCDF4
bash scripts/download_data.sh      # raw flare files are not stored in the repo
python3 scripts/cycles.py          # Part 1
python3 scripts/forecast_v2.py     # Part 2
python3 scripts/flares.py          # Part 3 (needs forecast_v2 output)
```
