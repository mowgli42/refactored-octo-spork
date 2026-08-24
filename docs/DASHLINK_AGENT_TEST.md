# DASHlink extended agent test

Validates the path from **NASA DASHlink assets → MATLAB conversion → aligned Parquet/CSV → schema checks**.

## Quick run

```bash
# deps: pandas, numpy, scipy, pyarrow
pip install pandas numpy scipy pyarrow

python scripts/run_dashlink_agent_test.py
# exit 0 + report under sample-data/dashlink_reports/

# pytest-only path (fixture, no network required if fixture already present)
python scripts/create_dashlink_fixture.py
python scripts/convert_dashlink.py --mat sample-data/dashlink_fixture/652201003041921.mat --out-dir sample-data/dashlink_converted
pytest scripts/test_dashlink_workflow.py -q
```

## What the agent does

| Step | Action |
|------|--------|
| 1 | Download official DASHlink `parameters.txt` (~190 entries) |
| 2 | Download anomaly dataset documentation PDF |
| 3 | Create synthetic Tail-652-style `.mat` fixture (offline-safe) |
| 4 | Convert multi-rate arrays → aligned 2 Hz CSV + Parquet |
| 5 | Verify columns (`altitude_ft`, `core_speed_pct`, …) and hyd discrete events |

## Optional full flight zip

```bash
export DASHLINK_FULL_ZIP='https://…/Tail_652_1.zip'  # ~800 MB
python scripts/run_dashlink_agent_test.py
```

Then unzip and point `convert_dashlink.py --mat-dir` at extracted `.mat` files.

## Screenshots

Concept captures of the analysis station with DASHlink-style series and the agent report UI live under `docs/screenshots/` once committed from a local capture pass.

See also: [DATASETS.md](./DATASETS.md).
