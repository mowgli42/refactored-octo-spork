# Flight Test Data Management — Project Context

## Purpose

Parquet-native flight test data platform for aerospace teams: track flight test events, register telemetry paths (Parquet/CSV/HDF5), process into a columnar cache, and explore aircraft performance with interactive D3.js plots.

## Tech Stack

- **Backend:** FastAPI, SQLAlchemy, SQLite metadata, pandas + pyarrow (Parquet cache)
- **Frontend:** Svelte 5, Vite, D3 v7
- **Tests:** pytest (`backend/tests/`)
- **OpenSpec:** living specs in `openspec/specs/`
- **Gherkin:** mirrored scenarios in `features/`
- **Beads:** task tracking (`.beads/`, prefix `refactored-octo-spork`)

## Conventions

- Run backend tests from repo root: `PYTHONPATH="$PWD" backend/.venv/bin/python -m pytest backend/tests/ -q`
- Pin `pandas<3` for test compatibility (see `AGENTS.md`)
- Processed telemetry always caches as Parquet under `backend/cache/`
- Roadmap items tracked in Beads and aligned with GitHub issues #3–#8

## Phase map

| Phase | Focus | Status |
|-------|-------|--------|
| 1 | Events CRUD, file registration, Parquet processing, D3 plot | Shipped |
| 2 | File upload, directory scanner, async parsing | Planned |
| 3 | Analysis, limits, reports | Planned |
| 4 | Auth, search, export APIs | Planned |

See `DEVELOPMENT_PLAN.md` and `bd list` for current beads.
