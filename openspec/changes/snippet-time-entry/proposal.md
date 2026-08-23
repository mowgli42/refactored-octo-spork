# Proposal: Time-Based Snippet Entry

## Why

The plot builder's time snippet was two abstract 0–1 fraction sliders. Flight test
analysts think in timestamps and offsets ("30 seconds starting at 14:31:00"), not
percentages of the recording.

## Scope (this change)

- Replace fraction sliders with a **start time entry** (HH:MM:SS, UTC)
- Snippet end defined either by a **duration offset** (secs or mins from start)
  or by an **explicit end time entry** — analyst-selectable mode toggle
- **Draggable start (▶) and end (◀) markers on the timeline** as a direct
  alternative to typed entry; entries and markers stay in sync
- "Full flight" reset and a live window summary (start–end · seconds)
- Capture modal and slides now describe windows in times, not percentages

## Out of Scope

- Snapping markers to detected discrete transitions
- Multiple simultaneous snippets / comparison windows
