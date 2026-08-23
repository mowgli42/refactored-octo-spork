# Tasks – Multiple Time-Aligned Panels per Slide

## Implemented

- [x] Slide model: `panels: [{ id, params, format }]` replaces single params/format
- [x] Stacked panel rendering with shared snippet window and scrub cursor;
      time-axis labels only on the bottom panel
- [x] "Editing" panel selector; chips edit the active panel
- [x] "+ Add panel" (defaults to a master-caution step panel) and per-panel
      remove with a one-panel minimum
- [x] Pre-built "Subsystem drop-outs" slide (discretes step + telemetry line)
- [x] Capture / recall of significant events stores the full panel stack
- [x] Slide and event metadata show panel + series counts
- [x] Clean y-axis tick formatting (`~g`)
- [x] Step (digital) format renders each parameter in its own stacked lane with
      a colored in-lane label and lane separators (no overlapping 0/1 traces);
      constant-in-window series still get a visible band

## Verified

- [x] Production build succeeds
- [x] Workflow validator step 4 extended: 2-panel subsystem slide renders both
      plots, add/edit/remove third panel — all pass headless with zero console
      errors (local build and live Vercel)
