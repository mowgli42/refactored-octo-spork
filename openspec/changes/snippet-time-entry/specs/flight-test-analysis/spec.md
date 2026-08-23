# Spec Delta: Time-Based Snippet Entry

## MODIFIED Requirement: Interactive D3 plot builder (time snippet)

The plotted time snippet SHALL be defined in flight time, not abstract fractions:
a start time entry plus either a duration offset (seconds or minutes) or an
explicit end time, with equivalent draggable start/end markers on the timeline.

### Scenario: Start time plus duration offset
- **GIVEN** the analysis station is ready
- **WHEN** the analyst enters start time 14:31:00 and a duration of 30 seconds
- **THEN** the plot re-renders for 14:31:00–14:31:30
- **AND** changing the unit to minutes redisplays the same offset (0.5 min)

### Scenario: Explicit end time
- **GIVEN** a snippet starting at 14:31:00
- **WHEN** the analyst switches to End time mode and enters 14:31:50
- **THEN** the plot re-renders for 14:31:00–14:31:50
- **AND** an end time at or before the start is clamped to a minimum window

### Scenario: Timeline markers
- **GIVEN** a defined snippet
- **WHEN** the analyst drags the ▶ start or ◀ end marker on the timeline
- **THEN** the snippet window, time entries, and plot update live
- **AND** invalid text entries are rejected and the previous value restored

### Scenario: Full-flight reset
- **GIVEN** a narrowed snippet
- **WHEN** the analyst clicks "Full flight"
- **THEN** the snippet spans the entire recording
