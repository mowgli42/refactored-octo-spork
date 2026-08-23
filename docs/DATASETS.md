# Flight-test datasets for refactored-octo-spork

The original goal was to ingest **known flight-test / flight-operations datasets** (NASA and similar), not only toy synthetic traces. This note catalogs public sources and how they map into the analysis station.

---

## 1. NASA DASHlink — Sample Flight Data (primary)

**Best match for this tool.**

| Item | Detail |
|------|--------|
| **What** | De-identified flight-recorded data from one regional-jet type in commercial service (~3 years) |
| **Tails** | Anonymized IDs **652–687** (36 aircraft) |
| **Parameters** | **~186** engineering parameters per flight segment |
| **Format** | MATLAB `.mat` (one param / rate group per file); ~650 files per flight zip |
| **Size** | ~800 MB zip per flight set; full corpus is very large |
| **Rates** | ¼ Hz – 16 Hz (must resample / align for multi-param plots) |
| **Portal** | [DASHlink Sample Flight Data](https://c3.ndc.nasa.gov/dashlink/projects/85/) |
| **data.nasa.gov** | e.g. [Flight Data For Tail 684](https://data.nasa.gov/dataset/flight-data-for-tail-684) |
| **Processing scripts** | [alacer/flightdata](https://github.com/alacer/flightdata) (MATLAB → CSV / RData) |
| **FAQ** | [DASHlink FAQ](https://c3.ndc.nasa.gov/dashlink/resources/901) |

### Parameter families (examples from real param lists)

- **Performance / nav:** BARO CORRECT ALTITUDE, COMPUTED AIRSPEED, VERTICAL SPEED, LAT/LON (where present)
- **Attitude:** PITCH ANGLE, ROLL ANGLE, TRUE HEADING, ANGLE OF ATTACK, VERTICAL ACCELERATION
- **Controls:** AILERON L/R, ELEVATOR, RUDDER, T.E. FLAP POSITION
- **Propulsion:** CORE SPEED AVG (throttle proxy), engine serials, TAT
- **Hydraulics / warnings:** LOW HYDRAULIC PRESSURE GREEN/YELLOW, APU FIRE WARNING
- **Approach:** GLIDESLOPE DEVIATION, LOCALIZER DEVIATION, SELECTED HEADING/COURSE
- **Environment:** WIND SPEED, WIND DIRECTION, TOTAL PRESSURE

### Curated anomaly subset (lighter)

[Curated 4-Class Anomaly Detection Data Set](https://c3.ndc.nasa.gov/dashlink/resources/1018):

- ~99k approach windows × **160 s** × **20 variables**
- Classes: Nominal, Speed High, Path High, Flaps Late Setting
- Docs: [parameter PDF](https://c3.ndc.nasa.gov/dashlink/static/media/dataset/DASHlink_full_data_documentation.pdf)
- Files: `.npz` (~1.6 GB) + meta CSV — still large, but structured for ML / approach demos

---

## 2. What ships in this repo today

| Asset | Role |
|-------|------|
| `sample-data/generate_sample_flight_data.py` | Full synthetic generator (continuous + discrete) |
| `frontend/src/lib/demoData.js` | **DASHlink-inspired** procedural sample for Vercel (richer param set) |
| `Dashlink-data` | Design notes on structures for .mat → pandas |
| Analysis station param groups | Aligned to DASHlink families (perf / attitude / controls / propulsion / discretes) |

**Why not embed a real DASHlink flight?**  
A single flight zip is ~800 MB of MATLAB; GitHub/Vercel cannot host that. The demo generator approximates parameter *types* and correlations so the UI (slides, time snippets, significant events) is exercisable offline. Real ingestion path: download a tail zip → convert with scipy/R scripts → Parquet → register via backend.

---

## 3. Recommended integration path

1. **Demo (now):** procedural DASHlink-inspired sample in the browser.  
2. **Local / lab:**  
   - Download one Tail_6xx_N.zip from DASHlink / data.nasa.gov  
   - Convert selected `.mat` params → aligned CSV/Parquet (`scipy.io.loadmat` + pandas resample)  
   - Point backend file registration at that path  
3. **Anomaly demo:** subset of the 20-variable approach windows for “significant event” capture training.  
4. **Production:** schema registry mapping DASHlink short names → analysis station groups; multi-rate alignment service.

---

## 4. Other public sources (secondary)

| Source | Notes |
|--------|--------|
| NASA CRM / wind-tunnel | Force/moment, geometry — not FOQA-style time series |
| ADS-B open feeds | Position/speed only — good for map demos, thin for subsystem analysis |
| FOQA research papers | Often cite DASHlink; raw airline FOQA is not public |

---

## 5. Attribution

NASA DASHlink Sample Flight Data is provided for research and data-mining evaluation. Use is subject to NASA / DASHlink terms on the portal. Cite Bryan Matthews / NASA Ames when publishing results based on the data.
