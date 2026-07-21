# Agent Workflow: OpenSpec + Gherkin + Beads

Follow this order unless the user explicitly requests otherwise.

## 1. Specification (OpenSpec)

- Add or change behavior under `openspec/changes/<change-id>/`:
  - `proposal.md` — why + what (include Non-goals)
  - `design.md` — architecture decisions
  - `specs/<capability>/spec.md` — `## ADDED Requirements` with **SHALL** and Gherkin scenarios
  - `tasks.md` — phased checkbox steps
  - `verification.md` — scenario → test traceability
- Mirror scenarios in `features/*.feature`
- Validate when CLI is available: `npx @fission-ai/openspec validate <change-id> --strict`

## 2. Task tracking (Beads)

- Create beads from change tasks; link specs with `--spec-id openspec/specs/<capability>/spec.md`
- Work with `bd ready`, `bd update <id> --status in_progress`, `bd close <id>`

## 3. Implementation

- One bead at a time; keep backend + frontend in sync with spec scenarios

## 4. Validation

- `PYTHONPATH="$PWD" backend/.venv/bin/python -m pytest backend/tests/ -q`
- `(cd frontend && npm run build)`
- Refresh screenshots in `screenshots/` when UI changes (see `BEADS.md`)

## 5. Archiving

- Merge change deltas into `openspec/specs/<capability>/spec.md`

## Living specs

| Capability | Spec |
|------------|------|
| Index | `openspec/specs/README.md` |
| Flight test data | `openspec/specs/flight-test-data/spec.md` |
