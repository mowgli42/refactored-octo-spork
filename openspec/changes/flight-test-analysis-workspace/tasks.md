# Tasks – Flight Test Analysis Workspace

## Validated / Complete (prototype)
- [x] Expand sample data generator with throttle, engine, pumps, gear, hydraulics (#13)
- [x] Create GitHub issue #12 for the workspace
- [x] OpenSpec change skeleton
- [x] Procedural demo data generator (`frontend/src/lib/demoData.js`)
- [x] `FlightAnalysisWorkspace.svelte` — map + performance + attitude + propulsion + discrete panels
- [x] Shared time brush + vertical cursor
- [x] Demo dashboard with import disabled (Vercel-only slice)
- [x] README + vercel.json aligned to analysis demo

## Next polish
- [ ] Push live-deploy screenshots into `screenshots/`
- [ ] Independent Y-axes with dual labels for mixed units
- [ ] Cursor value readout tooltip across panels
- [ ] Gear state labels (Up / Transition / Down) on discrete panel

## Production rebuild beads (later)
- Replace sim data with real telemetry pipeline + schema registry
- Proper map tile provider + offline capability
- Exceedance / limit checking engine
- Multi-event / multi-file comparison
- Export (PDF / CSV of selected window)
- Auth and audit trail for analysis sessions
