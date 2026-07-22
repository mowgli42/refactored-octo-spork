# Design: Parquet + D3

## Decisions

1. **Parquet as canonical cache** — pyarrow Snappy compression; UUID filenames under `backend/cache/`.
2. **Mock fallback** — non-local URLs or missing files generate realistic 8000-row telemetry so demos work without S3.
3. **API downsampling** — stride-based decimation in `/files/{id}/data` to keep payloads under ~3000 rows.
4. **D3 in modal** — `FlightDataPlot.svelte` fetches on mount; parent passes `fileId` from dashboard row actions.

## Risks

- `pandas>=3` breaks test frequency usage — pin `pandas<3` in dev docs until upgraded.
- CORS wide open for dev — restrict in production deploys.
