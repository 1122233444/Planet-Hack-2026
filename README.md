# Planet Hack 2026 – Seniors Challenge (G9–Y12)

**Challenge:** Develop a data-driven forecast of solar activity for the 2035 launch window and recommend strategies to protect future space missions from solar storms.

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

## Data sources
- Monthly sunspot number: WDC-SILSO, Royal Observatory of Belgium, Brussels (`SN_m_tot_V2.0.csv`)
- Sunspot area by latitude (butterfly data): D. Hathaway, NASA/MSFC (`bflydata.txt`)

## Reproduce
```bash
pip install numpy pandas matplotlib
python3 scripts/cycles.py
```
