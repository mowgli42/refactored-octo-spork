# Tasks – Time-Based Snippet Entry

## Implemented

- [x] Start time entry (HH:MM:SS) with validation and clamp to flight range
- [x] Duration mode: numeric offset + sec/min unit; end = start + offset
- [x] End-time mode: explicit HH:MM:SS entry, clamped after start
- [x] Draggable ▶ start / ◀ end markers on the timeline (pointer events)
- [x] "Full flight" reset + live snippet summary (start–end · seconds)
- [x] Capture modal shows the time window instead of percentages
- [x] Slides / captured events unchanged internally (still store fractions)

## Verified

- [x] Production build succeeds
- [x] `scripts/capture-screenshots.mjs` step 4 extended: start entry + 30 s
      duration, minute units, explicit end time, and end-marker drag — all pass
      headless with zero console errors
