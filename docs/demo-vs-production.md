# Demo vs production workflow

| Aspect | Production (local / full stack) | Vercel demo |
|--------|----------------------------------|-------------|
| Build | `(cd frontend && npm run build)` | `VITE_DEMO_MODE=true npm run build` via `vercel.json` |
| Backend | FastAPI on `:8000` — events, file registration, Parquet cache | None (static SPA only) |
| Events | Loaded from `GET /events/` | Embedded `demoEvents` in `FlightDashboard.svelte` |
| Plot data | `GET /files/{id}/data` from processed Parquet | Embedded `demoSampleData.json` (500 rows) |
| Add event / file | Enabled | Disabled with demo banner + alerts |
| Plot UI | Same D3 component (`FlightDataPlot.svelte`) | Same component via `initialData` |

Production sequence (see README architecture diagram):

1. Register file path → `POST /events/{id}/files/`
2. Background processing → Parquet cache
3. Plot → `GET /files/{id}/data` → D3 render

Demo sequence:

1. Static events table on load
2. Plot Data / Open D3 Plot → `initialData` from bundled JSON
3. No API calls required

## Verification checklist

- [ ] `pytest backend/tests/ -q` passes (production API)
- [ ] `(cd frontend && npm run build)` passes (production build)
- [ ] `(cd frontend && VITE_DEMO_MODE=true npm run build)` passes (demo build)
- [ ] Demo deploy shows events table, banner, and working D3 plot
- [ ] Local stack shows API-backed events and real Parquet plots

## GitHub issues alignment

| Issue | Demo | Production |
|-------|------|------------|
| #3 multipart upload | N/A (disabled) | Open |
| #4 Plot Data file ID | Uses embedded data | Fixed — uses `event.files[0].id` |
| #5 plot enhancements | Same UI | Open |
| #6 directory scanner | N/A | Open |
| #7 .mat support | N/A | Open |
| #8 multi-file UI | Partial (2 demo events) | Open |
