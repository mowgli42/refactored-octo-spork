# Tasks: Parquet + D3 visualization

## Phase 1 — Backend (done)

- [x] Parquet write path in `processing.py`
- [x] Legacy H5 read in `get_data_frame`
- [x] GET `/files/{id}/data` with column filter and downsampling
- [x] pytest coverage for Parquet cache and data API

## Phase 2 — Frontend (done)

- [x] Add D3 dependency and `FlightDataPlot.svelte`
- [x] Plot modal in `FlightDashboard.svelte`
- [x] `npm run build` passes

## Phase 3 — Spec + docs (done)

- [x] OpenSpec living spec + Gherkin feature
- [x] `docs/architecture.md` and `screenshots/`
- [x] Sample data generator script
- [x] Beads roadmap for Phase 2–4

## Phase 4 — Follow-ups (open)

- [ ] Multipart file upload (GitHub #3)
- [ ] Watched directory scanner
- [ ] Vercel demo mode (`DEMO_MODE` mock data)
- [ ] MATLAB `.mat` parser
- [ ] Plot export and limit checking
