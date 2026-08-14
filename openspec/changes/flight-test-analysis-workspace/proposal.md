# Proposal: Flight Test Analysis Workspace

## Why
The current single multi-line D3 plot is insufficient for real flight-test analysis. Engineers need:
- A geographic track (map)
- Time-aligned continuous panels (performance, attitude, propulsion)
- Discrete/digital subsystem state timelines (gear, pumps, hydraulics)
- Linked brush/zoom and a shared time cursor for correlation

## Scope (this change)
- Expand sample telemetry with engine + subsystem parameters
- New multi-panel analysis workspace component (time-aligned)
- Map panel showing aircraft track colored by altitude or speed
- Discrete state rendering (step/digital traces)
- Demo-mode support so the workspace works without a backend

## Out of Scope (future beads)
- Real map tiles / offline maps
- Limit checking / exceedance detection
- Multi-file comparison / overlay
- Export of analysis views
- Auth / multi-user collaboration
