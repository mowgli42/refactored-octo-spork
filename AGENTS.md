# AGENTS.md - guide for AI coding agents

## Project context

refactored-octo-spork is a Dashlink flight data API with a Svelte frontend.
Read `README.md`, then inspect `backend/` or `frontend/` depending on the task.

## Local setup

Run from the repository root:

```bash
(cd backend && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt "pandas<3")
(cd frontend && npm ci)
```

## Smoke test

```bash
PYTHONPATH="$PWD" backend/.venv/bin/python -m pytest backend/tests/ -q
(cd frontend && npm run build)
```

## Agent notes

- Keep `PYTHONPATH="$PWD"` when running backend tests from the repo root.
- `pandas<3` avoids the current uppercase frequency compatibility breakage in tests.
- Preserve existing local user changes; stage only files you intentionally modify.
