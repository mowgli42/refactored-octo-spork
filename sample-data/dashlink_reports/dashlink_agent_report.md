# DASHlink agent test report

- Started: `2026-08-24T00:03:52.691068+00:00`
- Finished: `2026-08-24T00:03:57.884253+00:00`
- **Passed: True**

## Steps

- **PASS** `download:parameters.txt` — `{"ok": true, "bytes": 22065}`
- **PASS** `download:DASHlink_full_data_documentation.pdf` — `{"ok": true, "bytes": 435573}`
- **PASS** `create_fixture` — `{"ok": true}`
- **PASS** `convert` — `{"ok": true}`
- **PASS** `verify` — `{"parquet_exists": true, "csv_exists": true, "rows": 200, "columns": ["timestamp", "altitude_ft", "airspeed_kt", "pitch_deg", "roll_deg", "core_speed_pct", "glideslope_dev_pct", "hyd_low_green"], "has_altitude": true, "has_core_speed": true, "hyd_events": 9, "ok": true}`
- **PASS** `param_catalog` — `{"ok": true, "entries": 190}`

## Notes

- Full Tail_652_*.zip files are ~800MB each; set `DASHLINK_FULL_ZIP=<url>` to exercise a real download.
- Fixture `.mat` validates conversion without NASA bandwidth.
- UI screenshots: run frontend with converted Parquet and capture (Playwright or manual).

## Outputs

- Raw assets: `sample-data/dashlink_raw`
- Fixture: `sample-data/dashlink_fixture`
- Converted: `sample-data/dashlink_converted`
