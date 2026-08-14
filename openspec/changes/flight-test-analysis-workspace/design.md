# Design: Flight Test Analysis Workspace

## Panel Layout (shared time domain)

```
┌─────────────────────────────────────────────────────────┐
│  Map (lat/lon track + current position)                 │
├─────────────────────────────────────────────────────────┤
│  Performance: altitude | airspeed | vertical speed      │  ← continuous
├─────────────────────────────────────────────────────────┤
│  Attitude: pitch | roll | AoA                           │  ← continuous
├─────────────────────────────────────────────────────────┤
│  Propulsion: throttle | RPM | fuel flow                 │  ← continuous
├─────────────────────────────────────────────────────────┤
│  Subsystems (digital): gear | fuel pump | oil | hyd     │  ← discrete
└─────────────────────────────────────────────────────────┘
         ◄──────── shared brush / zoom / time cursor ────────►
```

## Decisions

| Choice | Alternative considered | Reason (prototype) |
|--------|------------------------|--------------------|
| D3 multi-panel with shared x-scale | Plotly / Observable Plot | Already in stack; full control over brush linking |
| Discrete as step/digital traces | Overlay as continuous lines | Correct visual semantics for on/off & gear states |
| Simple D3 geo or Leaflet for map | Full Mapbox | Keep demo lightweight; Leaflet is acceptable if needed |
| Expand sample generator first | Wait for real data | Unblocks all panels immediately; demo-ready |

## Time synchronization
- One shared `xScale` (time) owned by the workspace
- Brush events on any continuous panel update the shared domain
- Vertical cursor (mousemove) broadcasts current time to all panels + map

## Data model
- Same Parquet / JSON records as today
- Continuous columns: numeric
- Discrete columns: integer codes (documented in sample generator)
- `landing_gear`: 0=up, 1=transition, 2=down
