# refactored-octo-spork

Parquet-native flight test analysis: events dashboard + full-screen D3 analysis station (map overview, multi-panel plots, significant-event capture).
Stack: Svelte 5 + Vite + D3 + Leaflet (frontend) · FastAPI + pandas/pyarrow + SQLite (backend) · Vercel demo (`VITE_DEMO_MODE`).
Posture: ponytail (repo >30 days). Shared health pack: `.cursor/skills/` + `.cursor/rules/`.

## Commands

- Backend venv + deps: `(cd backend && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt "pandas<3")`
- Backend run: `PYTHONPATH="$PWD" backend/.venv/bin/python -m uvicorn backend.main:app --reload`
- Backend tests: `PYTHONPATH="$PWD" backend/.venv/bin/python -m pytest backend/tests/ -q`
- Frontend install: `(cd frontend && npm ci)`
- Frontend dev: `(cd frontend && npm run dev)`
- Frontend build: `(cd frontend && npm run build)`
- Sample data: `python sample-data/generate_sample_flight_data.py`
- Screenshot / workflow: `(cd frontend && npm run build && npm run preview -- --port 4199) &` then `UI_URL=http://localhost:4199 node scripts/capture-screenshots.mjs`
- Secrets: `bash scripts/scan-secrets.sh .`
- Demo (live): https://refactored-octo-spork-eosin.vercel.app — Analyze on demo event
- Beads: `bd ready` · `bd create "Title" --type task --priority 2` · `bd close <id>` · `bd prime`

## Hard prohibitions

- Do not commit private keys, `*-key.pem`, `*.key`, `.env` secrets, or `BEGIN … PRIVATE KEY`. Generate locally; gitignore keys. Public certs OK.
- Do not enable data import on the Vercel demo path (`VITE_DEMO_MODE=true` keeps import disabled). Full-stack import is local/backend only.
- Do not invent routes, env vars, or scripts missing from this tree. Prefer README / OpenSpec / existing scripts.
- Do not rewrite OpenSpec / Gherkin / Beads for aspirational behavior. Update them only after code matches.
- Keep `PYTHONPATH="$PWD"` for backend tests from repo root; pin `pandas<3` for frequency compatibility.

## Verify by change type

| Change | Check |
| --- | --- |
| UI / Svelte (dashboard, AnalysisStation, plot builder) | `npm run dev` or build + preview; exercise Analyze → map → plots → capture |
| API / FastAPI | `pytest backend/tests/ -q` and/or curl touched `/events` or `/files/.../data` |
| Spec | Matching `features/*.feature` + `openspec/specs/` or change under `openspec/changes/` still true |
| Deploy | Live URL HTTP 200; primary flow Analyze on demo event |
| Secrets | `bash scripts/scan-secrets.sh .` passes |

## Source of truth

- Behavior: `openspec/specs/flight-test-data/`, change specs under `openspec/changes/`
- Gherkin: `features/flight-test-data.feature`, `features/analysis-station.feature`
- Remaining work: Beads (`bd list`) / GitHub issues
- Demo evidence: `screenshots/`, README verification section, live Vercel URL
- Health bar: `.cursor/rules/repo-health.mdc` — do not duplicate SUCCESS_CRITERIA here

## House vocabulary

- **Analysis station** — full-screen debrief UI (`AnalysisStation.svelte`), not a modal.
- **Slide** — named saved plot (or map) configuration; supports multiple time-aligned **panels**.
- **Snippet** — flight-time window (start HH:MM:SS + duration or end), not abstract 0–1 fractions.
- **Significant / anomalous event** — analyst-captured finding with severity + summary; recall restores plot config; markers on overview map.
- **Demo mode** — frontend-only procedural sample (`demoData.js`); import disabled.

## Borrowed patterns

- Hard prohibitions + secrets gate (portfolio health template / ossrules hard-prohibition style)
- Verification by change type (ossrules verification-matrix)
- Single source of truth pointers to OpenSpec / Gherkin / Beads (ossrules single-source)
- House vocabulary for station / slide / snippet / significant event (ossrules house-vocabulary)
