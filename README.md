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
| Forecast 2035; cross-check with solar activity ↔ radio blackouts (reported incidents) | ✅ | Parts 2–3: SSN median 156, ~30 R3 blackouts in 2035 (true-flux scale); 6 reported incidents and 12 look-alike years |
| Mission protection strategy | ⏳ | Step 5 (next) |
| Video pitch to the ISECG launch panel | ⏳ | Step 5 (next) |

**Headline:** Cycle 26 maximum ≈ **2035.4** (spread of historical analogues ±1.2 yr, full range 2033.6–2038.1) → mid-2035 smoothed sunspot number median **156** (10–90% of the historical-analogue combinations: 99–210) → expect ~**30 X-class flares (R3+ radio blackouts)** and ~440 M-class-or-stronger flares in 2035 on the true-flux scale used for today's alerts (19 and ~290 on the old pre-GOES-16 scale); elevated risk continues to ~2038 because, in equal time windows, X-class flares are 2.5–2.9× more frequent after a maximum than before it.

## Part 1 – Butterfly diagram & first (v1) forecast (the v1 numbers are superseded by Part 2)

![Butterfly diagram](figures/butterfly_c24_c25.png)
![Forecast 2035](figures/forecast_2035.png)

### Key results
| | Value |
|---|---|
| Mean cycle length (Cycles 1–24) | 11.0 ± 1.2 yr |
| Mean rise time (minimum → maximum) | 4.4 ± 1.1 yr |
| Cycle 24 maximum | 2014.3, smoothed SSN 116 |
| Cycle 25 maximum | 2024.8, smoothed SSN 161 (data to Sept 2026; SILSO's last months are provisional) |
| **Cycle 26 minimum (estimate)** | **2030.9 ± 1.2** |
| **Cycle 26 maximum (v1 estimate)** | **2035.3 ± 1.6** (superseded by Part 2: 2035.4 ± 1.2) |

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
- Two estimators of the Cycle 26 maximum (both use the same 15 historical cycles, so they are not independent): from the Cycle 25 minimum 2035.0 ± 1.2, from the Cycle 25 maximum 2035.8 ± 1.1 (± = spread of the historical values, ~68%; full range 2033.6–2038.1); 77% of the 30 estimates fall in 2034–2036. The spread assumes future cycles behave like past ones; the first high-latitude spots of Cycle 26 (~2029–31) will narrow it.
- Historical-analogue ensemble: 210 combinations of 15 cycle lengths × 14 real cycle shapes, i.e. only ~15 independent pieces of information. 2035 mean SSN median 156, 10–90% 99–210; share of combinations above 100: 88%, above 150: 55%, above 50: 100%. These are scenario frequencies within the 1855–2019 record, not calibrated probabilities: a cycle weaker than any in that record is not covered. Check with all cycles 1–24 (adds the less reliable 1755–1855 cycles, including the weak Dalton-minimum cycles): median 139, above 100: 74%, above 50: 97%. Peak year median 2035.0 (10–90% 2033.7–2036.3).

Details: [`results_forecast_v2.txt`](results_forecast_v2.txt)

## Part 3 – NOAA GOES flares and radio blackouts, 1975–2026

![Flares vs sunspots](figures/flares_vs_sunspots.png)
![Flare relations](figures/flares_relation.png)

96,840 GOES flares (NCEI legacy reports 1975–2016, GOES-16 2017–2025, GOES-19 2025–2026).

**Flux scale – read this before comparing with official records.** NOAA multiplied GOES-1 to GOES-15 fluxes by 0.7; GOES-16 onwards report the true flux, and flare classes announced in the GOES-16 era use it (14 May 2024: SWPC X8.7, GOES-16 science data X8.7). We divide the legacy fluxes by 0.7, so the whole record is on this **true-flux scale** – the scale on which 2035 alerts will be issued. Official classes and R levels of older events are therefore lower than ours: 6 Sep 2017 was reported as X9.3 / R3, here it is X14.6 / R4. On 120 flares seen by both GOES-15 and GOES-16 (Feb–Jun 2017) we measure a median ratio of 0.64, 8% below NOAA's 0.70, so the results are also shown with 0.64 and on the old scale:

| Scale | Flares per year per 100 SSN: R1+ / R3+ / R4+ | 2035 median: R1+ / R3+ | 6 Sep 2017 flare |
|---|---|---|---|
| True flux, legacy ÷ 0.70 (main) | 280 / 19 / 0.8 | 438 / 30 | X14.6 |
| True flux, legacy ÷ 0.64 (measured ratio) | 298 / 21 / 0.9 | 466 / 33 | X14.6 |
| Old scale (as reported before GOES-16) | 184 / 12 / 0.5 | 287 / 19 | X10.2 (GOES-15 reported X9.3) |

Everything below is on the true-flux scale.

| Radio-blackout level | r with yearly SSN | flares/yr per 100 SSN | 2035 expected (10% / median / 90%) |
|---|---|---|---|
| R1+ (≥M1) | 0.88 | 280 | 277 / 438 / 587 |
| R2+ (≥M5) | 0.82 | 44 | 43 / 68 / 91 |
| R3+ (≥X1) | 0.80 | 19 | 19 / 30 / 40 |
| R4+ (≥X10) | 0.38 | 0.8 | ~1–2 |

- In all 18 past years with SSN ≥ 100 there was at least one R3 event; 39% had an R4 event (true-flux scale).
- When in the cycle? Maximum = peak of the 13-month smoothed sunspot number (for the double-peaked cycle 23, the higher peak, 2001.9). In equal 1-year windows (complete cycles 21–24), X-class flares per cycle-year: 15.5 one to two years before maximum, 41.5 in the year before, 28.8 in the year after, 39.2 one to two years after, 25.8 two to three years after, 12.5 three to four years after. So there are 2.5× more X-class flares 1–2 years after a maximum than 1–2 years before (157 vs 62), and 2.9× more 2–3 years after than 2–3 years before (103 vs 35): risk stays high for about 3 years after the 2035 maximum (e.g. Halloween 2003, Sept 2005, Sept 2017).

Details: [`results_flares.txt`](results_flares.txt), [`data/flares_per_year.csv`](data/flares_per_year.csv)

### Cross-check with reported incidents and look-alike years (`scripts/incidents.py`)

![Incidents timeline](figures/incidents_timeline.png)

| Incident | Reported then | Level then | Our data (true-flux scale) | Level (true-flux) | Year SSN | From max | What happened |
|---|---|---|---|---|---|---|---|
| March 1989 | X15 | R4 | X21.4 | R5 | 211 | −0.7 yr | Hydro-Québec grid collapse, 6 million without power ~9 h |
| Halloween 2003 | X28+ | R5 | X40.0* | R5 | 99 | +1.9 yr | HF blackouts, polar flights rerouted, WAAS GPS unusable ~30 h, Malmö power cut |
| December 2006 | X9.0 | R3 | X12.9 | R4 | 25 | +5.0 yr | Solar radio burst: GPS receivers on the dayside lose lock |
| September 2017 | X9.3 | R3 | X14.6 | R4 | 22 | +3.4 yr | Hours-long HF blackout during the Caribbean hurricane (Irma) response |
| February 2022 | M1.1 | R1 | M1.1 | R1 | 83 | −2.7 yr | Minor geomagnetic storm: 38 of 49 new Starlink satellites re-enter |
| May 2024 | X8.7 | R3 | X8.7 | R3 | 155 | −0.4 yr | G5 storm: GPS-guided farm machinery disrupted, HF blackouts |

\* GOES saturated near X17 (old scale); X28+ was itself an estimate, so X40 is uncertain – quote "X28+" in the pitch.

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

Checks: A = 14.535 ± 0.005 (statistical) ± 0.016 (systematic = half the Greenwich–USAF/NOAA difference), B = −2.84 ± 0.05 ± 0.10. Sample: 21,003 passages pass the quality cuts; the fit removes 421 outliers beyond 3σ and uses 20,582 (the two era fits remove their own 215 + 207, hence 12,463 + 8,118 = 20,581). Greenwich era 14.55 − 2.92 sin² vs USAF/NOAA era 14.52 − 2.72 sin²; north 14.535 − 2.88 sin² vs south 14.537 − 2.81 sin²; changing the 60° limit to 45° or 75° moves A by ≤ 0.014 °/day. No sunspots above ~40°, so values there are extrapolations (Doppler measurements give ~34 days at the poles).

![Shear of a straight line](figures/differential_rotation_shear.png)

**B. Tracking spots on SDO/HMI images**: 7 daily images, 12–18 Dec 2014 (chosen because B0 ≈ 0 and spots sit at 4°–30°).

*Step by step* (`scripts/manual_walkthrough.py`, the same steps as reading positions with the mouse; whole pixels): on each image read the left/right/top/bottom edge of the disk → centre and radius (e.g. edges 64, 1983, 65, 1984 → centre (1023.5, 1024.5), R = 959.5 px); read the centre of the spot's dark core; convert the time to a Julian Date (JD = 367Y − INT(7(Y + INT((M+9)/12))/4) + INT(275M/9) + D + 1721013.5 + UT/24, e.g. 2014-12-12 23:59:40 UT → 2457004.49977). Records for spot A (NOAA 12236, +30°) and spot E (NOAA 12235, −8°), also in [`data/rotation/manual_walkthrough.csv`](data/rotation/manual_walkthrough.csv):

| Spot | Time (UT) | Julian Date | x (px) | y (px) | Disk centre (px) | Disk radius (px) |
|---|---|---|---|---|---|---|
| A | 2014-12-12 23:59:40 | 2457004.49977 | 302 | 553 | (1023.5, 1024.5) | 959.50 |
| A | 2014-12-13 23:59:40 | 2457005.49977 | 413 | 548 | (1023.5, 1024.0) | 959.25 |
| A | 2014-12-14 23:59:40 | 2457006.49977 | 553 | 542 | (1023.5, 1024.0) | 959.25 |
| A | 2014-12-15 23:59:40 | 2457007.49977 | 718 | 535 | (1023.0, 1024.0) | 959.00 |
| A | 2014-12-16 23:59:40 | 2457008.49977 | 898 | 532 | (1023.0, 1024.5) | 959.25 |
| A | 2014-12-17 23:59:40 | 2457009.49977 | 1082 | 528 | (1024.0, 1024.5) | 959.25 |
| E | 2014-12-11 23:59:40 | 2457003.49977 | 296 | 1149 | (1024.0, 1024.5) | 959.25 |
| E | 2014-12-12 23:59:40 | 2457004.49977 | 455 | 1147 | (1023.5, 1024.5) | 959.50 |
| E | 2014-12-13 23:59:40 | 2457005.49977 | 643 | 1144 | (1023.5, 1024.0) | 959.25 |
| E | 2014-12-14 23:59:40 | 2457006.49977 | 852 | 1143 | (1023.5, 1024.0) | 959.25 |
| E | 2014-12-15 23:59:40 | 2457007.49977 | 1069 | 1142 | (1023.0, 1024.0) | 959.00 |
| E | 2014-12-16 23:59:40 | 2457008.49977 | 1283 | 1145 | (1023.0, 1024.5) | 959.25 |
| E | 2014-12-17 23:59:40 | 2457009.49977 | 1486 | 1143 | (1024.0, 1024.5) | 959.25 |

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

*Automatic tracking of 9 spots* (`scripts/track_sdo.py`, sub-pixel positions, circle fit to the limb; without the PNG originals it uses the JPG copies in `data/sdo/`, which give the same rates within 0.01 °/day):

![Tracking](figures/sdo_tracking.png)
![SDO result](figures/sdo_rotation_result.png)
![Sine fits for all 9 spots](figures/xy_sine_fit_all.png)

| Spot | NOAA | Latitude | Days | ω sidereal (°/day) | 150-yr law | P_syn arcsin / sine fit (d) | P sidereal (d) | Speed (km/s) |
|---|---|---|---|---|---|---|---|---|
| A | 12236 | +29.5° | 6 | 13.71 ± 0.01 | 13.85 | 28.34 / 28.25 | 26.26 | 1.68 |
| B | 12239 | +14.2° | 4 | 14.79 ± 0.04 | 14.37 | 26.12 / 26.10 | 24.34 | 2.02 |
| C | 12240 | +10.3° | 4 | 14.42 ± 0.07 | 14.44 | 26.84 / 26.93 | 24.96 | 1.99 |
| D | 12234 | +3.6° | 5 | 15.17 ± 0.15 | 14.52 | 25.43 / 25.29 | 23.74 | 2.13 |
| E | 12235 | −8.0° | 7 | 14.19 ± 0.01 | 14.48 | 27.32 / 27.33 | 25.38 | 1.97 |
| F | 12241 | −9.4° | 4 | 14.78 ± 0.07 | 14.46 | 26.15 / 26.17 | 24.36 | 2.05 |
| G | 12237 | −13.1° | 6 | 14.08 ± 0.01 | 14.39 | 27.55 / 27.54 | 25.57 | 1.93 |
| H | 12230 | −14.2° | 4 | 14.27 ± 0.06 | 14.36 | 27.14 / 27.12 | 25.22 | 1.94 |
| I | 12242 | −20.9° | 4 | 13.81 ± 0.18 | 14.17 | 28.12 / 27.98 | 26.06 | 1.81 |

- Our latitudes agree with NOAA's to 0.7° on average; arcsin and sine-fit periods agree within 0.14 d for all 9 spots.
- Spots scatter around the 150-year law by 0.36 °/day (mean offset +0.02) — the same as single groups in the long record (0.50 °/day). A fit to the 9 spots alone gives 14.68 ± 0.17 − (4.70 ± 1.69) sin²: one week shows differential rotation, only a large sample measures it precisely.
- A systematic error found and fixed: the first version took the disk edge at half the central brightness, but the limb itself is only ~45% as bright (limb darkening), so the radius came out 954.6 px instead of 959.2 px. That made rates ~0.1 °/day too fast; after the fix the mean offset from the 150-year law fell from +0.12 to +0.02 °/day.

**C. Deriving the equation, and its assumptions** (`scripts/rotation.py`, `scripts/rotation_equation.py`)

![Linearised fit](figures/rotation_equation.png)

1. **One rotation rate per tracked spot.** For every disk passage, the trigonometry of Part B gives the spot's longitude each day; the slope of longitude against time is its rate seen from Earth, and adding Earth's orbital motion gives the true (sidereal) rate ω. Doing this for 21,003 sunspot-group passages (1874–2026) gives 21,003 pairs (latitude φᵢ, rate ωᵢ); our own 9 SDO spots give 9 more.
2. **Choose the form.** The Sun is north–south symmetric (+φ and −φ rotate alike), so only even powers of sin φ can appear. The simplest such form, and the standard one in solar physics, is ω = A + B·sin²φ.
3. **Make it a straight line.** With s = sin²φ the model becomes ω = A + B·s. Plotted against s, the band medians (red dots above) do lie on a straight line.
4. **Least squares (linear regression).** B = Σ(sᵢ − s̄)(ωᵢ − ω̄) / Σ(sᵢ − s̄)², A = ω̄ − B·s̄ (A is the rate at the equator, s = 0). Fitted to all single groups after removing 421 outliers beyond 3 standard deviations (20,582 left); errors from 200 bootstrap resamples.
5. **Result: A = 14.535 ± 0.005 (stat.) ± 0.016 (syst.) °/day, B = −2.84 ± 0.05 (stat.) ± 0.10 (syst.) °/day → ω(φ) = 14.54 − 2.84 sin²φ °/day.** Systematic = half the difference between the Greenwich and USAF/NOAA datasets.
   - A line through the 2.5°-band medians gives 14.48 − 2.77 sin²φ: the distribution of single groups is skewed (young groups rotate fast), so its mean sits a little above its median.
   - Adding a C·sin⁴φ term gives C = −0.10 ± 0.43, i.e. zero: within ±40° the sin²φ term is enough.
   - Our 9 SDO spots alone give 14.68 ± 0.17 − (4.70 ± 1.69) sin²φ: same trend, much larger error.
6. **Period and speed.** P(φ) = 360/ω(φ) days. The surface speed is the angular rate times the radius of the latitude circle: v = ω·(π/180)/86400 · R☉·cos φ, so **v(φ) = 2.043 · cos φ · (1 − 0.196 sin²φ) km/s** (2.04 km/s at the equator, 1.95 at 15°, 1.68 at 30°).

Assumptions:
1. The Sun is a perfect sphere.
2. It is seen from far away (orthographic projection). In reality we see slightly less than a hemisphere: 0.27° at the limb, negligible.
3. Spots move only with the surface, at a constant rate over a few days. Not exactly true for single spots (e.g. spot D), hence the large sample.
4. Rotation depends only on latitude and is north–south symmetric, so it can be written as A + B·sin²φ.
5. Images have solar north up (P = 0); checked against NOAA latitudes (0.7° mean difference).
6. B0 = 0 in the simple formulas (B0 was −0.5° to −1.3° on our dates); the full method includes B0.
7. Earth's orbital motion is 0.9856 °/day for synodic → sidereal (truly 0.953–1.019, at most ±0.03 °/day); the full method uses the exact value.
8. R☉ = 695,700 km (IAU nominal value).
9. Image times are exact (SDO time stamps, to the second).
10. The equation is valid only within ±40° latitude, where sunspots exist.

Details: [`results_rotation.txt`](results_rotation.txt), [`results_sdo_tracking.txt`](results_sdo_tracking.txt), [`results_manual_walkthrough.txt`](results_manual_walkthrough.txt), [`results_sine_fit_all.txt`](results_sine_fit_all.txt), [`results_rotation_equation.txt`](results_rotation_equation.txt)

## Data sources
- Monthly sunspot number: WDC-SILSO, Royal Observatory of Belgium, Brussels – https://www.sidc.be/SILSO/datafiles (`SN_m_tot_V2.0.csv`)
- Sunspot area by latitude (butterfly data) and daily sunspot-group positions (Greenwich/RGO 1874–1976, USAF/NOAA 1977–2026): D. Hathaway – http://solarcyclescience.com/AR_Database/ (`bflydata.txt`, `gYYYY.txt`; also at https://solarscience.msfc.nasa.gov/greenwch.shtml)
- Solar flares: NOAA NCEI GOES XRS flare reports 1975–2017 – https://www.ngdc.noaa.gov/stp/space-weather/solar-data/solar-features/solar-flares/x-rays/goes/xrs/ ; GOES-16 / GOES-19 XRS L2 flare summaries 2017–2026 – https://data.ngdc.noaa.gov/platforms/solar-space-observing-satellites/goes/
- Solar images: SDO/HMI continuum via the Helioviewer API – https://api.helioviewer.org (viewer: https://helioviewer.org)
- Exact download commands: [`scripts/download_data.sh`](scripts/download_data.sh)

## References (methods)
- Meeus, J. 1998, *Astronomical Algorithms*, 2nd ed., ch. 25 and 29 (solar ephemeris: B0, L0, P)
- Hathaway, D., Wilson, R. & Reichmann, E. 1994, Solar Physics 151, 177 (shape of the sunspot cycle)
- Snodgrass, H. & Ulrich, R. 1990, ApJ 351, 309 (rotation of Doppler features)
- Balthasar, H., Vázquez, M. & Wöhl, H. 1986, A&A 155, 87 (sunspot-group rotation from Greenwich data)

## Reproduce
All scripts find `data/` and `figures/` relative to the repository, so they run wherever it is cloned.
```bash
pip install -r requirements.txt      # versions used for the results (Python 3.13)
bash scripts/download_data.sh        # raw flare and sunspot-group files (~60 MB) are not stored in the repo
bash scripts/run_all.sh              # runs every script below in order and rewrites results_*.txt
```
Or one by one:
```bash
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
