# Planet Hack 2026 – Seniors Challenge (G9–Y12)

**Challenge:** Develop a data-driven forecast of solar activity for the 2035 launch window and recommend strategies to protect future space missions from solar storms.

📖 **中文说明（方法、局限、蝴蝶图解读、概念）：[docs/README_zh.md](docs/README_zh.md)**

### Challenge checklist
| Requirement | Status | Where |
|---|---|---|
| Track ≥ 2 sunspots at different latitudes on SDO/HMI images; record x, y pixels and Julian Dates | ✅ | Part 4B: spots A (+30°) and E (−8°) measured step by step (`data/rotation/manual_walkthrough.csv`); 9 spots tracked automatically |
| Trigonometric rotation period at each latitude; plot x and y vs time, fit a sine curve, estimate the rate of motion | ✅ | Part 4B: arcsin method and sine-curve fit for every spot |
| Quantify differential rotation; derive an equation, state the assumptions | ✅ | Part 4C: ω = 14.54 − 2.84 sin²φ °/day, v = 2.04 cos φ (1 − 0.196 sin²φ) km/s, 10 assumptions |
| Own butterfly diagram of the last two cycles; cycle period and next maximum from it | ✅ | Part 1B: period 11.2 yr, next maximum ≈ 2036.4 (all 12 cycles: 2034.9 ± 1.3) |
| Forecast 2035; cross-check with solar activity ↔ radio blackouts (reported incidents) | ✅ | Parts 2–3: SSN median 156, ~30 R3 blackouts in 2035; 6 reported incidents and 12 look-alike years |
| Mission protection strategy | ⏳ | Step 5 (next) |
| Video pitch to the ISECG launch panel | ⏳ | Step 5 (next) |

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

### Part 1B – Our own butterfly diagram, and the cycle period read off it (`scripts/butterfly_own.py`)

![Own butterfly diagram](figures/butterfly_own.png)

Built directly from the latitude of 3,647 sunspot groups (2006–2026). A cycle starts when more than half of the sunspot area (1-year running total) sits at |latitude| ≥ 15°, after a stretch in which almost all of it was below 15° (starts at least 7 years apart). Maximum = peak of the 1-year mean sunspot area.

- Cycle 24 starts 2008.77, cycle 25 starts 2019.97 (official minima 2008.9 and 2019.9; over 1874–2026 the 13 detected starts differ from the official minima by +0.11 yr on average, 0.6 yr at most).
- **Period of cycle 24: 11.2 yr.** Rise to maximum: 5.67 yr (cycle 24), 4.71 yr (cycle 25).
- **Next maximum from the last two cycles: 2019.97 + 11.20 + 5.19 ≈ 2036.4**; from all 12 complete cycles since 1890: 2034.9 ± 1.3. Both agree with the sunspot-number forecast (2035.4 ± 1.2).
- At maximum the mean spot latitude is 15.5° ± 2.8° (cycle 24: 12.6°, cycle 25: 13.9°) — a marker to watch for in cycle 26.

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

### Cross-check with reported incidents and look-alike years (`scripts/incidents.py`)

![Incidents timeline](figures/incidents_timeline.png)

| Incident | Reported then | Our data (today's scale) | Blackout | Year SSN | From max | What happened |
|---|---|---|---|---|---|---|
| March 1989 | X15 | X21.4 | R5 | 211 | −0.7 yr | Hydro-Québec grid collapse, 6 million without power ~9 h |
| Halloween 2003 | X28+ | X40.0 | R5 | 99 | +1.9 yr | HF blackouts, polar flights rerouted, WAAS GPS unusable ~30 h, Malmö power cut |
| December 2006 | X9.0 | X12.9 | R4 | 25 | +5.0 yr | Solar radio burst: GPS receivers on the dayside lose lock |
| September 2017 | X9.3 | X14.6 | R4 | 22 | +3.4 yr | Hours-long HF blackout during the Caribbean hurricane (Irma) response |
| February 2022 | M1.1 | M1.1 | R1 | 83 | −2.7 yr | Minor geomagnetic storm: 38 of 49 new Starlink satellites re-enter |
| May 2024 | X8.7 | X8.7 | R3 | 155 | −0.4 yr | G5 storm: GPS-guided farm machinery disrupted, HF blackouts |

Sources: Boteler 2019; NOAA Service Assessment 2004; Cerruti et al. 2008; Redmon et al. 2018; SpaceX 2022, Dang et al. 2022; NOAA SWPC 2024.
Look-alike years (yearly SSN 112–189, the middle half of the 2035 forecast; 12 years since 1978): every one had R3 blackouts (median ~20 per year, range 8–66), 3 of 12 had an R4. Our 2035 forecast (~30 R3, ~440 R1+) is of the same size. Details: [`results_incidents.txt`](results_incidents.txt)

## Part 4 – Differential rotation (Steps 1–2): tracking sunspots with trigonometry

**Result:** sidereal rotation rate of sunspots **ω = 14.54 − 2.84 sin²(latitude) °/day** (21,003 tracked sunspot groups).
Equator: 24.8 days, 2.04 km/s · 30°: 26.0 days, 1.68 km/s · 40°: 26.9 days, 1.44 km/s. Seen from Earth an active region comes back about every **27 days** and needs about **7 days** to rotate from the east limb to face Earth.

**A. Large sample** (`scripts/rotation.py`): daily positions of sunspot groups 1874–2026 (Greenwich + USAF/NOAA, compiled by D. Hathaway; 253,104 positions). For each disk passage (≥ 4 days within 60° of the central meridian) the Carrington longitude is fitted against time; slope + 14.184 °/day = sidereal rate.

![Rotation vs latitude](figures/rotation_vs_latitude.png)

| Latitude | ω (°/day) | Sidereal period | Synodic period (seen from Earth) | Surface speed |
|---|---|---|---|---|
| 0° | 14.54 | 24.8 d | 26.6 d | 2.04 km/s |
| 15° | 14.35 | 25.1 d | 27.0 d | 1.95 km/s |
| 30° | 13.83 | 26.0 d | 28.0 d | 1.68 km/s |
| 40° | 13.36 | 26.9 d | 29.1 d | 1.44 km/s |

Checks: fit errors ±0.005 (A) and ±0.05 (B); Greenwich era 14.55 − 2.92 sin² vs USAF/NOAA era 14.52 − 2.72 sin²; north 14.535 − 2.88 sin² vs south 14.537 − 2.81 sin²; changing the 60° limit to 45° or 75° moves A by ≤ 0.014 °/day. No sunspots above ~40°, so values there are extrapolations (Doppler measurements give ~34 days at the poles).

![Shear of a straight line](figures/differential_rotation_shear.png)

**B. Tracking spots on SDO/HMI images**: 7 daily images, 12–18 Dec 2014 (chosen because B0 ≈ 0 and spots sit at 4°–30°).

*Step by step* (`scripts/manual_walkthrough.py`, the same steps as reading positions with the mouse; whole pixels): on each image read the left/right/top/bottom edge of the disk → centre and radius (e.g. edges 64, 1983, 65, 1984 → centre (1023.5, 1024.5), R = 959.5 px); read the centre of the spot's dark core; convert the time to a Julian Date (JD = 367Y − INT(7(Y + INT((M+9)/12))/4) + INT(275M/9) + D + 1721013.5 + UT/24, e.g. 2014-12-12 23:59:40 UT → 2457004.49977). Records for spot A (NOAA 12236, +30°) and spot E (NOAA 12235, −8°): [`data/rotation/manual_walkthrough.csv`](data/rotation/manual_walkthrough.csv).

![Measurement steps](figures/manual_steps.png)

*Two trigonometric methods* (`scripts/manual_rotation.py`):
1. arcsin: latitude = arcsin(Y), central-meridian distance = arcsin(X / cos lat), with X = (x − xc)/R, Y = −(y − yc)/R; it grows linearly in time, slope = synodic rate.
2. sine fit: x(t) = xc + R cos(lat) · sin(2π(t − t₀)/P); y(t) stays ~constant.

![x and y vs time with sine fits](figures/xy_sine_fit.png)

| Spot | Sine fit (t in JD) | P_syn arcsin / sine | ω sidereal | P sidereal | Speed across disk / true |
|---|---|---|---|---|---|
| A (+29.5°) | x = 1023.4 + 834.6·sin(2π(t − 2457009.18)/28.18) | 28.35 / 28.18 d | 13.79 °/d | 26.10 d | 186 px/d = 1.56 km/s / 1.69 km/s |
| E (−8.0°) | x = 1023.5 + 949.9·sin(2π(t − 2457007.29)/27.33) | 27.32 / 27.33 d | 14.19 °/d | 25.37 d | 218 px/d = 1.83 km/s / 1.98 km/s |

The sine fits leave 0.5 px residuals. The amplitude is fixed to R·cos(lat): with only ~1/5 of a rotation observed, fitting amplitude and period together is unstable.

*Automatic tracking of 9 spots* (`scripts/track_sdo.py`, sub-pixel positions, circle fit to the limb):

![Tracking](figures/sdo_tracking.png)
![SDO result](figures/sdo_rotation_result.png)
![Sine fits for all 9 spots](figures/xy_sine_fit_all.png)

- Our latitudes agree with NOAA's to 0.7° on average; arcsin and sine-fit periods agree within 0.14 d for all 9 spots.
- Spots scatter around the 150-year law by 0.36 °/day (mean offset +0.02) — the same as single groups in the long record (0.50 °/day). A fit to the 9 spots alone gives 14.68 ± 0.17 − (4.70 ± 1.69) sin²: one week shows differential rotation, only a large sample measures it precisely.
- A systematic error found and fixed: the first version took the disk edge at half the central brightness, but the limb itself is only ~45% as bright (limb darkening), so the radius came out 954.6 px instead of 959.2 px. That made rates ~0.1 °/day too fast; after the fix the mean offset from the 150-year law fell from +0.12 to +0.02 °/day.

**C. The equation and its assumptions** (`scripts/rotation_equation.py`)

![Linearised fit](figures/rotation_equation.png)

Against s = sin²(latitude) the rates lie on a straight line, so ω = A + B·s with intercept A and slope B from a least-squares line (through the band medians: 14.48 − 2.77 s; through all single groups: 14.54 − 2.84 s — the mean of a skewed distribution sits a little above its median). Hence
ω(φ) = 14.54 − 2.84 sin²φ °/day, P(φ) = 360/ω(φ) days, **v(φ) = ω·(π/180)/86400·R☉·cos φ = 2.043 cos φ (1 − 0.196 sin²φ) km/s.**

Assumptions: the Sun is a sphere seen from far away (orthographic projection); spots move only with the surface and at a constant rate over a few days; rotation depends only on latitude and is north–south symmetric (hence sin²φ); images have solar north up (checked against NOAA); B0 ≈ 0 for the simple formulas (the full method includes B0); Earth's orbital motion 0.9856 °/day for synodic → sidereal (true range 0.953–1.019); R☉ = 695,700 km; exact image times; valid only within ±40° latitude.

Details: [`results_rotation.txt`](results_rotation.txt), [`results_sdo_tracking.txt`](results_sdo_tracking.txt), [`results_manual_walkthrough.txt`](results_manual_walkthrough.txt), [`results_sine_fit_all.txt`](results_sine_fit_all.txt), [`results_rotation_equation.txt`](results_rotation_equation.txt)

## Data sources
- Monthly sunspot number: WDC-SILSO, Royal Observatory of Belgium, Brussels (`SN_m_tot_V2.0.csv`)
- Sunspot area by latitude (butterfly data): D. Hathaway, NASA/MSFC (`bflydata.txt`)
- Solar flares: NOAA NCEI GOES XRS flare reports (1975–2017) and GOES-16 / GOES-19 XRS L2 flare summaries (2017–2026)
- Sunspot group positions: D. Hathaway, Greenwich (RGO) 1874–1976 and USAF/NOAA 1977–2026 (`gYYYY.txt`)
- Solar images: SDO/HMI continuum via helioviewer.org

## Reproduce
```bash
pip install numpy pandas scipy matplotlib xarray netCDF4 pillow
bash scripts/download_data.sh        # raw flare and sunspot-group files are not stored in the repo
python3 scripts/cycles.py            # Part 1
python3 scripts/forecast_v2.py       # Part 2
python3 scripts/flares.py            # Part 3 (needs forecast_v2 output)
python3 scripts/rotation.py          # Part 4A
python3 scripts/track_sdo.py         # Part 4B (downloads the SDO images; needs rotation.py output)
python3 scripts/manual_walkthrough.py               # Part 4B: spots A and E step by step
python3 scripts/manual_rotation.py my_spots.csv out.png   # your own hand measurements, both methods
python3 scripts/rotation_equation.py # Part 4C
python3 scripts/butterfly_own.py     # Part 1B
python3 scripts/incidents.py         # Part 3 cross-check (needs flares.py output)
python3 scripts/solar_geometry.py    # self-test against SunPy (pip install sunpy)
```
