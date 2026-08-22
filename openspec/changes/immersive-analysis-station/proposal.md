# Proposal: Immersive Analysis Station

## Why

The modal analysis workspace kept engineers inside the events dashboard. Debrief-style
analysis (o-my-debrief layout) needs a dedicated full-screen station where the analyst
can build plots, step through time, and record findings without leaving the data.

## Scope (this change — implemented on main)

- Replace the modal workspace with a full-screen `AnalysisStation.svelte`
  (dark themed, fixed-viewport layout; dashboard becomes an event selector)
- Cinematic loading sequence: event → associated data products → time index → ready
- Interactive D3 plot builder: grouped parameter chips (Performance, Attitude,
  Propulsion, Subsystems), plot formats (multi-line, step/digital, area),
  time-snippet range selection
- Analysis slides: named, saved plot configurations the analyst can switch between
  and extend with "+ New slide"
- Significant / anomalous event capture: severity (note / anomaly / critical) +
  summary, saved with the exact plot configuration and time window for recall
- Timeline scrub bar with play/pause and live aircraft-state readout
  (altitude, airspeed, throttle, RPM, gear, pumps, hydraulics, master caution)

## Out of Scope (future beads)

- Persistence of slides / captured events beyond the browser session
- Export of slides or captured events (PDF / CSV / share link)
- Backend-served telemetry in the station (demo uses procedural sample)
- Keyboard interaction for timeline slider; ARIA roles on modal backdrop
