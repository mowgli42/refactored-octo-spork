# Proposal: Multiple Time-Aligned Panels per Slide

## Why

Data analysis frequently needs several plots of different data at once: when a
master caution asserts or a subsystem goes offline, the analyst must see the
discrete drop-out and the corresponding instrumentation telemetry of that
subsystem on the same time base. A single overlay plot mixes digital and
continuous traces illegibly.

## Scope (this change)

- Plot slides become stacks of panels; each panel has its own parameter set and
  format (multi-line / step / area) while all panels share the slide's time
  snippet and the timeline scrub cursor
- "Editing" panel selector in the builder bar; parameter/format chips edit the
  active panel; "+ Add panel" and per-panel remove (minimum one panel)
- Pre-built "Subsystem drop-outs" slide: discretes (master caution, fuel/oil
  pumps, hydraulics) as step traces above the corresponding oil pressure, fuel
  flow, and RPM telemetry
- Significant/anomalous event capture stores and recalls the full panel stack
- Only the bottom panel draws time-axis labels; panels stay time-aligned

## Out of Scope

- Per-panel independent time windows
- Cross-panel hover tooltip readout
- Drag-to-reorder panels
