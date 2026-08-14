# Spec: Flight Test Analysis Workspace

## Requirement: Time-aligned multi-panel analysis

The system SHALL provide a flight-test analysis workspace where continuous and discrete parameters share a common time domain so engineers can correlate events.

### Scenario: Load expanded sample and open workspace
- **GIVEN** the expanded sample telemetry (performance + propulsion + discrete states)
- **WHEN** the user opens the analysis workspace in demo mode
- **THEN** the workspace renders a map track and at least three time-aligned panels
- **AND** continuous panels show altitude/airspeed/throttle (or equivalent)
- **AND** a discrete panel shows landing gear and pump states as step traces

### Scenario: Linked brush / zoom
- **GIVEN** the analysis workspace is open with data loaded
- **WHEN** the user brushes a time range on one continuous panel
- **THEN** all other continuous and discrete panels update to the same time range
- **AND** the map highlights the corresponding track segment

### Scenario: Discrete subsystem states
- **GIVEN** discrete columns (`landing_gear`, `fuel_pump_on`, `oil_pump_on`, `hyd_system_ok`)
- **WHEN** the subsystem panel renders
- **THEN** states appear as digital/step traces (not continuous lines)
- **AND** gear transition periods are visually distinct from up/down

### Scenario: Shared time cursor
- **GIVEN** the workspace is open
- **WHEN** the user moves the mouse over any panel
- **THEN** a vertical cursor appears at the same time on every panel
- **AND** the map shows the aircraft position for that timestamp
