# Tasks – Flight Test Analysis Workspace

## Validated / In Progress
- [x] Expand sample data generator with throttle, engine, pumps, gear, hydraulics (#13)
- [x] Create GitHub issue #12 for the workspace
- [x] OpenSpec change skeleton (this folder)

## Next (prototype slice)
- [ ] `FlightAnalysisWorkspace.svelte` shell with shared time domain
- [ ] Performance + Attitude continuous panels (linked brush)
- [ ] Propulsion panel
- [ ] Discrete subsystem digital timeline
- [ ] Map / track panel (lat/lon colored by altitude)
- [ ] Demo mode loads expanded sample and renders all panels
- [ ] Vertical time cursor across panels

## Production rebuild beads (later)
- Replace sim data with real telemetry pipeline + schema registry
- Proper map tile provider + offline capability
- Exceedance / limit checking engine
- Multi-event / multi-file comparison
- Export (PDF / CSV of selected window)
- Auth and audit trail for analysis sessions
