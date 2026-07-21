# Task Beads — Flight Test Data Management

See `.beads/` / `bd list` for the issue database.

## Shipped on main

- **Phase 1:** Event CRUD, file registration, Parquet processing, D3 plot modal, sample data generator
- **OpenSpec:** `openspec/specs/flight-test-data/spec.md` + `features/flight-test-data.feature`
- **Docs:** `docs/architecture.md`, README diagrams, `screenshots/`

## Docs hygiene

Screenshots in `screenshots/` should reflect the current UI. After UI landings:

```bash
# Terminal 1 — API on :8000
PYTHONPATH="$PWD" backend/.venv/bin/python -m uvicorn backend.main:app --reload

# Terminal 2 — Vite on :5173
cd frontend && npm run dev

# Capture manually or via scripts/capture-screenshots.mjs (set API_URL / VITE_API_URL if not on :8000)
VITE_API_URL=http://127.0.0.1:8020 node scripts/capture-screenshots.mjs
```

Update README and `openspec/specs/README.md` when capabilities change.

## Roadmap beads

Run `bd ready` for unblocked work. Roadmap items align with GitHub issues #3–#8 and `DEVELOPMENT_PLAN.md` Phase 2–4.
