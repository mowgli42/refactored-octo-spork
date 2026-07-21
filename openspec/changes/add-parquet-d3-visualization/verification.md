# Verification: Parquet + D3

| Scenario | Evidence |
|----------|----------|
| Create and list events | `test_create_event`, `test_read_events` |
| Register and process Parquet telemetry | `test_file_registration_and_processing` (Parquet path, 8000 rows) |
| Serve plot data with downsampling | same test — GET `/files/{id}/data?limit=100` |
| Interactive D3 plot rendering | Manual / screenshot; frontend build succeeds |
| Generate sample flight telemetry | `sample-data/generate_sample_flight_data.py` |

Commands:

```bash
PYTHONPATH="$PWD" backend/.venv/bin/python -m pytest backend/tests/ -q
(cd frontend && npm run build)
```
